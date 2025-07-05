#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DNS Monitor Backend Application
Modern DNS server monitoring system with real-time system and BIND9 monitoring
"""

import os
import sys
import sqlite3
import json
import time
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import psutil
import threading
import logging
from pathlib import Path

# Add monitors directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'monitors'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from system_monitor import SystemMonitor
from dns_monitor import DNSMonitor
from database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
            static_folder='../frontend',
            template_folder='../frontend')
app.config['SECRET_KEY'] = 'dns-monitor-secret-key-2024'

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Initialize monitors
system_monitor = SystemMonitor()
dns_monitor = DNSMonitor()
db_manager = DatabaseManager()

class DNSMonitorApp:
    def __init__(self):
        self.running = False
        self.monitoring_thread = None
        
    def start_monitoring(self):
        """Start the monitoring thread"""
        self.running = True
        self.monitoring_thread = threading.Thread(target=self._monitor_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        logger.info("Monitoring started")
        
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        logger.info("Monitoring stopped")
        
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Collect system data
                system_data = system_monitor.get_system_stats()
                
                # Collect DNS data
                dns_data = dns_monitor.get_dns_stats()
                
                # Combine data
                monitoring_data = {
                    'timestamp': datetime.now().isoformat(),
                    'system': system_data,
                    'dns': dns_data
                }
                
                # Store in database
                db_manager.store_monitoring_data(monitoring_data)
                
                # Emit to connected clients
                socketio.emit('monitoring_data', monitoring_data)
                
                # Wait before next iteration
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)

# Initialize app
monitor_app = DNSMonitorApp()

@app.route('/')
def index():
    """Main monitoring page"""
    return render_template('index.html')

@app.route('/api/system/stats')
def get_system_stats():
    """Get current system statistics"""
    try:
        return jsonify(system_monitor.get_system_stats())
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dns/stats')
def get_dns_stats():
    """Get current DNS statistics"""
    try:
        return jsonify(dns_monitor.get_dns_stats())
    except Exception as e:
        logger.error(f"Error getting DNS stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dns/queries')
def get_dns_queries():
    """Get recent DNS queries"""
    try:
        limit = request.args.get('limit', 100, type=int)
        return jsonify(dns_monitor.get_recent_queries(limit))
    except Exception as e:
        logger.error(f"Error getting DNS queries: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/system')
def get_system_history():
    """Get system monitoring history"""
    try:
        hours = request.args.get('hours', 24, type=int)
        return jsonify(db_manager.get_system_history(hours))
    except Exception as e:
        logger.error(f"Error getting system history: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/dns')
def get_dns_history():
    """Get DNS monitoring history"""
    try:
        hours = request.args.get('hours', 24, type=int)
        return jsonify(db_manager.get_dns_history(hours))
    except Exception as e:
        logger.error(f"Error getting DNS history: {e}")
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('status', {'message': 'Connected to DNS Monitor'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('request_current_data')
def handle_current_data_request():
    """Handle request for current monitoring data"""
    try:
        system_data = system_monitor.get_system_stats()
        dns_data = dns_monitor.get_dns_stats()
        
        monitoring_data = {
            'timestamp': datetime.now().isoformat(),
            'system': system_data,
            'dns': dns_data
        }
        
        emit('monitoring_data', monitoring_data)
    except Exception as e:
        logger.error(f"Error handling current data request: {e}")
        emit('error', {'message': str(e)})

if __name__ == '__main__':
    try:
        # Initialize database
        db_manager.init_database()
        
        # Start monitoring
        monitor_app.start_monitoring()
        
        # Start Flask app
        logger.info("Starting DNS Monitor server...")
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
        
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        monitor_app.stop_monitoring()
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)