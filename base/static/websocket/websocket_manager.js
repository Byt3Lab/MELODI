class WebSocketManager {
    constructor() {
        this.socket = null;
    }

    connect(url="/ws") {
        if (this.socket) {
            console.warn("WebSocket is already connected.");
            return;
        }

        this.socket = new WebSocket(url);

        this.socket.onopen = () => {
            console.log("WebSocket connection established.");
        };

        this.socket.onmessage = (event) => {
            console.log("Received message:", event.data);
            // Handle incoming messages here
        };

        this.socket.onclose = () => {
            console.log("WebSocket connection closed.");
            this.socket = null;
        };

        this.socket.onerror = (error) => {
            console.error("WebSocket error:", error);
        };
    }

    sendMessage(message) {
        if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
            console.warn("WebSocket is not connected.");
            return;
        }
        this.socket.send(message);
    }

    disconnect() {
        if (this.socket) {
            this.socket.close();
        }
    }
}

// Example usage:
// const wsManager = new WebSocketManager();
// wsManager.connect("ws://example.com/socket");
// wsManager.sendMessage("Hello, WebSocket!");
// wsManager.disconnect();

window.WebSocketManager = WebSocketManager;