#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple HTTP Server for DNS Monitor Demo
Basic implementation using only Python standard library for demonstration
"""

import os
import sys
import json
import time
import random
import sqlite3
import subprocess
import re
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path

class DNSMonitorHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.frontend_dir = Path(__file__).parent.parent / 'frontend'
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # API endpoints
        if path.startswith('/api/'):
            self.handle_api_request(path)
        # Static files
        elif path == '/' or path == '/index.html':
            self.serve_file('index.html', 'text/html')
        elif path.endswith('.css'):
            self.serve_file(path[1:], 'text/css')
        elif path.endswith('.js'):
            self.serve_file(path[1:], 'application/javascript')
        elif path.endswith('.html'):
            self.serve_file(path[1:], 'text/html')
        else:
            self.send_error(404, "File not found")
    
    def handle_api_request(self, path):
        """Handle API requests"""
        try:
            if path == '/api/system/stats':
                self.send_json_response(self.get_system_stats())
            elif path == '/api/dns/stats':
                self.send_json_response(self.get_dns_stats())
            elif path == '/api/dns/queries':
                self.send_json_response(self.get_dns_queries())
            elif path == '/api/history/system':
                self.send_json_response(self.get_system_history())
            elif path == '/api/history/dns':
                self.send_json_response(self.get_dns_history())
            else:
                self.send_error(404, "API endpoint not found")
        except Exception as e:
            self.send_json_response({'error': str(e)}, status=500)
    
    def get_system_stats(self):
        """Get system statistics (simplified version)"""
        try:
            # Get CPU info
            cpu_percent = self.get_cpu_usage()
            
            # Get memory info
            memory_info = self.get_memory_info()
            
            # Get disk info
            disk_info = self.get_disk_info()
            
            # Get network info (simplified)
            network_info = self.get_network_info()
            
            # Get load average
            load_avg = self.get_load_average()
            
            # Get uptime
            uptime = self.get_uptime()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': os.cpu_count() or 1,
                    'frequency': {
                        'current': 2400,  # Mock value
                        'min': 1200,
                        'max': 3600
                    }
                },
                'memory': memory_info,
                'disk': disk_info,
                'network': network_info,
                'load_average': load_avg,
                'uptime': uptime
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_dns_stats(self):
        """Get DNS statistics (simplified version)"""
        try:
            # Mock DNS data since we don't have real BIND9 access
            return {
                'timestamp': datetime.now().isoformat(),
                'bind_status': {
                    'process_running': True,
                    'service_status': {'active': True, 'status': 'active'},
                    'config_status': {'valid': True},
                    'version': 'BIND 9.16.1 (Demo)'
                },
                'query_stats': {
                    'total_queries': random.randint(10000, 50000),
                    'qps': round(random.uniform(10, 100), 2),
                    'queries_per_minute': random.randint(500, 2000),
                    'queries_per_hour': random.randint(30000, 120000)
                },
                'response_times': {
                    'average': round(random.uniform(1, 50), 2),
                    'min': round(random.uniform(0.5, 2), 2),
                    'max': round(random.uniform(50, 200), 2)
                },
                'query_types': {
                    'A': {'count': random.randint(1000, 5000), 'percentage': random.uniform(40, 60)},
                    'AAAA': {'count': random.randint(500, 2000), 'percentage': random.uniform(15, 25)},
                    'MX': {'count': random.randint(100, 500), 'percentage': random.uniform(5, 10)},
                    'CNAME': {'count': random.randint(200, 800), 'percentage': random.uniform(8, 15)},
                    'TXT': {'count': random.randint(50, 300), 'percentage': random.uniform(2, 8)},
                    'NS': {'count': random.randint(20, 100), 'percentage': random.uniform(1, 3)},
                    'SOA': {'count': random.randint(10, 50), 'percentage': random.uniform(0.5, 2)},
                    'PTR': {'count': random.randint(30, 150), 'percentage': random.uniform(1, 5)}
                },
                'top_domains': [
                    {'domain': 'example.com', 'count': random.randint(100, 500)},
                    {'domain': 'google.com', 'count': random.randint(80, 400)},
                    {'domain': 'github.com', 'count': random.randint(60, 300)},
                    {'domain': 'stackoverflow.com', 'count': random.randint(50, 250)},
                    {'domain': 'ubuntu.com', 'count': random.randint(40, 200)},
                    {'domain': 'python.org', 'count': random.randint(30, 150)},
                    {'domain': 'mozilla.org', 'count': random.randint(25, 120)},
                    {'domain': 'docker.com', 'count': random.randint(20, 100)},
                    {'domain': 'nginx.org', 'count': random.randint(15, 80)},
                    {'domain': 'debian.org', 'count': random.randint(10, 60)}
                ],
                'recent_queries': self.generate_mock_queries(),
                'service_health': {
                    'status': 'healthy',
                    'issues': []
                }
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_dns_queries(self):
        """Get recent DNS queries"""
        return self.generate_mock_queries()
    
    def get_system_history(self):
        """Get system monitoring history"""
        # Return mock historical data
        history = []
        for i in range(24):  # Last 24 hours
            timestamp = datetime.now().replace(hour=i, minute=0, second=0, microsecond=0)
            history.append({
                'timestamp': timestamp.isoformat(),
                'cpu_percent': random.uniform(10, 80),
                'memory_percent': random.uniform(30, 90),
                'disk_percent': random.uniform(20, 70),
                'load_avg_1min': random.uniform(0.1, 2.0),
                'network_upload_speed': random.uniform(1000, 10000),
                'network_download_speed': random.uniform(5000, 50000)
            })
        return history
    
    def get_dns_history(self):
        """Get DNS monitoring history"""
        # Return mock DNS historical data
        history = []
        for i in range(24):  # Last 24 hours
            timestamp = datetime.now().replace(hour=i, minute=0, second=0, microsecond=0)
            history.append({
                'timestamp': timestamp.isoformat(),
                'bind_running': True,
                'service_active': True,
                'total_queries': random.randint(1000, 10000),
                'qps': random.uniform(10, 100),
                'queries_per_minute': random.randint(500, 2000),
                'queries_per_hour': random.randint(30000, 120000),
                'avg_response_time': random.uniform(1, 50),
                'config_valid': True
            })
        return history
    
    def generate_mock_queries(self):
        """Generate mock DNS queries for demonstration"""
        domains = [
            'example.com', 'google.com', 'github.com', 'stackoverflow.com',
            'ubuntu.com', 'python.org', 'mozilla.org', 'docker.com',
            'nginx.org', 'debian.org', 'cloudflare.com', 'amazon.com'
        ]
        
        query_types = ['A', 'AAAA', 'MX', 'CNAME', 'TXT', 'NS', 'SOA', 'PTR']
        
        queries = []
        for i in range(20):  # Generate 20 mock queries
            timestamp = datetime.now().replace(second=random.randint(0, 59))
            queries.append({
                'timestamp': timestamp.isoformat(),
                'client_ip': f"192.168.1.{random.randint(1, 254)}",
                'domain': random.choice(domains),
                'query_type': random.choice(query_types),
                'response_time': round(random.uniform(1, 100), 2)
            })
        
        return sorted(queries, key=lambda x: x['timestamp'], reverse=True)
    
    def get_cpu_usage(self):
        """Get CPU usage percentage"""
        try:
            # Try to get CPU usage from /proc/stat
            with open('/proc/stat', 'r') as f:
                line = f.readline()
                cpu_times = [int(x) for x in line.split()[1:]]
                idle_time = cpu_times[3]
                total_time = sum(cpu_times)
                usage = 100 * (total_time - idle_time) / total_time
                return round(usage, 2)
        except:
            # Fallback to mock data
            return round(random.uniform(10, 80), 2)
    
    def get_memory_info(self):
        """Get memory information"""
        try:
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()
                
            mem_info = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    mem_info[key.strip()] = value.strip()
            
            total = int(mem_info.get('MemTotal', '0').split()[0]) * 1024
            available = int(mem_info.get('MemAvailable', '0').split()[0]) * 1024
            free = int(mem_info.get('MemFree', '0').split()[0]) * 1024
            buffers = int(mem_info.get('Buffers', '0').split()[0]) * 1024
            cached = int(mem_info.get('Cached', '0').split()[0]) * 1024
            
            used = total - available
            percent = (used / total) * 100 if total > 0 else 0
            
            return {
                'total': total,
                'available': available,
                'used': used,
                'free': free,
                'percent': round(percent, 2),
                'buffers': buffers,
                'cached': cached
            }
        except:
            # Fallback to mock data
            total = 8 * 1024 * 1024 * 1024  # 8GB
            used = int(total * random.uniform(0.3, 0.8))
            return {
                'total': total,
                'available': total - used,
                'used': used,
                'free': total - used,
                'percent': round((used / total) * 100, 2),
                'buffers': int(total * 0.02),
                'cached': int(total * 0.15)
            }
    
    def get_disk_info(self):
        """Get disk information"""
        try:
            result = subprocess.run(['df', '/'], capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                total = int(parts[1]) * 1024
                used = int(parts[2]) * 1024
                free = int(parts[3]) * 1024
                percent = float(parts[4].rstrip('%'))
                
                return {
                    'total': total,
                    'used': used,
                    'free': free,
                    'percent': percent
                }
        except:
            pass
        
        # Fallback to mock data
        total = 100 * 1024 * 1024 * 1024  # 100GB
        used = int(total * random.uniform(0.2, 0.7))
        return {
            'total': total,
            'used': used,
            'free': total - used,
            'percent': round((used / total) * 100, 2)
        }
    
    def get_network_info(self):
        """Get network information"""
        # Mock network data
        return {
            'bytes_sent': random.randint(1000000, 10000000),
            'bytes_recv': random.randint(5000000, 50000000),
            'packets_sent': random.randint(10000, 100000),
            'packets_recv': random.randint(50000, 500000),
            'speed': {
                'upload': random.uniform(1000, 10000),
                'download': random.uniform(5000, 50000)
            }
        }
    
    def get_load_average(self):
        """Get load average"""
        try:
            with open('/proc/loadavg', 'r') as f:
                load_avg = f.read().split()[:3]
                return {
                    '1min': float(load_avg[0]),
                    '5min': float(load_avg[1]),
                    '15min': float(load_avg[2])
                }
        except:
            return {
                '1min': round(random.uniform(0.1, 2.0), 2),
                '5min': round(random.uniform(0.1, 2.0), 2),
                '15min': round(random.uniform(0.1, 2.0), 2)
            }
    
    def get_uptime(self):
        """Get system uptime"""
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.read().split()[0])
                return {
                    'seconds': uptime_seconds,
                    'boot_time': time.time() - uptime_seconds
                }
        except:
            # Mock uptime
            uptime_seconds = random.randint(3600, 864000)  # 1 hour to 10 days
            return {
                'seconds': uptime_seconds,
                'boot_time': time.time() - uptime_seconds
            }
    
    def serve_file(self, filename, content_type):
        """Serve static files"""
        try:
            file_path = self.frontend_dir / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-Type', content_type + '; charset=utf-8')
                self.send_header('Content-Length', str(len(content.encode('utf-8'))))
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
            else:
                self.send_error(404, f"File not found: {filename}")
        except Exception as e:
            self.send_error(500, f"Error serving file: {str(e)}")
    
    def send_json_response(self, data, status=200):
        """Send JSON response"""
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(json_str.encode('utf-8'))))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json_str.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to customize logging"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

def main():
    """Main function to start the server"""
    host = '0.0.0.0'
    port = 5000
    
    print(f"Starting DNS Monitor Demo Server on {host}:{port}")
    print(f"Frontend directory: {Path(__file__).parent.parent / 'frontend'}")
    print(f"Open your browser to: http://localhost:{port}")
    print("Press Ctrl+C to stop the server")
    
    try:
        server = HTTPServer((host, port), DNSMonitorHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()
        print("Server stopped.")

if __name__ == '__main__':
    main()