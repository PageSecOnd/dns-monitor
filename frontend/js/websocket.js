// DNS Monitor - WebSocket Client
// Real-time communication with backend

class WebSocketClient {
    constructor() {
        this.socket = null;
        this.reconnectInterval = 5000;
        this.maxReconnectAttempts = 10;
        this.reconnectAttempts = 0;
        this.isConnected = false;
        this.listeners = new Map();
        this.messageQueue = [];
        
        this.init();
    }
    
    init() {
        this.connect();
        this.setupEventListeners();
    }
    
    connect() {
        try {
            // Get the WebSocket URL
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const host = window.location.host;
            const wsUrl = `${protocol}//${host}/socket.io/`;
            
            console.log('Connecting to WebSocket:', wsUrl);
            
            // Initialize Socket.IO connection
            this.socket = io(wsUrl, {
                transports: ['websocket', 'polling'],
                timeout: 10000,
                reconnection: true,
                reconnectionAttempts: this.maxReconnectAttempts,
                reconnectionDelay: 1000,
                reconnectionDelayMax: 5000
            });
            
            this.setupSocketEvents();
            
        } catch (error) {
            console.error('WebSocket connection error:', error);
            this.handleConnectionError();
        }
    }
    
    setupSocketEvents() {
        if (!this.socket) return;
        
        // Connection established
        this.socket.on('connect', () => {
            console.log('WebSocket connected');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.updateConnectionStatus(true);
            this.processPendingMessages();
            
            // Request current data
            this.socket.emit('request_current_data');
        });
        
        // Connection lost
        this.socket.on('disconnect', (reason) => {
            console.log('WebSocket disconnected:', reason);
            this.isConnected = false;
            this.updateConnectionStatus(false);
            
            // Auto-reconnect for certain disconnect reasons
            if (reason === 'io server disconnect') {
                // Server initiated disconnect, try to reconnect
                this.reconnect();
            }
        });
        
        // Connection error
        this.socket.on('connect_error', (error) => {
            console.error('WebSocket connection error:', error);
            this.handleConnectionError();
        });
        
        // Reconnection attempts
        this.socket.on('reconnect_attempt', (attemptNumber) => {
            console.log(`Reconnection attempt ${attemptNumber}`);
            this.reconnectAttempts = attemptNumber;
        });
        
        // Reconnection successful
        this.socket.on('reconnect', (attemptNumber) => {
            console.log(`Reconnected after ${attemptNumber} attempts`);
            this.reconnectAttempts = 0;
            this.updateConnectionStatus(true);
        });
        
        // Reconnection failed
        this.socket.on('reconnect_failed', () => {
            console.error('Failed to reconnect to WebSocket');
            this.updateConnectionStatus(false);
        });
        
        // Status message
        this.socket.on('status', (data) => {
            console.log('Status:', data.message);
            this.emit('status', data);
        });
        
        // Monitoring data
        this.socket.on('monitoring_data', (data) => {
            console.log('Received monitoring data:', data);
            this.handleMonitoringData(data);
        });
        
        // Error messages
        this.socket.on('error', (error) => {
            console.error('WebSocket error:', error);
            this.emit('error', error);
        });
        
        // Custom event handlers
        this.socket.on('dns_query', (data) => {
            this.handleDNSQuery(data);
        });
        
        this.socket.on('system_alert', (data) => {
            this.handleSystemAlert(data);
        });
    }
    
    setupEventListeners() {
        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseUpdates();
            } else {
                this.resumeUpdates();
            }
        });
        
        // Handle network status changes
        window.addEventListener('online', () => {
            console.log('Network online, attempting to reconnect');
            this.reconnect();
        });
        
        window.addEventListener('offline', () => {
            console.log('Network offline');
            this.updateConnectionStatus(false);
        });
    }
    
    reconnect() {
        if (this.isConnected) return;
        
        console.log('Attempting to reconnect...');
        
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            setTimeout(() => {
                this.connect();
            }, this.reconnectInterval);
        } else {
            console.error('Max reconnection attempts reached');
            this.updateConnectionStatus(false);
        }
    }
    
    handleConnectionError() {
        this.isConnected = false;
        this.updateConnectionStatus(false);
        
        // Fall back to HTTP polling
        this.fallbackToHTTP();
    }
    
    fallbackToHTTP() {
        console.log('Falling back to HTTP polling');
        
        // Notify main application to use HTTP polling
        if (window.dnsMonitor) {
            window.dnsMonitor.isConnected = false;
            window.dnsMonitor.startPeriodicUpdates();
        }
    }
    
    handleMonitoringData(data) {
        try {
            // Update main application with received data
            if (window.dnsMonitor) {
                window.dnsMonitor.updateUI(data);
            }
            
            // Update charts
            if (window.chartManager) {
                // Update CPU gauge
                if (data.system && data.system.cpu) {
                    window.chartManager.updateCPUGauge(data.system.cpu.percent);
                }
                
                // Update DNS charts
                if (data.dns) {
                    window.chartManager.updateCharts(data.dns);
                }
            }
            
            // Emit to custom listeners
            this.emit('monitoring_data', data);
            
        } catch (error) {
            console.error('Error handling monitoring data:', error);
        }
    }
    
    handleDNSQuery(data) {
        // Handle individual DNS query notifications
        console.log('DNS Query:', data);
        
        // Add to real-time query list
        this.addQueryToList(data);
        
        // Emit to listeners
        this.emit('dns_query', data);
    }
    
    handleSystemAlert(data) {
        // Handle system alerts
        console.log('System Alert:', data);
        
        // Show notification
        this.showNotification(data);
        
        // Emit to listeners
        this.emit('system_alert', data);
    }
    
    addQueryToList(query) {
        const tbody = document.getElementById('queries-table-body');
        if (!tbody) return;
        
        // Create new row
        const row = document.createElement('tr');
        row.className = 'table-row-enter';
        
        const timestamp = new Date(query.timestamp).toLocaleTimeString();
        const clientIP = query.client_ip || 'Unknown';
        const domain = query.domain || 'Unknown';
        const queryType = query.query_type || 'Unknown';
        const responseTime = query.response_time ? `${query.response_time}ms` : 'N/A';
        
        row.innerHTML = `
            <td>${timestamp}</td>
            <td>${clientIP}</td>
            <td>${domain}</td>
            <td>${queryType}</td>
            <td>${responseTime}</td>
        `;
        
        // Add to top of table
        tbody.insertBefore(row, tbody.firstChild);
        
        // Limit to 50 rows
        while (tbody.children.length > 50) {
            tbody.removeChild(tbody.lastChild);
        }
        
        // Add highlight animation
        row.classList.add('highlight');
        setTimeout(() => {
            row.classList.remove('highlight');
        }, 1000);
    }
    
    showNotification(alert) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.innerHTML = `
            <div class="notification-content">
                <h4>${alert.title}</h4>
                <p>${alert.message}</p>
                <button class="notification-close">×</button>
            </div>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
        
        // Close button handler
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        });
    }
    
    updateConnectionStatus(connected) {
        this.isConnected = connected;
        
        // Update UI
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.textContent = connected ? '已连接' : '断开连接';
            statusElement.style.color = connected ? 'var(--accent-green)' : 'var(--accent-red)';
        }
        
        // Update main application
        if (window.dnsMonitor) {
            window.dnsMonitor.updateConnectionStatus(connected);
        }
        
        // Emit to listeners
        this.emit('connection_status', { connected });
    }
    
    // Message handling
    send(event, data) {
        if (this.isConnected && this.socket) {
            this.socket.emit(event, data);
        } else {
            // Queue message for later
            this.messageQueue.push({ event, data });
        }
    }
    
    processPendingMessages() {
        while (this.messageQueue.length > 0) {
            const message = this.messageQueue.shift();
            this.send(message.event, message.data);
        }
    }
    
    // Event listener system
    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
    }
    
    off(event, callback) {
        if (this.listeners.has(event)) {
            const callbacks = this.listeners.get(event);
            const index = callbacks.indexOf(callback);
            if (index > -1) {
                callbacks.splice(index, 1);
            }
        }
    }
    
    emit(event, data) {
        if (this.listeners.has(event)) {
            this.listeners.get(event).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error('Error in event listener:', error);
                }
            });
        }
    }
    
    // Control methods
    pauseUpdates() {
        if (this.socket) {
            this.socket.emit('pause_updates');
        }
    }
    
    resumeUpdates() {
        if (this.socket) {
            this.socket.emit('resume_updates');
        }
    }
    
    requestCurrentData() {
        if (this.socket) {
            this.socket.emit('request_current_data');
        }
    }
    
    // Cleanup
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
        }
        this.isConnected = false;
        this.listeners.clear();
        this.messageQueue = [];
    }
}

// Initialize WebSocket client
document.addEventListener('DOMContentLoaded', () => {
    window.webSocketClient = new WebSocketClient();
    
    // Connect to main application
    if (window.dnsMonitor) {
        window.dnsMonitor.webSocket = window.webSocketClient;
    }
});

// Handle page unload
window.addEventListener('beforeunload', () => {
    if (window.webSocketClient) {
        window.webSocketClient.disconnect();
    }
});

// Export for use in other modules
window.WebSocketClient = WebSocketClient;