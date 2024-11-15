# PrinterWebSocket.js with Python Server

This project is a WebSocket server in Python along with a vanilla JS client that allows clients to interact with networked printers via WebSocket messages from web applications. It enables clients to list available printers, check printer statuses, and send print jobs directly. The server includes a GUI to monitor connected clients and server activity. 
I started this project to make a free alternative to JSPM and QZ Tray which allows web-based POS software to communicate with printers directly and allow silent printing without any prompts to the user. I reversed-engineered those, and this PrinterWebsocket works similarly to these aftermarket solutions. Still, it's in the development phase and I don't have access to a lot of printers that everyone uses. I worked with a Thermal POS printer, it worked well with TSPL printer Raw Commands using this client-server setup.

![Framework Diagram](https://blogger.googleusercontent.com/img/a/AVvXsEiyxS9FRJCVf2LswRgUjXbXRbXlaeU3TeSjYGdDPAs8LU6eRUN1owLq9rscS2kzeE8LvfuveQf03ZbZb38Hs6j5O-2AZam9X9isz5OS9M6uJaQpPRtssfGwiMVznLZ-XAfGttp3sUvD8dagG2F1XM7D9rHtPbogrhShjuXNuh1t9rgg2RJEYGh-peqqaFUm=s16000)

## Features

-   **List Available Printers**: Get a list of all printers connected to the server.
-   **Printer Status**: Query the status of a specific printer (e.g., Idle, Printing, Out of Paper, Error).
-   **Send Print Job**: Send raw TSPL commands to a specified Thermal printer or other printers.
-   **Real-Time Notifications**: Broadcast printer statuses and job completion details to connected clients.
-   **Client Management**: Monitor connected clients in real-time through the GUI.
- **Silent Printing**: This script allows silent printing, which means not giving the user any prompt to confirm the print. Silent printing is suitable for automation and printer servers. 

## Project Structure

-   `printer_server.py` - Main server file with WebSocket and printer handling.
-   `requirements.txt` - Dependencies required to run the server.
-   `PrinterWebsocket.js` - Client js to communicate with the Python server.

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


## Start with the script 

 1. ###  Include the JavaScript File
 Before starting, we have to include the **PrinterWebSocket.js** into the documents body tag where we tend to create the receipt creation or handle print jobs on the website.    

`<script src="printerWebSocket.js"></script>`

2. ### Initializing the PrinterWebSocket.
The python server is set to response on the port 8765 on default. We have to change the port from the python server code.
```
// Initialize WebSocket connection and wait for it to establish
PrinterWebSocket.initialize("ws://localhost:8765")
    .then(() => {
        
        console.log('Connected to Printer Server  - ' + PrinterWebSocket.getServerAddress());
     
        // Fetch the printers after connection is established
        console.log('Fetched Printer List');
        return PrinterWebSocket.fetchPrinters();
    })
    .then((printers) => {
        // Populate printer dropdown with fetched printers
        console.log('Printer List Updated');
        populatePrinterDropdown(printers);
        console.log("Array of printers:", printers); // Log the printer array
    })
    .catch((error) => {
        console.error("Error occurred:", error);
    });
```

2. ### Printing a Raw TSPL Data
After successful initialization of WebSocket connection with the server, we are ready to print.
```
var paperSize = printerPaperSelect.value; // Get selected paper size in 80*40 format (mm scale)
var tsplData =
    `
    SIZE ${paperSize.replace('*', ' mm, ')} mm 
    GAP 3 mm, 0 mm
    CLS
    TEXT 25,60,"4",0,1,1,"26 OCT T 07"
    TEXT 25,120,"5",0,1,1,"105570553"
    TEXT 25,180,"1",0,1,1,"Liopetra"
    PRINT 1,1
`;
PrinterWebSocket.print(printerName, tsplData);


```  


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
