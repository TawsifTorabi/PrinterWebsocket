import asyncio
import websockets
import json
import win32print
import threading
import tkinter as tk
from tkinter import scrolledtext
import time

# Store connected clients
connected_clients = set()

# Mock printer status codes
PRINTER_STATUS_CODES = {
    "IDLE": 0,          # Printer is ready/idle
    "PRINTING": 1,      # Print job in progress
    "OUT_OF_PAPER": 2,  # Out of paper
    "ERROR": 3          # Printer error (general)
}

# Store the last known status of the printer to detect changes
last_printer_status = None

# Function to find available printers


def find_printers():
    printers = []
    for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS):
        printers.append(printer[2])
    return printers

# Function to simulate getting the printer's status


def get_printer_status(printer_name):
    # Simulated status. You could fetch real status based on your printer's capabilities
    return PRINTER_STATUS_CODES["IDLE"]

# Function to print RAW TSPL commands to the selected printer


def send_raw_tspl_to_printer(printer_name, tspl_data):
    printer_handle = win32print.OpenPrinter(printer_name)
    try:
        job_id = win32print.StartDocPrinter(
            printer_handle, 1, ("TSPL Print Job", None, "RAW"))
        win32print.StartPagePrinter(printer_handle)
        win32print.WritePrinter(printer_handle, tspl_data.encode('utf-8'))
        win32print.EndPagePrinter(printer_handle)
        win32print.EndDocPrinter(printer_handle)

        # Now poll for the job completion status
        return check_print_job_status(printer_handle, job_id)
    finally:
        win32print.ClosePrinter(printer_handle)


def check_print_job_status(printer_handle, job_id):
    completed = False
    while not completed:
        job_info = win32print.EnumJobs(printer_handle, 0, -1, 1)
        for job in job_info:
            if job["JobId"] == job_id:
                if job["Status"] == 0:  # Status 0 means the job is done or idle
                    return "completed"
                elif job["Status"] & win32print.JOB_STATUS_ERROR:
                    return "error"
                elif job["Status"] & win32print.JOB_STATUS_PRINTING:
                    log_message(f"Job {job_id} is printing...")
                elif job["Status"] & win32print.JOB_STATUS_PAUSED:
                    return "paused"
        time.sleep(1)

# Function to continuously check printer status and broadcast any changes


def poll_printer_status(printer_name, loop):
    global last_printer_status
    while True:
        # Get the current printer status
        current_status = get_printer_status(printer_name)

        # If the status has changed since the last check, broadcast to clients
        if current_status != last_printer_status:
            last_printer_status = current_status
            status_message = {
                "status": "Printer status changed",
                "status_code": current_status
            }
            # Schedule the status broadcast on the event loop
            asyncio.run_coroutine_threadsafe(
                broadcast_status_change(status_message), loop)

        # Sleep for a bit before polling again
        time.sleep(5)

# Function to broadcast printer status to all connected clients


async def broadcast_status_change(status_message):
    if connected_clients:
        message = json.dumps(status_message)
        clients_to_remove = set()
        for client in connected_clients:
            try:
                await client.send(message)
                log_message(f"Broadcast to {client.remote_address}: {message}")
            except Exception as e:
                log_message(
                    f"Error sending message to {client.remote_address}: {e}")
                clients_to_remove.add(client)

        # Remove any clients that failed
        for client in clients_to_remove:
            connected_clients.remove(client)

# WebSocket server handler


async def printer_server(websocket, path):
    # Add the new client
    connected_clients.add(websocket)
    log_message(f"Client connected: {websocket.remote_address}")
    update_client_list()

    try:
        async for message in websocket:
            log_message(f"Received from {websocket.remote_address}: {message}")
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                log_message(
                    f"Error decoding message from {websocket.remote_address}: {message}")
                continue

            # Handle printer search request
            if data.get('call') == 'printers.find':
                printers = find_printers()
                printer_status = PRINTER_STATUS_CODES["IDLE"]
                response = {
                    "uid": data.get('uid'),
                    "result": printers,
                    "status_code": printer_status
                }
                await send_response(websocket, response)

            # Handle server version request
            elif data.get('call') == 'server.version':
                printer_status = PRINTER_STATUS_CODES["IDLE"]
                response = {
                    "uid": data.get('uid'),
                    "result": "0.1.0",
                    "info": "serverVersion",
                    "status_code": printer_status
                }
                await send_response(websocket, response)

            # Handle print command
            elif data.get('call') == 'print':
                params = data.get('params', {})
                printer_name = params.get('printer', {}).get('name')
                tspl_data = "".join(params.get('data', []))

                if printer_name and tspl_data:
                    try:
                        printer_status = get_printer_status(printer_name)

                        notify_response = {
                            "uid": data.get('uid'),
                            "status": "Printing job started on " + printer_name,
                            "status_code": PRINTER_STATUS_CODES["PRINTING"]
                        }
                        await send_response(websocket, notify_response)

                        send_raw_tspl_to_printer(printer_name, tspl_data)

                        response = {
                            "uid": data.get('uid'),
                            "status": "success",
                            "message": f"Printed on {printer_name}",
                            "status_code": PRINTER_STATUS_CODES["IDLE"]
                        }
                    except Exception as e:
                        response = {
                            "uid": data.get('uid'),
                            "status": "error",
                            "message": str(e),
                            "status_code": PRINTER_STATUS_CODES["ERROR"]
                        }
                else:
                    response = {
                        "uid": data.get('uid'),
                        "status": "error",
                        "message": "Invalid printer or TSPL data",
                        "status_code": PRINTER_STATUS_CODES["ERROR"]
                    }

                await send_response(websocket, response)

            # Handle printer status request
            elif data.get('call') == 'printerStatus':
                # Get the printer name and uid from the message
                printer_name = data.get('PrinterName')
                uid = data.get('uid')

                if printer_name:
                    try:
                        # Get the current status of the specified printer
                        printer_status = get_printer_status(printer_name)

                        # Prepare the response with the printer status
                        response = {
                            "uid": uid,
                            "status": "Printer status retrieved",
                            "PrinterName": printer_name,
                            "status_code": printer_status
                        }
                    except Exception as e:
                        response = {
                            "uid": uid,
                            "status": "error",
                            "message": str(e),
                            "PrinterName": printer_name,
                            "status_code": PRINTER_STATUS_CODES["ERROR"]
                        }
                else:
                    # Invalid request if printer name is not provided
                    response = {
                        "uid": uid,
                        "status": "error",
                        "message": "PrinterName not provided",
                        "status_code": PRINTER_STATUS_CODES["ERROR"]
                    }

                # Send the response with the printer status
                await send_response(websocket, response)

    finally:
        connected_clients.remove(websocket)
        log_message(f"Client disconnected: {websocket.remote_address}")
        update_client_list()


# Function to safely send a response to a WebSocket client
async def send_response(websocket, response):
    try:
        await websocket.send(json.dumps(response))
        log_message(
            f"Sent to {websocket.remote_address}: {json.dumps(response)}")
    except Exception as e:
        log_message(
            f"Failed to send message to {websocket.remote_address}: {str(e)}")

# Function to log messages in the GUI


def log_message(message):
    log_area.configure(state=tk.NORMAL)  # Enable editing
    log_area.insert(tk.END, message + '\n')  # Add message to log
    log_area.configure(state=tk.DISABLED)  # Disable editing
    log_area.yview(tk.END)  # Scroll to the end

# Update the client list in the GUI


def update_client_list():
    client_listbox.delete(0, tk.END)  # Clear the listbox
    for client in connected_clients:
        client_listbox.insert(tk.END, str(client.remote_address))

# Start the WebSocket server


def start_server(loop):
    async def main():
        async with websockets.serve(printer_server, "localhost", 8765):
            log_message(
                "Printer WebSocket server running on ws://localhost:8765")
            await asyncio.Future()  # Run forever

    # Start polling the printer status in a separate thread
    start_status_polling_thread("Your Printer Name", loop)

    asyncio.run(main())

# Wrapper to start polling in a separate thread


def start_status_polling_thread(printer_name, loop):
    polling_thread = threading.Thread(
        target=poll_printer_status, args=(printer_name, loop), daemon=True)
    polling_thread.start()

# Wrapper for starting the server in a thread


def start_server_thread(loop):
    server_thread = threading.Thread(
        target=start_server, args=(loop,), daemon=True)
    server_thread.start()

# Start the GUI in the main thread


def start_gui():
    global log_area, client_listbox
    root = tk.Tk()
    root.title("Printer WebSocket Server")

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)

    log_label = tk.Label(frame, text="Server Log")
    log_label.pack()

    log_area = scrolledtext.ScrolledText(frame, height=10, state=tk.DISABLED)
    log_area.pack()

    client_list_label = tk.Label(frame, text="Connected Clients")
    client_list_label.pack()

    client_listbox = tk.Listbox(frame, height=5)
    client_listbox.pack()

    root.geometry("500x400")
    root.mainloop()


if __name__ == "__main__":
    # Create a new event loop for the WebSocket server
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Start the server and GUI in parallel
    start_server_thread(loop)
    start_gui()
