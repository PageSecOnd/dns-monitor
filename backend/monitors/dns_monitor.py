#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DNS Monitor Module
Monitors BIND9 DNS server status and parses DNS query logs
"""

import os
import re
import subprocess
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class DNSMonitor:
    def __init__(self):
        self.bind_log_paths = [
            '/var/log/named/query.log',
            '/var/log/bind/query.log',
            '/var/log/syslog',
            '/var/log/messages'
        ]
        self.query_history = deque(maxlen=1000)
        self.query_stats = defaultdict(int)
        self.response_times = deque(maxlen=100)
        self.last_log_position = {}
        
    def get_dns_stats(self):
        """Get comprehensive DNS statistics"""
        try:
            # Get BIND9 service status
            bind_status = self._get_bind_status()
            
            # Parse recent queries
            recent_queries = self._parse_recent_queries()
            
            # Calculate statistics
            query_stats = self._calculate_query_stats()
            
            # Get response time statistics
            response_stats = self._get_response_time_stats()
            
            # Get query type distribution
            query_types = self._get_query_type_distribution()
            
            # Get top queried domains
            top_domains = self._get_top_domains()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'bind_status': bind_status,
                'recent_queries': recent_queries,
                'query_stats': query_stats,
                'response_times': response_stats,
                'query_types': query_types,
                'top_domains': top_domains,
                'service_health': self._get_service_health()
            }
            
        except Exception as e:
            logger.error(f"Error getting DNS stats: {e}")
            return {'error': str(e)}
    
    def _get_bind_status(self):
        """Get BIND9 service status"""
        try:
            # Check if named process is running
            result = subprocess.run(['pgrep', '-x', 'named'], 
                                  capture_output=True, text=True)
            process_running = result.returncode == 0
            
            # Get systemd service status
            service_status = {}
            try:
                result = subprocess.run(['systemctl', 'is-active', 'named'], 
                                      capture_output=True, text=True)
                service_status['active'] = result.stdout.strip() == 'active'
                service_status['status'] = result.stdout.strip()
            except:
                service_status['active'] = process_running
                service_status['status'] = 'unknown'
            
            # Get process information
            process_info = {}
            if process_running:
                try:
                    result = subprocess.run(['ps', '-o', 'pid,ppid,cpu,mem,cmd', '-C', 'named'], 
                                          capture_output=True, text=True)
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        headers = lines[0].split()
                        values = lines[1].split()
                        if len(values) >= 4:
                            process_info = {
                                'pid': values[0],
                                'ppid': values[1],
                                'cpu_percent': values[2],
                                'memory_percent': values[3],
                                'command': ' '.join(values[4:])
                            }
                except:
                    pass
            
            # Check configuration
            config_status = self._check_bind_config()
            
            return {
                'process_running': process_running,
                'service_status': service_status,
                'process_info': process_info,
                'config_status': config_status,
                'version': self._get_bind_version()
            }
            
        except Exception as e:
            logger.error(f"Error getting BIND status: {e}")
            return {'error': str(e)}
    
    def _get_bind_version(self):
        """Get BIND9 version"""
        try:
            result = subprocess.run(['named', '-v'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
            return 'unknown'
        except:
            return 'unknown'
    
    def _check_bind_config(self):
        """Check BIND9 configuration"""
        try:
            result = subprocess.run(['named-checkconf'], 
                                  capture_output=True, text=True)
            return {
                'valid': result.returncode == 0,
                'errors': result.stderr.strip() if result.stderr else None
            }
        except:
            return {'valid': False, 'errors': 'Cannot check configuration'}
    
    def _parse_recent_queries(self):
        """Parse recent DNS queries from logs"""
        try:
            queries = []
            
            for log_path in self.bind_log_paths:
                if os.path.exists(log_path):
                    try:
                        queries.extend(self._parse_log_file(log_path))
                    except Exception as e:
                        logger.warning(f"Error parsing {log_path}: {e}")
                        continue
            
            # Sort by timestamp and return most recent
            queries.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            return queries[:50]  # Return last 50 queries
            
        except Exception as e:
            logger.error(f"Error parsing recent queries: {e}")
            return []
    
    def _parse_log_file(self, log_path):
        """Parse a specific log file for DNS queries"""
        try:
            queries = []
            
            # Get current file position
            current_pos = self.last_log_position.get(log_path, 0)
            
            with open(log_path, 'r') as f:
                # Seek to last position
                f.seek(current_pos)
                
                # Read new lines
                new_lines = f.readlines()
                
                # Update position
                self.last_log_position[log_path] = f.tell()
                
                # Parse lines
                for line in new_lines:
                    query = self._parse_query_line(line)
                    if query:
                        queries.append(query)
                        self.query_history.append(query)
            
            return queries
            
        except Exception as e:
            logger.error(f"Error parsing log file {log_path}: {e}")
            return []
    
    def _parse_query_line(self, line):
        """Parse a single query line"""
        try:
            # BIND query log patterns
            patterns = [
                # Standard query log format
                r'(\d{2}-\w{3}-\d{4} \d{2}:\d{2}:\d{2}\.\d{3}).*client (@\S+).*query: (\S+) IN (\S+)',
                # Alternative format
                r'(\w{3} \d{2} \d{2}:\d{2}:\d{2}).*named.*client (\S+).*query: (\S+) IN (\S+)',
                # Syslog format
                r'(\w{3} \d{2} \d{2}:\d{2}:\d{2}).*named.*client (\S+)#\d+.*query: (\S+) IN (\S+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    timestamp_str, client_ip, domain, query_type = match.groups()
                    
                    # Clean up client IP
                    client_ip = client_ip.replace('@', '').split('#')[0]
                    
                    # Parse timestamp
                    timestamp = self._parse_timestamp(timestamp_str)
                    
                    query = {
                        'timestamp': timestamp,
                        'client_ip': client_ip,
                        'domain': domain,
                        'query_type': query_type,
                        'raw_line': line.strip()
                    }
                    
                    # Update statistics
                    self.query_stats[query_type] += 1
                    
                    return query
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing query line: {e}")
            return None
    
    def _parse_timestamp(self, timestamp_str):
        """Parse timestamp from log line"""
        try:
            # Try different timestamp formats
            formats = [
                '%d-%b-%Y %H:%M:%S.%f',
                '%b %d %H:%M:%S',
                '%Y-%m-%d %H:%M:%S'
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(timestamp_str, fmt)
                    # Add current year for formats without year
                    if dt.year == 1900:
                        dt = dt.replace(year=datetime.now().year)
                    return dt.isoformat()
                except ValueError:
                    continue
            
            # If all formats fail, return current time
            return datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"Error parsing timestamp: {e}")
            return datetime.now().isoformat()
    
    def _calculate_query_stats(self):
        """Calculate query statistics"""
        try:
            total_queries = len(self.query_history)
            
            # Calculate QPS (queries per second) over last minute
            now = datetime.now()
            one_minute_ago = now - timedelta(minutes=1)
            
            recent_queries = 0
            for query in self.query_history:
                try:
                    query_time = datetime.fromisoformat(query['timestamp'])
                    if query_time >= one_minute_ago:
                        recent_queries += 1
                except:
                    continue
            
            qps = recent_queries / 60.0
            
            # Calculate hourly stats
            one_hour_ago = now - timedelta(hours=1)
            hourly_queries = 0
            for query in self.query_history:
                try:
                    query_time = datetime.fromisoformat(query['timestamp'])
                    if query_time >= one_hour_ago:
                        hourly_queries += 1
                except:
                    continue
            
            return {
                'total_queries': total_queries,
                'qps': round(qps, 2),
                'queries_per_minute': recent_queries,
                'queries_per_hour': hourly_queries
            }
            
        except Exception as e:
            logger.error(f"Error calculating query stats: {e}")
            return {'total_queries': 0, 'qps': 0, 'queries_per_minute': 0, 'queries_per_hour': 0}
    
    def _get_response_time_stats(self):
        """Get response time statistics"""
        try:
            if not self.response_times:
                return {'average': 0, 'min': 0, 'max': 0}
            
            times = list(self.response_times)
            return {
                'average': round(sum(times) / len(times), 2),
                'min': round(min(times), 2),
                'max': round(max(times), 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting response time stats: {e}")
            return {'average': 0, 'min': 0, 'max': 0}
    
    def _get_query_type_distribution(self):
        """Get distribution of query types"""
        try:
            total = sum(self.query_stats.values())
            if total == 0:
                return {}
            
            distribution = {}
            for query_type, count in self.query_stats.items():
                distribution[query_type] = {
                    'count': count,
                    'percentage': round((count / total) * 100, 2)
                }
            
            return distribution
            
        except Exception as e:
            logger.error(f"Error getting query type distribution: {e}")
            return {}
    
    def _get_top_domains(self, limit=10):
        """Get top queried domains"""
        try:
            domain_counts = defaultdict(int)
            
            for query in self.query_history:
                domain = query.get('domain', '')
                if domain:
                    domain_counts[domain] += 1
            
            # Sort by count and return top domains
            sorted_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)
            return [{'domain': domain, 'count': count} for domain, count in sorted_domains[:limit]]
            
        except Exception as e:
            logger.error(f"Error getting top domains: {e}")
            return []
    
    def _get_service_health(self):
        """Get overall DNS service health"""
        try:
            bind_status = self._get_bind_status()
            
            health = {
                'status': 'healthy',
                'issues': []
            }
            
            # Check if service is running
            if not bind_status.get('process_running', False):
                health['status'] = 'critical'
                health['issues'].append('BIND9 process is not running')
            
            # Check configuration
            config_status = bind_status.get('config_status', {})
            if not config_status.get('valid', True):
                health['status'] = 'warning'
                health['issues'].append('Configuration issues detected')
            
            # Check query load
            stats = self._calculate_query_stats()
            if stats.get('qps', 0) > 100:  # High load threshold
                health['status'] = 'warning'
                health['issues'].append(f"High query load: {stats['qps']} QPS")
            
            return health
            
        except Exception as e:
            logger.error(f"Error getting service health: {e}")
            return {'status': 'error', 'issues': [str(e)]}
    
    def get_recent_queries(self, limit=100):
        """Get recent DNS queries"""
        try:
            queries = list(self.query_history)
            queries.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            return queries[:limit]
        except Exception as e:
            logger.error(f"Error getting recent queries: {e}")
            return []