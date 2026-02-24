/**
 * WebSocketManager handles the communication between the client and the MELODI backend.
 * It supports a request-response pattern (RPC) and event-based notifications.
 */
class WebSocketManager {
    constructor() {
        this.socket = null;
        this.url = null;
        this._pendingCalls = new Map(); // id -> {resolve, reject, timeout}
        this._listeners = new Map();    // eventType -> Set of callbacks
        this._reconnectAttempts = 0;
        this._maxReconnectDelay = 30000;
        this._rpcTimeout = 30000;       // 30 seconds
    }

    /**
     * Connect to the WebSocket server.
     * @param {string} url - The WebSocket URL (default: /ws)
     */
    connect(url = "/ws") {
        if (this.socket && (this.socket.readyState === WebSocket.CONNECTING || this.socket.readyState === WebSocket.OPEN)) {
            return;
        }

        // Handle relative URLs
        if (!url.startsWith("ws://") && !url.startsWith("wss://")) {
            const protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
            url = `${protocol}${window.location.host}${url}`;
        }

        this.url = url;
        console.log(`[WS] Connecting to ${url}...`);
        this.socket = new WebSocket(url);

        this.socket.onopen = () => {
            console.log("[WS] Connection established.");
            this._reconnectAttempts = 0;
            this._emit("open", null);
        };

        this.socket.onmessage = (event) => {
            this._handleMessage(event.data);
        };

        this.socket.onclose = (event) => {
            console.log(`[WS] Connection closed (code: ${event.code}).`);
            this.socket = null;
            this._emit("close", event);
            this._scheduleReconnect();
        };

        this.socket.onerror = (error) => {
            console.error("[WS] Error:", error);
            this._emit("error", error);
        };
    }

    /**
     * Call a registered module function on the backend.
     * @param {string} module - Module name.
     * @param {string} functionName - Function name in the module.
     * @param {object} params - Parameters object.
     * @returns {Promise<any>}
     */
    async call(module, functionName, params = {}) {
        if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
            throw new Error("WebSocket is not connected.");
        }

        const id = this._generateId();
        const payload = { id, module, function: functionName, params };

        return new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                if (this._pendingCalls.has(id)) {
                    this._pendingCalls.delete(id);
                    reject(new Error(`RPC Timeout: ${module}.${functionName} (${id})`));
                }
            }, this._rpcTimeout);

            this._pendingCalls.set(id, { resolve, reject, timeout });
            this.socket.send(JSON.stringify(payload));
        });
    }

    /**
     * Add an event listener for WebSocket events or broadcasted messages.
     * @param {string} type - Event type ('open', 'close', 'error', or custom)
     * @param {Function} callback 
     */
    on(type, callback) {
        if (!this._listeners.has(type)) {
            this._listeners.set(type, new Set());
        }
        this._listeners.get(type).add(callback);
    }

    /**
     * Remove an event listener.
     */
    off(type, callback) {
        if (this._listeners.has(type)) {
            this._listeners.get(type).delete(callback);
        }
    }

    /**
     * Disconnect the WebSocket.
     */
    disconnect() {
        if (this.socket) {
            this.socket.onclose = null; // Prevent auto-reconnect
            this.socket.close();
            this.socket = null;
        }
    }

    // --- Private Methods ---

    _handleMessage(data) {
        try {
            const message = JSON.parse(data);

            // 1. Check if it's an RPC response
            if (message.id && this._pendingCalls.has(message.id)) {
                const { resolve, reject, timeout } = this._pendingCalls.get(message.id);
                clearTimeout(timeout);
                this._pendingCalls.delete(message.id);
                
                if (message.status === "ok") {
                    resolve(message.result);
                } else {
                    reject(new Error(message.error || "Unknown RPC error"));
                }
                return;
            }

            // 2. Otherwise, treat as a generic event/broadcast
            this._emit("message", message);
            if (message.type) {
                this._emit(message.type, message.data || message);
            }

        } catch (e) {
            console.warn("[WS] Failed to parse message:", data, e);
        }
    }

    _emit(type, data) {
        const callbacks = this._listeners.get(type);
        if (callbacks) {
            callbacks.forEach(cb => {
                try {
                    cb(data);
                } catch (e) {
                    console.error(`[WS] Error in listener '${type}':`, e);
                }
            });
        }
    }

    _scheduleReconnect() {
        const delay = Math.min(1000 * Math.pow(2, this._reconnectAttempts), this._maxReconnectDelay);
        this._reconnectAttempts++;
        console.log(`[WS] Reconnecting in ${delay}ms...`);
        setTimeout(() => this.connect(this.url), delay);
    }

    _generateId() {
        return Math.random().toString(36).substring(2, 15) +
            Math.random().toString(36).substring(2, 15);
    }
}

// Global instance for convenience
window.wsManager = new WebSocketManager();
window.WebSocketManager = WebSocketManager;