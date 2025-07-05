// DNS Monitor - Charts and Visualizations
// Chart.js implementations for system and DNS monitoring

class ChartManager {
    constructor() {
        this.charts = {};
        this.chartOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#ffffff',
                        font: {
                            family: 'Rajdhani',
                            size: 12
                        }
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: '#b0b0b0',
                        font: {
                            family: 'Rajdhani'
                        }
                    },
                    grid: {
                        color: '#333333'
                    }
                },
                y: {
                    ticks: {
                        color: '#b0b0b0',
                        font: {
                            family: 'Rajdhani'
                        }
                    },
                    grid: {
                        color: '#333333'
                    }
                }
            }
        };
        
        this.init();
    }
    
    init() {
        // Set Chart.js defaults
        Chart.defaults.font.family = 'Rajdhani';
        Chart.defaults.color = '#ffffff';
        Chart.defaults.backgroundColor = 'rgba(0, 255, 255, 0.2)';
        Chart.defaults.borderColor = '#00ffff';
        
        // Initialize charts
        this.initializeCPUGauge();
        this.initializeQueryTypeChart();
        this.initializeResponseTimeChart();
        this.initializeSystemTrendChart();
        this.initializeDNSTrendChart();
    }
    
    initializeCPUGauge() {
        const canvas = document.getElementById('cpu-gauge');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        
        // Create custom gauge chart
        this.charts.cpuGauge = new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [0, 100],
                    backgroundColor: [
                        'rgba(0, 255, 255, 0.8)',
                        'rgba(42, 42, 42, 0.3)'
                    ],
                    borderColor: [
                        '#00ffff',
                        '#2a2a2a'
                    ],
                    borderWidth: 2,
                    cutout: '70%'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        enabled: false
                    }
                },
                rotation: -90,
                circumference: 180,
                animation: {
                    animateRotate: true,
                    duration: 1000
                }
            }
        });
    }
    
    initializeQueryTypeChart() {
        const canvas = document.getElementById('query-type-chart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        
        this.charts.queryTypeChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['A', 'AAAA', 'MX', 'CNAME', 'TXT', 'NS', 'SOA', 'PTR'],
                datasets: [{
                    data: [0, 0, 0, 0, 0, 0, 0, 0],
                    backgroundColor: [
                        'rgba(0, 255, 255, 0.8)',
                        'rgba(255, 0, 255, 0.8)',
                        'rgba(0, 255, 0, 0.8)',
                        'rgba(255, 136, 0, 0.8)',
                        'rgba(255, 0, 68, 0.8)',
                        'rgba(136, 0, 255, 0.8)',
                        'rgba(255, 255, 0, 0.8)',
                        'rgba(0, 136, 255, 0.8)'
                    ],
                    borderColor: [
                        '#00ffff',
                        '#ff00ff',
                        '#00ff00',
                        '#ff8800',
                        '#ff0044',
                        '#8800ff',
                        '#ffff00',
                        '#0088ff'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#ffffff',
                            font: {
                                family: 'Rajdhani',
                                size: 10
                            },
                            padding: 15,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(26, 26, 26, 0.9)',
                        titleColor: '#ffffff',
                        bodyColor: '#b0b0b0',
                        borderColor: '#00ffff',
                        borderWidth: 1,
                        titleFont: {
                            family: 'Rajdhani'
                        },
                        bodyFont: {
                            family: 'Rajdhani'
                        },
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    animateScale: true,
                    duration: 1000
                }
            }
        });
    }
    
    initializeResponseTimeChart() {
        const canvas = document.getElementById('response-time-chart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        
        this.charts.responseTimeChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: '响应时间 (ms)',
                    data: [],
                    borderColor: '#00ffff',
                    backgroundColor: 'rgba(0, 255, 255, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#00ffff',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        labels: {
                            color: '#ffffff',
                            font: {
                                family: 'Rajdhani',
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(26, 26, 26, 0.9)',
                        titleColor: '#ffffff',
                        bodyColor: '#b0b0b0',
                        borderColor: '#00ffff',
                        borderWidth: 1,
                        titleFont: {
                            family: 'Rajdhani'
                        },
                        bodyFont: {
                            family: 'Rajdhani'
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: '时间',
                            color: '#ffffff',
                            font: {
                                family: 'Rajdhani',
                                size: 12
                            }
                        },
                        ticks: {
                            color: '#b0b0b0',
                            font: {
                                family: 'Rajdhani'
                            }
                        },
                        grid: {
                            color: '#333333'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: '响应时间 (ms)',
                            color: '#ffffff',
                            font: {
                                family: 'Rajdhani',
                                size: 12
                            }
                        },
                        ticks: {
                            color: '#b0b0b0',
                            font: {
                                family: 'Rajdhani'
                            }
                        },
                        grid: {
                            color: '#333333'
                        }
                    }
                },
                animation: {
                    duration: 1000,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }
    
    initializeSystemTrendChart() {
        // This would be used for system monitoring trends
        // Implementation can be added later for historical data
    }
    
    initializeDNSTrendChart() {
        // This would be used for DNS query trends
        // Implementation can be added later for historical data
    }
    
    // Update methods
    updateCPUGauge(value) {
        if (!this.charts.cpuGauge) return;
        
        const chart = this.charts.cpuGauge;
        chart.data.datasets[0].data = [value, 100 - value];
        
        // Update colors based on value
        if (value > 80) {
            chart.data.datasets[0].backgroundColor[0] = 'rgba(255, 0, 68, 0.8)';
            chart.data.datasets[0].borderColor[0] = '#ff0044';
        } else if (value > 60) {
            chart.data.datasets[0].backgroundColor[0] = 'rgba(255, 136, 0, 0.8)';
            chart.data.datasets[0].borderColor[0] = '#ff8800';
        } else {
            chart.data.datasets[0].backgroundColor[0] = 'rgba(0, 255, 255, 0.8)';
            chart.data.datasets[0].borderColor[0] = '#00ffff';
        }
        
        chart.update('none');
    }
    
    updateQueryTypeChart(data) {
        if (!this.charts.queryTypeChart || !data) return;
        
        const chart = this.charts.queryTypeChart;
        const labels = Object.keys(data);
        const values = Object.values(data).map(item => item.count || 0);
        
        chart.data.labels = labels;
        chart.data.datasets[0].data = values;
        chart.update('none');
    }
    
    updateResponseTimeChart(data) {
        if (!this.charts.responseTimeChart) return;
        
        const chart = this.charts.responseTimeChart;
        const now = new Date();
        const timeLabel = now.toLocaleTimeString('zh-CN', { 
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit' 
        });
        
        // Add new data point
        chart.data.labels.push(timeLabel);
        chart.data.datasets[0].data.push(data.average || 0);
        
        // Keep only last 20 data points
        if (chart.data.labels.length > 20) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
        }
        
        chart.update('none');
    }
    
    updateCharts(dnsData) {
        if (!dnsData) return;
        
        // Update query type chart
        if (dnsData.query_types) {
            this.updateQueryTypeChart(dnsData.query_types);
        }
        
        // Update response time chart
        if (dnsData.response_times) {
            this.updateResponseTimeChart(dnsData.response_times);
        }
        
        // Update average response time display
        if (dnsData.response_times && dnsData.response_times.average) {
            const element = document.getElementById('avg-response-time');
            if (element) {
                element.textContent = dnsData.response_times.average.toFixed(2);
                element.classList.add('counter-animation');
                setTimeout(() => {
                    element.classList.remove('counter-animation');
                }, 500);
            }
        }
    }
    
    // Utility methods
    resizeCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.resize) {
                chart.resize();
            }
        });
    }
    
    destroyCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.destroy) {
                chart.destroy();
            }
        });
        this.charts = {};
    }
    
    // Animation helpers
    animateNumber(element, start, end, duration = 1000) {
        const startTime = performance.now();
        const difference = end - start;
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easeProgress = this.easeInOutQuart(progress);
            const current = start + (difference * easeProgress);
            
            element.textContent = Math.round(current);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }
    
    easeInOutQuart(t) {
        return t < 0.5 ? 8 * t * t * t * t : 1 - 8 * (--t) * t * t * t;
    }
    
    // Theme support
    updateTheme(theme) {
        const isDark = theme === 'dark';
        const textColor = isDark ? '#ffffff' : '#000000';
        const gridColor = isDark ? '#333333' : '#cccccc';
        
        Object.values(this.charts).forEach(chart => {
            if (chart.options.plugins && chart.options.plugins.legend) {
                chart.options.plugins.legend.labels.color = textColor;
            }
            
            if (chart.options.scales) {
                if (chart.options.scales.x) {
                    chart.options.scales.x.ticks.color = textColor;
                    chart.options.scales.x.grid.color = gridColor;
                }
                if (chart.options.scales.y) {
                    chart.options.scales.y.ticks.color = textColor;
                    chart.options.scales.y.grid.color = gridColor;
                }
            }
            
            chart.update('none');
        });
    }
}

// Initialize chart manager
document.addEventListener('DOMContentLoaded', () => {
    window.chartManager = new ChartManager();
    
    // Connect to main application
    if (window.dnsMonitor) {
        window.dnsMonitor.charts = window.chartManager.charts;
    }
});

// Handle window resize
window.addEventListener('resize', () => {
    if (window.chartManager) {
        window.chartManager.resizeCharts();
    }
});

// Export for use in other modules
window.ChartManager = ChartManager;