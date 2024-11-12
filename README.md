# PrinterWebSocket.js with Python Server

This project is a WebSocket server in Python along with a vanilla JS client that allows clients to interact with networked printers via WebSocket messages from web applications. It enables clients to list available printers, check printer statuses, and send print jobs directly. The server includes a GUI to monitor connected clients and server activity. 
I started this project to make a free alternative to JSPM and QZ Tray which allows web-based POS softwares to communicate with printers directly and allow silent printing without any promts to the user. I reversed engineered those, and this PrinterWebsocket work similarly like these aftermarket solutions. Still it's in development phase and I don't have access to a lot of printers that everyone uses. I worked with a Thermal POS printer, it worked well with TSPL printer Raw Commands using this client-server setup.


## Features

-   **List Available Printers**: Get a list of all printers connected to the server.
-   **Printer Status**: Query the status of a specific printer (e.g., Idle, Printing, Out of Paper, Error).
-   **Send Print Job**: Send raw TSPL commands to a specified Thermal printer or other printers.
-   **Real-Time Notifications**: Broadcast printer statuses and job completion details to connected clients.
-   **Client Management**: Monitor connected clients in real-time through the GUI.
- **Silent Printing**: This script allows silent printing, which means not to give the user any prompt to confirm the print. Silent Prinitng is suitable for automation and printer servers. 

## Project Structure

-   `printer_server.py` - Main server file with WebSocket and printer handling.
-   `requirements.txt` - Dependencies required to run the server.
-   `PrinterWebsocket.js` - Client js to communicate with the python server.

## Requirements

-   Python 3.x
-   `websockets` library for WebSocket communication
-   `pywin32` library for printer handling on Windows
-   `tkinter` library for the GUI (usually included with Python)

### Installing Dependencies

Install required libraries using `pip`:
`pip install websockets pywin32` 

## Running the Server

 **Start the Server**: 
1. Run `printer_server.py` to start the WebSocket server.   
    `python printer_server.py` 
    
3.  **GUI**: The server includes a GUI with real-time logging and a list of connected clients. The GUI displays:
    
    -   **Log Area**: Displays server activity, connection status, and error messages.
    -   **Connected Clients List**: Shows the list of clients connected to the server.


## WebSocket API

### Available WebSocket Messages

Clients can interact with the server by sending JSON-encoded messages using the websocket with specific fields.

### 1. Find Available Printers

| **Type**   | **Field**          | **Value / Example**                                                                                 |
|------------|---------------------|-----------------------------------------------------------------------------------------------------|
| Request    | `call`             | `"printers.find"`                                                                                   |
|            | `uid`              | `"unique-request-id"`                                                                               |
|            |                    |                                                                                                     |
| Response   | `uid`              | `"unique-request-id"`                                                                               |
|            | `result`           | `["Printer1", "Printer2", "Printer3"]`                                                              |
|            | `status_code`      | `0`                                                                                                 |


#### Example Request:
`{
    "call": "printers.find",
    "uid": "hHOIa02asXJ"
}` 

#### Example Response:
`{
    "uid": "hHOIa02asXJ",
    "result": ["Printer1", "Printer2", "Printer3"],
    "status_code": 0
}` 


### 2. Get Server Version
| **Type**   | **Field**       | **Value / Example**                 |
|------------|-----------------|-------------------------------------|
| Request    | `call`          | `"server.version"`                 |
|            | `uid`           | `"unique-request-id"`              |
|            |                 |                                     |
| Response   | `uid`           | `"unique-request-id"`              |
|            | `result`        | `"0.1.0"`                          |
|            | `info`          | `"serverVersion"`                  |
|            | `status_code`   | `0`                                 |

#### Example Request:
`{
    "call": "server.version",
    "uid": "hHOIa02asXJ"
}` 

#### Example Response:
`{
    "uid": "hHOIa02asXJ",
    "result": "0.1.0",
    "info": "serverVersion",
    "status_code": 0
}` 

### 3. Send Print Job

| **Type**   | **Field**           | **Value / Example**                                                                                                          |
|------------|---------------------|-------------------------------------------------------------------------------------------------------------------------------|
| Request    | `call`              | `"print"`                                                                                                                     |
|            | `uid`               | `"unique-request-id"`                                                                                                         |
|            | `params`            |                                                                                                                               |
|            | `params.printer.name` | `"Gprinter GP-3120TUC"`                                                                                                     |
|            | `params.data`       | `["SIZE 100 mm, 150 mm", "GAP 3 mm, 0", "TEXT 100,100,\"TSS24.BF2\",0,1,1,\"Hello World\"", "PRINT 1,1"]`                    |
|            |                     |                                                                                                                               |
| Response   | `uid`               | `"unique-request-id"`                                                                                                         |
| (Success)  | `status`            | `"success"`                                                                                                                   |
|            | `message`           | `"Printed on Gprinter GP-3120TUC"`                                                                                            |
|            | `status_code`       | `0`                                                                                                                           |
|            |                     |                                                                                                                               |
| Response   | `uid`               | `"unique-request-id"`                                                                                                         |
| (Error)    | `status`            | `"error"`                                                                                                                     |
|            | `message`           | `"Invalid printer or TSPL data"`                                                                                              |
|            | `status_code`       | `3`                                                                                                                           |


#### Example Request in JSON:
`{
    "call": "print",
    "uid": "unique-request-id",
    "params": {
        "printer": {
            "name": "Gprinter GP-3120TUC"
        },
        "data": [
            "SIZE 100 mm, 150 mm",
            "GAP 3 mm, 0",
            "TEXT 100,100,\"TSS24.BF2\",0,1,1,\"Hello World\"",
            "PRINT 1,1"
        ]
    }
}` 

#### Example Response in JSON:

*On successful print job initiation:*
`{
    "uid": "unique-request-id",
    "status": "success",
    "message": "Printed on Gprinter GP-3120TUC",
    "status_code": 0
}` 

*If there’s an error with the printer or print data:*
`{
    "uid": "unique-request-id",
    "status": "error",
    "message": "Invalid printer or TSPL data",
    "status_code": 3
}` 


### 4. Query Printer Status (Still in Test)

This feature is still in test, might not work with your printer. There are limitations in pywin32 library that it can't get the printer status from the printer. It can create print jobs, the rest is handled by windows. 

To check the status of a specific printer.

#### Request:
`{
    "call": "printerStatus",
    "uid": "unique-request-id",
    "PrinterName": "Gprinter GP-3120TUC"
}` 

#### Response:

-   **Idle Printer**:
       `{
        "uid": "unique-request-id",
        "status": "Printer status retrieved",
        "PrinterName": "Gprinter GP-3120TUC",
        "status_code": 0
    }` 
    
-   **Printing**:
    `{
        "uid": "unique-request-id",
        "status": "Printer status retrieved",
        "PrinterName": "Gprinter GP-3120TUC",
        "status_code": 1
    }` 
    
-   **Error**:
    `{
        "uid": "unique-request-id",
        "status": "Printer status retrieved",
        "PrinterName": "Gprinter GP-3120TUC",
        "status_code": 3
    }` 
    

## Logging and Client Updates

-   **Logging**: All interactions, including errors, are logged in the GUI.
-   **Client Updates**: Broadcast messages to all connected clients in case of printer status updates or errors.


## Example Usage

You can use a WebSocket client, such as the WebSocket tool in the browser’s developer console or Postman, to connect to the server and send requests. Building POS software on web technologies will be easier to integrate with off-the-shelf thermal POS printers.

## Notes

-   This server is built for Windows environments, using `pywin32` to manage printer interactions.
-   Modify the `PRINTER_STATUS_CODES` dictionary as needed to align with your printer's status codes.