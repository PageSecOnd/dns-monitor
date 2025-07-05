// DNS Monitor - Main Application
// Main application logic and UI updates

class DNSMonitor {
    constructor() {
        this.isConnected = false;
        this.isPaused = false;
        this.lastUpdateTime = null;
        this.queryCount = 0;
        this.charts = {};
        this.currentData = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.updateClock();
        this.startClockTimer();
        this.hideLoadingOverlay();
        
        // Initialize charts
        this.initializeCharts();
        
        // Start monitoring
        this.startMonitoring();
    }
    
    setupEventListeners() {
        // Refresh button
        document.getElementById('refresh-queries')?.addEventListener('click', () => {
            this.refreshQueries();
        });
        
        // Clear queries button
        document.getElementById('clear-queries')?.addEventListener('click', () => {
            this.clearQueries();
        });
        
        // Pause/Resume button
        document.getElementById('pause-queries')?.addEventListener('click', () => {
            this.togglePause();
        });
        
        // Window resize handler
        window.addEventListener('resize', () => {
            this.handleResize();
        });
        
        // Visibility change handler
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseMonitoring();
            } else {
                this.resumeMonitoring();
            }
        });
    }
    
    startMonitoring() {
        // Connect to WebSocket
        this.connectWebSocket();
        
        // Start periodic updates
        this.startPeriodicUpdates();
    }
    
    connectWebSocket() {
        // This will be handled in websocket.js
        console.log('WebSocket connection will be established in websocket.js');
    }
    
    startPeriodicUpdates() {
        // Update every 5 seconds if not connected via WebSocket
        this.updateInterval = setInterval(() => {
            if (!this.isConnected) {
                this.fetchData();
            }
        }, 5000);
    }
    
    async fetchData() {
        try {
            const [systemData, dnsData] = await Promise.all([
                fetch('/api/system/stats').then(r => r.json()),
                fetch('/api/dns/stats').then(r => r.json())
            ]);
            
            this.currentData = {
                system: systemData,
                dns: dnsData,
                timestamp: new Date().toISOString()
            };
            
            this.updateUI(this.currentData);
        } catch (error) {
            console.error('Error fetching data:', error);
            this.showError('Failed to fetch monitoring data');
        }
    }
    
    updateUI(data) {
        if (!data) return;
        
        this.updateSystemStats(data.system);
        this.updateDNSStats(data.dns);
        this.updateConnectionStatus(true);
        this.lastUpdateTime = new Date();
    }
    
    updateSystemStats(systemData) {
        if (!systemData) return;
        
        // Update CPU
        this.updateCPUStats(systemData.cpu);
        
        // Update Memory
        this.updateMemoryStats(systemData.memory);
        
        // Update Disk
        this.updateDiskStats(systemData.disk);
        
        // Update Network
        this.updateNetworkStats(systemData.network);
        
        // Update Load Average
        this.updateLoadStats(systemData.load_average);
        
        // Update Uptime
        this.updateUptimeStats(systemData.uptime);
    }
    
    updateCPUStats(cpuData) {
        if (!cpuData) return;
        
        const percent = Math.round(cpuData.percent || 0);
        const cores = cpuData.count || 0;
        const freq = cpuData.frequency?.current || 0;
        
        // Update CPU gauge
        this.updateGauge('cpu-gauge', percent);
        
        // Update display values
        this.updateElement('cpu-percent', percent);
        this.updateElement('cpu-cores', cores);
        this.updateElement('cpu-freq', `${(freq / 1000).toFixed(2)} GHz`);
        
        // Update status
        this.updateStatus('cpu-status', percent > 80 ? 'warning' : 'normal');
    }
    
    updateMemoryStats(memoryData) {
        if (!memoryData) return;
        
        const percent = Math.round(memoryData.percent || 0);
        const used = this.formatBytes(memoryData.used || 0);
        const total = this.formatBytes(memoryData.total || 0);
        
        // Update progress bar
        this.updateProgressBar('memory-progress', percent);
        
        // Update display values
        this.updateElement('memory-percent', `${percent}%`);
        this.updateElement('memory-used', used);
        this.updateElement('memory-total', total);
        
        // Update status
        this.updateStatus('memory-status', percent > 85 ? 'warning' : 'normal');
    }
    
    updateDiskStats(diskData) {
        if (!diskData) return;
        
        const percent = Math.round(diskData.percent || 0);
        const used = this.formatBytes(diskData.used || 0);
        const total = this.formatBytes(diskData.total || 0);
        
        // Update progress bar
        this.updateProgressBar('disk-progress', percent);
        
        // Update display values
        this.updateElement('disk-percent', `${percent}%`);
        this.updateElement('disk-used', used);
        this.updateElement('disk-total', total);
        
        // Update status
        this.updateStatus('disk-status', percent > 90 ? 'warning' : 'normal');
    }
    
    updateNetworkStats(networkData) {
        if (!networkData) return;
        
        const upload = this.formatBytes(networkData.speed?.upload || 0, true);
        const download = this.formatBytes(networkData.speed?.download || 0, true);
        const sent = this.formatBytes(networkData.bytes_sent || 0);
        const recv = this.formatBytes(networkData.bytes_recv || 0);
        
        // Update display values
        this.updateElement('network-upload', upload);
        this.updateElement('network-download', download);
        this.updateElement('network-sent', sent);
        this.updateElement('network-recv', recv);
        
        // Update status
        this.updateStatus('network-status', 'normal');
    }
    
    updateLoadStats(loadData) {
        if (!loadData) return;
        
        const load1 = (loadData['1min'] || 0).toFixed(2);
        const load5 = (loadData['5min'] || 0).toFixed(2);
        const load15 = (loadData['15min'] || 0).toFixed(2);
        
        // Update display values
        this.updateElement('load-1min', load1);
        this.updateElement('load-5min', load5);
        this.updateElement('load-15min', load15);
        
        // Update status
        const highLoad = parseFloat(load1) > 2.0;
        this.updateStatus('load-status', highLoad ? 'warning' : 'normal');
    }
    
    updateUptimeStats(uptimeData) {
        if (!uptimeData) return;
        
        const uptime = this.formatUptime(uptimeData.seconds || 0);
        this.updateElement('system-uptime', uptime);
    }
    
    updateDNSStats(dnsData) {
        if (!dnsData) return;
        
        // Update service status
        this.updateDNSServiceStatus(dnsData.bind_status);
        
        // Update query statistics
        this.updateQueryStats(dnsData.query_stats);
        
        // Update recent queries
        this.updateRecentQueries(dnsData.recent_queries);
        
        // Update charts
        this.updateCharts(dnsData);
        
        // Update top domains
        this.updateTopDomains(dnsData.top_domains);
    }
    
    updateDNSServiceStatus(bindStatus) {
        if (!bindStatus) return;
        
        const processRunning = bindStatus.process_running;
        const serviceActive = bindStatus.service_status?.active;
        const configValid = bindStatus.config_status?.valid;
        const version = bindStatus.version || 'Unknown';
        
        // Update indicator lights
        this.updateIndicatorLight('bind-process-light', processRunning);
        this.updateIndicatorLight('bind-service-light', serviceActive);
        this.updateIndicatorLight('bind-config-light', configValid);
        
        // Update version
        this.updateElement('bind-version', version);
        
        // Update overall status
        const overallStatus = processRunning && serviceActive && configValid ? 'normal' : 'warning';
        this.updateStatus('dns-service-status', overallStatus);
    }
    
    updateQueryStats(queryStats) {
        if (!queryStats) return;
        
        const total = queryStats.total_queries || 0;
        const qps = queryStats.qps || 0;
        const perMinute = queryStats.queries_per_minute || 0;
        
        // Update display values with animation
        this.updateElementWithAnimation('total-queries', total);
        this.updateElementWithAnimation('queries-per-second', qps.toFixed(2));
        this.updateElementWithAnimation('queries-per-minute', perMinute);
    }
    
    updateRecentQueries(queries) {
        if (!queries || this.isPaused) return;
        
        const tbody = document.getElementById('queries-table-body');
        if (!tbody) return;
        
        // Clear existing rows
        tbody.innerHTML = '';
        
        // Add new rows
        queries.slice(0, 50).forEach(query => {
            const row = this.createQueryRow(query);
            tbody.appendChild(row);
        });
    }
    
    createQueryRow(query) {
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
        
        return row;
    }
    
    updateTopDomains(domains) {
        if (!domains) return;
        
        const container = document.getElementById('top-domains-list');
        if (!container) return;
        
        container.innerHTML = '';
        
        domains.forEach((domain, index) => {
            const item = document.createElement('div');
            item.className = 'domain-item';
            item.innerHTML = `
                <span class="domain-name">${domain.domain}</span>
                <span class="domain-count">${domain.count}</span>
            `;
            container.appendChild(item);
        });
    }
    
    // Utility functions
    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }
    
    updateElementWithAnimation(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.classList.add('counter-animation');
            element.textContent = value;
            
            setTimeout(() => {
                element.classList.remove('counter-animation');
            }, 500);
        }
    }
    
    updateStatus(id, status) {
        const element = document.getElementById(id);
        if (element) {
            element.className = `card-status ${status}`;
            element.textContent = status === 'normal' ? '正常' : status === 'warning' ? '警告' : '异常';
        }
    }
    
    updateProgressBar(id, percent) {
        const element = document.getElementById(id);
        if (element) {
            element.style.width = `${percent}%`;
            
            // Update color based on percentage
            if (percent > 90) {
                element.style.background = 'var(--gradient-danger)';
            } else if (percent > 75) {
                element.style.background = 'var(--gradient-secondary)';
            } else {
                element.style.background = 'var(--gradient-primary)';
            }
        }
    }
    
    updateIndicatorLight(id, active) {
        const element = document.getElementById(id);
        if (element) {
            element.className = `indicator-light ${active ? 'active' : ''}`;
        }
    }
    
    updateGauge(id, value) {
        // This will be implemented in charts.js
        if (this.charts[id]) {
            this.charts[id].update(value);
        }
    }
    
    updateConnectionStatus(connected) {
        this.isConnected = connected;
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.textContent = connected ? '已连接' : '断开连接';
            statusElement.style.color = connected ? 'var(--accent-green)' : 'var(--accent-red)';
        }
    }
    
    formatBytes(bytes, isSpeed = false) {
        if (bytes === 0) return '0 B';
        
        const k = 1024;
        const sizes = isSpeed ? ['B/s', 'KB/s', 'MB/s', 'GB/s'] : ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    formatUptime(seconds) {
        const days = Math.floor(seconds / 86400);
        const hours = Math.floor((seconds % 86400) / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        
        if (days > 0) {
            return `${days}天 ${hours}小时`;
        } else if (hours > 0) {
            return `${hours}小时 ${minutes}分钟`;
        } else {
            return `${minutes}分钟`;
        }
    }
    
    updateClock() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('zh-CN', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        
        const timeElement = document.getElementById('current-time');
        if (timeElement) {
            timeElement.textContent = timeString;
        }
    }
    
    startClockTimer() {
        setInterval(() => {
            this.updateClock();
        }, 1000);
    }
    
    hideLoadingOverlay() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.add('hidden');
        }
    }
    
    showError(message) {
        console.error(message);
        // Could implement toast notifications here
    }
    
    // Event handlers
    refreshQueries() {
        this.fetchData();
    }
    
    clearQueries() {
        const tbody = document.getElementById('queries-table-body');
        if (tbody) {
            tbody.innerHTML = '';
        }
    }
    
    togglePause() {
        this.isPaused = !this.isPaused;
        const button = document.getElementById('pause-queries');
        if (button) {
            button.textContent = this.isPaused ? '继续' : '暂停';
        }
    }
    
    handleResize() {
        // Handle responsive chart resizing
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.resize) {
                chart.resize();
            }
        });
    }
    
    pauseMonitoring() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
    }
    
    resumeMonitoring() {
        this.startPeriodicUpdates();
    }
    
    initializeCharts() {
        // Charts will be initialized in charts.js
        console.log('Charts will be initialized in charts.js');
    }
    
    updateCharts(dnsData) {
        // Charts will be updated in charts.js
        if (window.chartManager) {
            window.chartManager.updateCharts(dnsData);
        }
    }
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dnsMonitor = new DNSMonitor();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (window.dnsMonitor) {
        if (document.hidden) {
            window.dnsMonitor.pauseMonitoring();
        } else {
            window.dnsMonitor.resumeMonitoring();
        }
    }
});

// Handle window beforeunload
window.addEventListener('beforeunload', () => {
    if (window.dnsMonitor) {
        window.dnsMonitor.pauseMonitoring();
    }
});