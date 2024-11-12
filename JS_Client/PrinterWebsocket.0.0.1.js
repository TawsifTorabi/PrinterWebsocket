/* 

PrinterWebSocket.js

 By @TawsifTorabi
 https://github.com/TawsifTorabi

//version 0.0.1 (Beta) 

*/

var PrinterWebSocket = (function () {
    var socket;
    var isConnected = false;
    var uniqID = generateUID();
    var connectionTimeout = 2000; // 2 seconds timeout
    var printerList = []; // To store printers
    var printerStatus = "idle"; // Default printer status
    var CurrentUrl = '';
  
    // Initialize PrinterWebSocket
    function initialize(url) {
      CurrentUrl = url;
      return connect(url);
    }
  
    // Function to connect to the WebSocket server
    function connect(url) {
      return new Promise((resolve, reject) => {
        // Check if already connected
        if (isConnected) {
          console.warn(
            "WebSocket connection already exists and is still active. Use the existing connection."
          );
          resolve(); // Immediately resolve if already connected
          return;
        }
  
        socket = new WebSocket(url);
  
        socket.onopen = function () {
          console.log("Connected to WebSocket server.");
          isConnected = true;
          updateTimestamp(); // Update timestamp on open
          resolve(); // Resolve the promise when connection is open
        };
  
        socket.onmessage = function (event) {
          var data = JSON.parse(event.data);
          console.log("Received:", data);
          handleMessage(data); // Call the unified handler for all messages
          updateTimestamp(); // Update timestamp on message
        };
  
        socket.onclose = function () {
          console.log("WebSocket connection closed.");
          isConnected = false;
          resetConnection(); // Reset connection state on close
        };
  
        socket.onerror = function (error) {
          console.error("WebSocket error:", error);
          reject(error); // Reject the promise if there’s an error
        };
      });
    }
  
    // Reset the connection state
    function resetConnection() {
      socket = null; // Clear the socket reference
      uniqID = generateUID(); // Generate a new unique ID for future connections
      printerList = []; // Clear printer list on reset
    }
  
    // Update the connection timestamp in memory
    function updateTimestamp() {
      // Optionally implement logic to track the last activity timestamp here
    }
  
    // Mapping of printer status codes to human-readable messages
    const errorCodeMessages = {
      0: "No error",
      1: "The printer is out of paper.",
      2: "The printer is paused.",
      3: "There is a printer error.",
      4: "The printer is printing.",
      5: "The job failed.",
      6: "The printer is jammed.",
      // Add more codes as needed...
    };
  
    // Handle incoming messages from the server
    function handleMessage(data) {
      if (data.result) {
        console.log("Received result:", data.result);
        printerList = data.result; // Store the printers in the array
        populatePrinterDropdown(data.result);
      } else if (data.status) {
        console.log("Status:", data.status, "Message:", data.message);
  
        // Check for error status and log the error code
        if (data.status === "error") {
          const errorCode = data.status_code;
          console.error("Error Code:", errorCode);
          console.error("Error Message:", data.message);
  
          // Translate error code to human-readable message
          const translatedMessage =
            errorCodeMessages[errorCode] || "Unknown error code.";
          console.error("Translated Message:", translatedMessage);
        }
  
        // Update printer status if received from the server
        if (data.status_code === 4) {
          printerStatus = "printing"; // Printer is currently printing
        } else if (data.status_code === 0) {
          printerStatus = "idle"; // Printer is idle
        }
      }
    }
  
    // Fetch the list of printers from the server
    function fetchPrinters() {
      return new Promise((resolve, reject) => {
        if (!isConnected) {
          console.error("Not connected to WebSocket server.");
          return reject("Not connected to WebSocket server.");
        }
  
        var message = {
          call: "printers.find",
          uid: uniqID,
        };
  
        socket.send(JSON.stringify(message));
  
        // Listen for the message event to resolve the promise
        socket.onmessage = function (event) {
          var data = JSON.parse(event.data);
          if (data.result) {
            resolve(data.result); // Resolve with the printers array
          } else {
            reject("Failed to fetch printers.");
          }
        };
      });
    }
  
    // Send a print request to the server
    function print(printerName, tsplData) {
      if (!isConnected) {
        console.error("Not connected to WebSocket server.");
        return;
      }
  
      var message = {
        call: "print",
        uid: uniqID,
        params: {
          printer: { name: printerName },
          data: [tsplData], // Ensure data is in an array
        },
      };
      socket.send(JSON.stringify(message));
    }
  
    // Generate a unique identifier
    function generateUID() {
      return "uid-" + Math.random().toString(36).substr(2, 16);
    }
  
    // Public API
    return {
      initialize: initialize,
      fetchPrinters: fetchPrinters,
      print: print,
      getUniqID: function () {
        return uniqID;
      },
      isConnected: function () {
        return isConnected;
      },
      getPrinterStatus: function () {
        return printerStatus; // Expose the printer status
      },
      getServerAddress: function () {
        return CurrentUrl; // Expose the printer status
      },
      resetConnection: resetConnection, // Make resetConnection public for window event
    };
  })();
  
  // Ensure the connection state resets when the window is unloaded
  window.addEventListener("beforeunload", function () {
    PrinterWebSocket.resetConnection(); // Optional: Clear any local state
  });
  