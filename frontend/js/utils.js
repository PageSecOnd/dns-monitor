// DNS Monitor - Utility Functions
// Helper functions and utilities

class Utils {
    // Format bytes to human readable format
    static formatBytes(bytes, decimals = 2, isSpeed = false) {
        if (bytes === 0) return '0 B';
        
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = isSpeed ? ['B/s', 'KB/s', 'MB/s', 'GB/s', 'TB/s'] : ['B', 'KB', 'MB', 'GB', 'TB'];
        
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }
    
    // Format uptime to human readable format
    static formatUptime(seconds) {
        const days = Math.floor(seconds / 86400);
        const hours = Math.floor((seconds % 86400) / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        
        if (days > 0) {
            return `${days}天 ${hours}小时 ${minutes}分钟`;
        } else if (hours > 0) {
            return `${hours}小时 ${minutes}分钟`;
        } else if (minutes > 0) {
            return `${minutes}分钟 ${secs}秒`;
        } else {
            return `${secs}秒`;
        }
    }
    
    // Format time to Chinese format
    static formatTime(date) {
        if (!date) return '';
        
        const d = new Date(date);
        return d.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        });
    }
    
    // Get time ago string
    static getTimeAgo(date) {
        if (!date) return '';
        
        const now = new Date();
        const past = new Date(date);
        const diff = now - past;
        
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        
        if (days > 0) {
            return `${days}天前`;
        } else if (hours > 0) {
            return `${hours}小时前`;
        } else if (minutes > 0) {
            return `${minutes}分钟前`;
        } else {
            return `${seconds}秒前`;
        }
    }
    
    // Debounce function
    static debounce(func, wait, immediate) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func(...args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func(...args);
        };
    }
    
    // Throttle function
    static throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
    
    // Deep clone object
    static deepClone(obj) {
        if (obj === null || typeof obj !== 'object') return obj;
        if (obj instanceof Date) return new Date(obj.getTime());
        if (obj instanceof Array) return obj.map(item => this.deepClone(item));
        if (typeof obj === 'object') {
            const cloned = {};
            for (let key in obj) {
                if (obj.hasOwnProperty(key)) {
                    cloned[key] = this.deepClone(obj[key]);
                }
            }
            return cloned;
        }
    }
    
    // Get status color based on value and thresholds
    static getStatusColor(value, type = 'percentage') {
        if (type === 'percentage') {
            if (value >= 90) return 'var(--accent-red)';
            if (value >= 75) return 'var(--accent-orange)';
            if (value >= 50) return 'var(--accent-cyan)';
            return 'var(--accent-green)';
        } else if (type === 'response_time') {
            if (value >= 1000) return 'var(--accent-red)';
            if (value >= 500) return 'var(--accent-orange)';
            if (value >= 100) return 'var(--accent-cyan)';
            return 'var(--accent-green)';
        }
        return 'var(--accent-cyan)';
    }
    
    // Generate random ID
    static generateId() {
        return Math.random().toString(36).substr(2, 9);
    }
    
    // Check if mobile device
    static isMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }
    
    // Check if touch device
    static isTouchDevice() {
        return ('ontouchstart' in window) || (navigator.msMaxTouchPoints > 0);
    }
    
    // Get viewport dimensions
    static getViewportSize() {
        return {
            width: Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0),
            height: Math.max(document.documentElement.clientHeight || 0, window.innerHeight || 0)
        };
    }
    
    // Animate number
    static animateNumber(element, start, end, duration = 1000, formatter = null) {
        const startTime = performance.now();
        const difference = end - start;
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easeProgress = this.easeInOutQuart(progress);
            const current = start + (difference * easeProgress);
            
            if (formatter) {
                element.textContent = formatter(current);
            } else {
                element.textContent = Math.round(current);
            }
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }
    
    // Easing function
    static easeInOutQuart(t) {
        return t < 0.5 ? 8 * t * t * t * t : 1 - 8 * (--t) * t * t * t;
    }
    
    // Local storage helpers
    static saveToStorage(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('Error saving to localStorage:', error);
        }
    }
    
    static loadFromStorage(key, defaultValue = null) {
        try {
            const value = localStorage.getItem(key);
            return value ? JSON.parse(value) : defaultValue;
        } catch (error) {
            console.error('Error loading from localStorage:', error);
            return defaultValue;
        }
    }
    
    static removeFromStorage(key) {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.error('Error removing from localStorage:', error);
        }
    }
    
    // DOM helpers
    static createElement(tag, className = '', innerHTML = '') {
        const element = document.createElement(tag);
        if (className) element.className = className;
        if (innerHTML) element.innerHTML = innerHTML;
        return element;
    }
    
    static addEventListeners(element, events) {
        for (const [event, handler] of Object.entries(events)) {
            element.addEventListener(event, handler);
        }
    }
    
    static removeEventListeners(element, events) {
        for (const [event, handler] of Object.entries(events)) {
            element.removeEventListener(event, handler);
        }
    }
    
    // CSS helpers
    static addCSS(css) {
        const style = document.createElement('style');
        style.textContent = css;
        document.head.appendChild(style);
        return style;
    }
    
    static removeClass(element, className) {
        if (element.classList.contains(className)) {
            element.classList.remove(className);
        }
    }
    
    static addClass(element, className) {
        if (!element.classList.contains(className)) {
            element.classList.add(className);
        }
    }
    
    static toggleClass(element, className) {
        element.classList.toggle(className);
    }
    
    // Network helpers
    static async fetchWithTimeout(url, options = {}, timeout = 10000) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);
        
        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal
            });
            clearTimeout(timeoutId);
            return response;
        } catch (error) {
            clearTimeout(timeoutId);
            throw error;
        }
    }
    
    static async retry(fn, retries = 3, delay = 1000) {
        try {
            return await fn();
        } catch (error) {
            if (retries > 0) {
                await new Promise(resolve => setTimeout(resolve, delay));
                return this.retry(fn, retries - 1, delay);
            } else {
                throw error;
            }
        }
    }
    
    // Color helpers
    static hexToRgb(hex) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : null;
    }
    
    static rgbToHex(r, g, b) {
        return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
    }
    
    static interpolateColor(color1, color2, factor) {
        const rgb1 = this.hexToRgb(color1);
        const rgb2 = this.hexToRgb(color2);
        
        if (!rgb1 || !rgb2) return color1;
        
        const r = Math.round(rgb1.r + (rgb2.r - rgb1.r) * factor);
        const g = Math.round(rgb1.g + (rgb2.g - rgb1.g) * factor);
        const b = Math.round(rgb1.b + (rgb2.b - rgb1.b) * factor);
        
        return this.rgbToHex(r, g, b);
    }
    
    // Validation helpers
    static isValidIP(ip) {
        const ipv4Regex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
        const ipv6Regex = /^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$/;
        return ipv4Regex.test(ip) || ipv6Regex.test(ip);
    }
    
    static isValidDomain(domain) {
        const domainRegex = /^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$/;
        return domainRegex.test(domain);
    }
    
    // Performance helpers
    static measurePerformance(fn, label = 'Operation') {
        const start = performance.now();
        const result = fn();
        const end = performance.now();
        console.log(`${label} took ${end - start} milliseconds`);
        return result;
    }
    
    static async measurePerformanceAsync(fn, label = 'Async Operation') {
        const start = performance.now();
        const result = await fn();
        const end = performance.now();
        console.log(`${label} took ${end - start} milliseconds`);
        return result;
    }
    
    // Error handling
    static handleError(error, context = 'Unknown') {
        console.error(`Error in ${context}:`, error);
        
        // Log to external service if available
        if (window.errorLogger) {
            window.errorLogger.log(error, context);
        }
        
        // Show user-friendly message
        this.showToast(`发生错误: ${error.message}`, 'error');
    }
    
    // Toast notifications
    static showToast(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        // Add to page
        document.body.appendChild(toast);
        
        // Animate in
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Auto-remove
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, duration);
    }
}

// Export to global scope
window.Utils = Utils;

// Add CSS for toast notifications
Utils.addCSS(`
    .toast {
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--bg-card);
        color: var(--text-primary);
        padding: 12px 16px;
        border-radius: 8px;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-card);
        z-index: 1000;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
        font-family: 'Rajdhani', sans-serif;
        font-size: 14px;
    }
    
    .toast.show {
        opacity: 1;
        transform: translateX(0);
    }
    
    .toast-info {
        border-color: var(--accent-cyan);
    }
    
    .toast-success {
        border-color: var(--accent-green);
    }
    
    .toast-warning {
        border-color: var(--accent-orange);
    }
    
    .toast-error {
        border-color: var(--accent-red);
    }
    
    @media (max-width: 768px) {
        .toast {
            left: 20px;
            right: 20px;
            transform: translateY(-100%);
        }
        
        .toast.show {
            transform: translateY(0);
        }
    }
`);