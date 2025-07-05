#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Monitor Module
Collects real-time system information including CPU, memory, disk, network stats
"""

import psutil
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SystemMonitor:
    def __init__(self):
        self.boot_time = psutil.boot_time()
        self.last_network_io = psutil.net_io_counters()
        self.last_disk_io = psutil.disk_io_counters()
        self.last_check_time = time.time()
        
    def get_system_stats(self):
        """Get comprehensive system statistics"""
        try:
            current_time = time.time()
            
            # CPU information
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory information
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk information
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Network information
            network_io = psutil.net_io_counters()
            network_interfaces = self._get_network_interfaces()
            
            # Calculate network speeds
            time_delta = current_time - self.last_check_time
            network_speeds = self._calculate_network_speeds(network_io, time_delta)
            
            # System load
            load_avg = psutil.getloadavg()
            
            # System uptime
            uptime = current_time - self.boot_time
            
            # Process information
            processes = self._get_top_processes()
            
            # Update last values
            self.last_network_io = network_io
            self.last_disk_io = disk_io
            self.last_check_time = current_time
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'frequency': {
                        'current': cpu_freq.current if cpu_freq else 0,
                        'min': cpu_freq.min if cpu_freq else 0,
                        'max': cpu_freq.max if cpu_freq else 0
                    }
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'free': memory.free,
                    'percent': memory.percent,
                    'buffers': memory.buffers,
                    'cached': memory.cached
                },
                'swap': {
                    'total': swap.total,
                    'used': swap.used,
                    'free': swap.free,
                    'percent': swap.percent
                },
                'disk': {
                    'total': disk_usage.total,
                    'used': disk_usage.used,
                    'free': disk_usage.free,
                    'percent': disk_usage.percent,
                    'io': {
                        'read_bytes': disk_io.read_bytes if disk_io else 0,
                        'write_bytes': disk_io.write_bytes if disk_io else 0,
                        'read_count': disk_io.read_count if disk_io else 0,
                        'write_count': disk_io.write_count if disk_io else 0
                    }
                },
                'network': {
                    'bytes_sent': network_io.bytes_sent,
                    'bytes_recv': network_io.bytes_recv,
                    'packets_sent': network_io.packets_sent,
                    'packets_recv': network_io.packets_recv,
                    'speed': network_speeds,
                    'interfaces': network_interfaces
                },
                'load_average': {
                    '1min': load_avg[0],
                    '5min': load_avg[1],
                    '15min': load_avg[2]
                },
                'uptime': {
                    'seconds': uptime,
                    'boot_time': self.boot_time
                },
                'processes': processes
            }
            
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {'error': str(e)}
    
    def _get_network_interfaces(self):
        """Get network interface information"""
        try:
            interfaces = {}
            for name, addrs in psutil.net_if_addrs().items():
                interfaces[name] = {
                    'addresses': [],
                    'stats': {}
                }
                
                for addr in addrs:
                    interfaces[name]['addresses'].append({
                        'family': str(addr.family),
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    })
                
                # Get interface statistics
                try:
                    stats = psutil.net_if_stats()[name]
                    interfaces[name]['stats'] = {
                        'isup': stats.isup,
                        'duplex': stats.duplex,
                        'speed': stats.speed,
                        'mtu': stats.mtu
                    }
                except:
                    pass
                    
            return interfaces
        except Exception as e:
            logger.error(f"Error getting network interfaces: {e}")
            return {}
    
    def _calculate_network_speeds(self, current_io, time_delta):
        """Calculate network speeds in bytes per second"""
        try:
            if time_delta <= 0:
                return {'upload': 0, 'download': 0}
                
            upload_speed = (current_io.bytes_sent - self.last_network_io.bytes_sent) / time_delta
            download_speed = (current_io.bytes_recv - self.last_network_io.bytes_recv) / time_delta
            
            return {
                'upload': max(0, upload_speed),
                'download': max(0, download_speed)
            }
        except Exception as e:
            logger.error(f"Error calculating network speeds: {e}")
            return {'upload': 0, 'download': 0}
    
    def _get_top_processes(self, limit=10):
        """Get top processes by CPU usage"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'username']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
            return processes[:limit]
        except Exception as e:
            logger.error(f"Error getting top processes: {e}")
            return []
    
    def get_system_health(self):
        """Get overall system health status"""
        try:
            stats = self.get_system_stats()
            
            # Define health thresholds
            health_status = {
                'overall': 'healthy',
                'warnings': [],
                'critical': []
            }
            
            # Check CPU usage
            if stats['cpu']['percent'] > 90:
                health_status['critical'].append(f"High CPU usage: {stats['cpu']['percent']:.1f}%")
            elif stats['cpu']['percent'] > 70:
                health_status['warnings'].append(f"Moderate CPU usage: {stats['cpu']['percent']:.1f}%")
            
            # Check memory usage
            if stats['memory']['percent'] > 95:
                health_status['critical'].append(f"Critical memory usage: {stats['memory']['percent']:.1f}%")
            elif stats['memory']['percent'] > 80:
                health_status['warnings'].append(f"High memory usage: {stats['memory']['percent']:.1f}%")
            
            # Check disk usage
            if stats['disk']['percent'] > 95:
                health_status['critical'].append(f"Critical disk usage: {stats['disk']['percent']:.1f}%")
            elif stats['disk']['percent'] > 85:
                health_status['warnings'].append(f"High disk usage: {stats['disk']['percent']:.1f}%")
            
            # Check load average
            if stats['load_average']['1min'] > stats['cpu']['count']:
                health_status['warnings'].append(f"High system load: {stats['load_average']['1min']:.2f}")
            
            # Determine overall status
            if health_status['critical']:
                health_status['overall'] = 'critical'
            elif health_status['warnings']:
                health_status['overall'] = 'warning'
            
            return health_status
            
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {'overall': 'error', 'error': str(e)}