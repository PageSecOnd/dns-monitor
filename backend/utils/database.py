#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Manager Module
Handles SQLite database operations for storing historical monitoring data
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / 'data' / 'dns_monitor.db'
        
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
    def init_database(self):
        """Initialize the database with required tables"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Create system monitoring table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_monitoring (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    cpu_percent REAL,
                    memory_percent REAL,
                    memory_used INTEGER,
                    memory_total INTEGER,
                    disk_percent REAL,
                    disk_used INTEGER,
                    disk_total INTEGER,
                    load_avg_1min REAL,
                    load_avg_5min REAL,
                    load_avg_15min REAL,
                    network_bytes_sent INTEGER,
                    network_bytes_recv INTEGER,
                    network_upload_speed REAL,
                    network_download_speed REAL,
                    uptime REAL,
                    raw_data TEXT
                )
            ''')
            
            # Create DNS monitoring table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dns_monitoring (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    bind_running BOOLEAN,
                    service_active BOOLEAN,
                    total_queries INTEGER,
                    qps REAL,
                    queries_per_minute INTEGER,
                    queries_per_hour INTEGER,
                    avg_response_time REAL,
                    config_valid BOOLEAN,
                    raw_data TEXT
                )
            ''')
            
            # Create DNS queries table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dns_queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    client_ip TEXT,
                    domain TEXT,
                    query_type TEXT,
                    response_time REAL,
                    raw_line TEXT
                )
            ''')
            
            # Create query statistics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS query_statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    query_type TEXT,
                    count INTEGER,
                    percentage REAL
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_system_timestamp ON system_monitoring(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_dns_timestamp ON dns_monitoring(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_queries_timestamp ON dns_queries(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_queries_domain ON dns_queries(domain)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_queries_type ON dns_queries(query_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_queries_client ON dns_queries(client_ip)')
            
            conn.commit()
            conn.close()
            
            logger.info(f"Database initialized successfully at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def store_monitoring_data(self, monitoring_data):
        """Store monitoring data in the database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            timestamp = monitoring_data.get('timestamp', datetime.now().isoformat())
            
            # Store system data
            system_data = monitoring_data.get('system', {})
            if system_data:
                cursor.execute('''
                    INSERT INTO system_monitoring (
                        timestamp, cpu_percent, memory_percent, memory_used, memory_total,
                        disk_percent, disk_used, disk_total, load_avg_1min, load_avg_5min,
                        load_avg_15min, network_bytes_sent, network_bytes_recv,
                        network_upload_speed, network_download_speed, uptime, raw_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    timestamp,
                    system_data.get('cpu', {}).get('percent', 0),
                    system_data.get('memory', {}).get('percent', 0),
                    system_data.get('memory', {}).get('used', 0),
                    system_data.get('memory', {}).get('total', 0),
                    system_data.get('disk', {}).get('percent', 0),
                    system_data.get('disk', {}).get('used', 0),
                    system_data.get('disk', {}).get('total', 0),
                    system_data.get('load_average', {}).get('1min', 0),
                    system_data.get('load_average', {}).get('5min', 0),
                    system_data.get('load_average', {}).get('15min', 0),
                    system_data.get('network', {}).get('bytes_sent', 0),
                    system_data.get('network', {}).get('bytes_recv', 0),
                    system_data.get('network', {}).get('speed', {}).get('upload', 0),
                    system_data.get('network', {}).get('speed', {}).get('download', 0),
                    system_data.get('uptime', {}).get('seconds', 0),
                    json.dumps(system_data)
                ))
            
            # Store DNS data
            dns_data = monitoring_data.get('dns', {})
            if dns_data:
                bind_status = dns_data.get('bind_status', {})
                query_stats = dns_data.get('query_stats', {})
                response_times = dns_data.get('response_times', {})
                
                cursor.execute('''
                    INSERT INTO dns_monitoring (
                        timestamp, bind_running, service_active, total_queries, qps,
                        queries_per_minute, queries_per_hour, avg_response_time,
                        config_valid, raw_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    timestamp,
                    bind_status.get('process_running', False),
                    bind_status.get('service_status', {}).get('active', False),
                    query_stats.get('total_queries', 0),
                    query_stats.get('qps', 0),
                    query_stats.get('queries_per_minute', 0),
                    query_stats.get('queries_per_hour', 0),
                    response_times.get('average', 0),
                    bind_status.get('config_status', {}).get('valid', True),
                    json.dumps(dns_data)
                ))
                
                # Store recent queries
                recent_queries = dns_data.get('recent_queries', [])
                for query in recent_queries:
                    cursor.execute('''
                        INSERT INTO dns_queries (
                            timestamp, client_ip, domain, query_type, response_time, raw_line
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        query.get('timestamp', timestamp),
                        query.get('client_ip', ''),
                        query.get('domain', ''),
                        query.get('query_type', ''),
                        query.get('response_time', 0),
                        query.get('raw_line', '')
                    ))
                
                # Store query type statistics
                query_types = dns_data.get('query_types', {})
                for query_type, stats in query_types.items():
                    cursor.execute('''
                        INSERT INTO query_statistics (
                            timestamp, query_type, count, percentage
                        ) VALUES (?, ?, ?, ?)
                    ''', (
                        timestamp,
                        query_type,
                        stats.get('count', 0),
                        stats.get('percentage', 0)
                    ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing monitoring data: {e}")
            if conn:
                conn.close()
    
    def get_system_history(self, hours=24):
        """Get system monitoring history"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            start_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            cursor.execute('''
                SELECT timestamp, cpu_percent, memory_percent, disk_percent,
                       load_avg_1min, network_upload_speed, network_download_speed,
                       uptime
                FROM system_monitoring
                WHERE timestamp >= ?
                ORDER BY timestamp
            ''', (start_time,))
            
            results = cursor.fetchall()
            conn.close()
            
            # Format results
            history = []
            for row in results:
                history.append({
                    'timestamp': row[0],
                    'cpu_percent': row[1],
                    'memory_percent': row[2],
                    'disk_percent': row[3],
                    'load_avg_1min': row[4],
                    'network_upload_speed': row[5],
                    'network_download_speed': row[6],
                    'uptime': row[7]
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting system history: {e}")
            return []
    
    def get_dns_history(self, hours=24):
        """Get DNS monitoring history"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            start_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            cursor.execute('''
                SELECT timestamp, bind_running, service_active, total_queries,
                       qps, queries_per_minute, queries_per_hour, avg_response_time,
                       config_valid
                FROM dns_monitoring
                WHERE timestamp >= ?
                ORDER BY timestamp
            ''', (start_time,))
            
            results = cursor.fetchall()
            conn.close()
            
            # Format results
            history = []
            for row in results:
                history.append({
                    'timestamp': row[0],
                    'bind_running': row[1],
                    'service_active': row[2],
                    'total_queries': row[3],
                    'qps': row[4],
                    'queries_per_minute': row[5],
                    'queries_per_hour': row[6],
                    'avg_response_time': row[7],
                    'config_valid': row[8]
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting DNS history: {e}")
            return []
    
    def get_query_history(self, hours=24, limit=1000):
        """Get DNS query history"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            start_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            cursor.execute('''
                SELECT timestamp, client_ip, domain, query_type, response_time
                FROM dns_queries
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (start_time, limit))
            
            results = cursor.fetchall()
            conn.close()
            
            # Format results
            history = []
            for row in results:
                history.append({
                    'timestamp': row[0],
                    'client_ip': row[1],
                    'domain': row[2],
                    'query_type': row[3],
                    'response_time': row[4]
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting query history: {e}")
            return []
    
    def get_top_domains(self, hours=24, limit=10):
        """Get top queried domains"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            start_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            cursor.execute('''
                SELECT domain, COUNT(*) as count
                FROM dns_queries
                WHERE timestamp >= ? AND domain != ''
                GROUP BY domain
                ORDER BY count DESC
                LIMIT ?
            ''', (start_time, limit))
            
            results = cursor.fetchall()
            conn.close()
            
            # Format results
            top_domains = []
            for row in results:
                top_domains.append({
                    'domain': row[0],
                    'count': row[1]
                })
            
            return top_domains
            
        except Exception as e:
            logger.error(f"Error getting top domains: {e}")
            return []
    
    def get_query_type_stats(self, hours=24):
        """Get query type statistics"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            start_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            cursor.execute('''
                SELECT query_type, COUNT(*) as count
                FROM dns_queries
                WHERE timestamp >= ? AND query_type != ''
                GROUP BY query_type
                ORDER BY count DESC
            ''', (start_time,))
            
            results = cursor.fetchall()
            conn.close()
            
            # Calculate percentages
            total = sum(row[1] for row in results)
            stats = {}
            
            for row in results:
                query_type, count = row
                stats[query_type] = {
                    'count': count,
                    'percentage': round((count / total) * 100, 2) if total > 0 else 0
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting query type stats: {e}")
            return {}
    
    def cleanup_old_data(self, days=30):
        """Clean up old monitoring data"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cutoff_time = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Clean up old system monitoring data
            cursor.execute('DELETE FROM system_monitoring WHERE timestamp < ?', (cutoff_time,))
            
            # Clean up old DNS monitoring data
            cursor.execute('DELETE FROM dns_monitoring WHERE timestamp < ?', (cutoff_time,))
            
            # Clean up old DNS queries (keep more recent data)
            query_cutoff = (datetime.now() - timedelta(days=7)).isoformat()
            cursor.execute('DELETE FROM dns_queries WHERE timestamp < ?', (query_cutoff,))
            
            # Clean up old query statistics
            cursor.execute('DELETE FROM query_statistics WHERE timestamp < ?', (cutoff_time,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Cleaned up data older than {days} days")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    def get_database_stats(self):
        """Get database statistics"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            stats = {}
            
            # Get table row counts
            tables = ['system_monitoring', 'dns_monitoring', 'dns_queries', 'query_statistics']
            for table in tables:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                stats[f'{table}_count'] = cursor.fetchone()[0]
            
            # Get database size
            cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
            stats['database_size'] = cursor.fetchone()[0]
            
            # Get oldest and newest timestamps
            cursor.execute('SELECT MIN(timestamp), MAX(timestamp) FROM system_monitoring')
            result = cursor.fetchone()
            stats['oldest_system_data'] = result[0]
            stats['newest_system_data'] = result[1]
            
            cursor.execute('SELECT MIN(timestamp), MAX(timestamp) FROM dns_queries')
            result = cursor.fetchone()
            stats['oldest_query_data'] = result[0]
            stats['newest_query_data'] = result[1]
            
            conn.close()
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}