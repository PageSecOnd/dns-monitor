# API Documentation

## Base URL

```
http://localhost:5000/api
```

## Authentication

Currently, the API does not require authentication. In production, you should implement proper authentication mechanisms.

## Response Format

All API responses are in JSON format with the following structure:

```json
{
  "timestamp": "2024-01-01T12:00:00.000Z",
  "data": { ... },
  "status": "success|error",
  "message": "Optional message"
}
```

## System Monitoring Endpoints

### Get Current System Statistics

```http
GET /api/system/stats
```

Returns real-time system monitoring data including CPU, memory, disk, network, and load information.

**Response Example:**

```json
{
  "timestamp": "2024-01-01T12:00:00.000Z",
  "cpu": {
    "percent": 25.4,
    "count": 4,
    "frequency": {
      "current": 2400.0,
      "min": 1200.0,
      "max": 3600.0
    }
  },
  "memory": {
    "total": 8589934592,
    "available": 6442450944,
    "used": 2147483648,
    "free": 6442450944,
    "percent": 25.0,
    "buffers": 134217728,
    "cached": 1073741824
  },
  "disk": {
    "total": 107374182400,
    "used": 53687091200,
    "free": 53687091200,
    "percent": 50.0,
    "io": {
      "read_bytes": 1048576000,
      "write_bytes": 524288000,
      "read_count": 10000,
      "write_count": 5000
    }
  },
  "network": {
    "bytes_sent": 104857600,
    "bytes_recv": 524288000,
    "packets_sent": 100000,
    "packets_recv": 200000,
    "speed": {
      "upload": 1024.0,
      "download": 5120.0
    },
    "interfaces": {
      "eth0": {
        "addresses": [...],
        "stats": {...}
      }
    }
  },
  "load_average": {
    "1min": 0.5,
    "5min": 0.3,
    "15min": 0.2
  },
  "uptime": {
    "seconds": 86400,
    "boot_time": 1704067200
  },
  "processes": [...]
}
```

### Get System History

```http
GET /api/history/system?hours=24
```

Returns historical system monitoring data for the specified time period.

**Parameters:**
- `hours` (optional): Number of hours to retrieve (default: 24)

**Response Example:**

```json
[
  {
    "timestamp": "2024-01-01T11:00:00.000Z",
    "cpu_percent": 20.5,
    "memory_percent": 30.2,
    "disk_percent": 45.8,
    "load_avg_1min": 0.8,
    "network_upload_speed": 1500.0,
    "network_download_speed": 8000.0,
    "uptime": 86400
  },
  ...
]
```

## DNS Monitoring Endpoints

### Get Current DNS Statistics

```http
GET /api/dns/stats
```

Returns comprehensive DNS monitoring data including BIND9 status, query statistics, and recent queries.

**Response Example:**

```json
{
  "timestamp": "2024-01-01T12:00:00.000Z",
  "bind_status": {
    "process_running": true,
    "service_status": {
      "active": true,
      "status": "active"
    },
    "config_status": {
      "valid": true,
      "errors": null
    },
    "process_info": {
      "pid": "1234",
      "ppid": "1",
      "cpu_percent": "0.5",
      "memory_percent": "2.1",
      "command": "/usr/sbin/named -f -u bind"
    },
    "version": "BIND 9.16.1-Ubuntu"
  },
  "query_stats": {
    "total_queries": 15420,
    "qps": 12.5,
    "queries_per_minute": 750,
    "queries_per_hour": 45000
  },
  "response_times": {
    "average": 5.2,
    "min": 0.8,
    "max": 45.6
  },
  "query_types": {
    "A": {
      "count": 8500,
      "percentage": 55.1
    },
    "AAAA": {
      "count": 3200,
      "percentage": 20.8
    },
    "MX": {
      "count": 1500,
      "percentage": 9.7
    },
    "CNAME": {
      "count": 1200,
      "percentage": 7.8
    },
    "TXT": {
      "count": 800,
      "percentage": 5.2
    },
    "NS": {
      "count": 150,
      "percentage": 1.0
    },
    "SOA": {
      "count": 50,
      "percentage": 0.3
    },
    "PTR": {
      "count": 20,
      "percentage": 0.1
    }
  },
  "top_domains": [
    {
      "domain": "example.com",
      "count": 2500
    },
    {
      "domain": "google.com",
      "count": 1800
    },
    ...
  ],
  "recent_queries": [...],
  "service_health": {
    "status": "healthy",
    "issues": []
  }
}
```

### Get Recent DNS Queries

```http
GET /api/dns/queries?limit=100
```

Returns a list of recent DNS queries with detailed information.

**Parameters:**
- `limit` (optional): Number of queries to retrieve (default: 100, max: 1000)

**Response Example:**

```json
[
  {
    "timestamp": "2024-01-01T12:00:00.000Z",
    "client_ip": "192.168.1.100",
    "domain": "example.com",
    "query_type": "A",
    "response_time": 5.2,
    "raw_line": "01-Jan-2024 12:00:00.000 client @0x7f8b8c000000 192.168.1.100#12345 (example.com): query: example.com IN A + (192.168.1.1)"
  },
  ...
]
```

### Get DNS History

```http
GET /api/history/dns?hours=24
```

Returns historical DNS monitoring data for the specified time period.

**Parameters:**
- `hours` (optional): Number of hours to retrieve (default: 24)

**Response Example:**

```json
[
  {
    "timestamp": "2024-01-01T11:00:00.000Z",
    "bind_running": true,
    "service_active": true,
    "total_queries": 14500,
    "qps": 10.8,
    "queries_per_minute": 648,
    "queries_per_hour": 38880,
    "avg_response_time": 4.8,
    "config_valid": true
  },
  ...
]
```

## WebSocket Events

The application uses WebSocket for real-time updates. Connect to:

```
ws://localhost:5000/socket.io/
```

### Events

#### Client to Server

- `connect` - Establish connection
- `request_current_data` - Request current monitoring data
- `pause_updates` - Pause real-time updates
- `resume_updates` - Resume real-time updates

#### Server to Client

- `status` - Connection status message
- `monitoring_data` - Real-time monitoring data
- `dns_query` - New DNS query notification
- `system_alert` - System alert notification
- `error` - Error message

### Example WebSocket Usage

```javascript
const socket = io('http://localhost:5000');

socket.on('connect', () => {
    console.log('Connected to DNS Monitor');
    socket.emit('request_current_data');
});

socket.on('monitoring_data', (data) => {
    console.log('Received monitoring data:', data);
    updateUI(data);
});

socket.on('dns_query', (query) => {
    console.log('New DNS query:', query);
    addQueryToTable(query);
});

socket.on('system_alert', (alert) => {
    console.log('System alert:', alert);
    showNotification(alert);
});
```

## Error Handling

### HTTP Status Codes

- `200` - Success
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

### Error Response Format

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### Common Error Codes

- `BIND_NOT_RUNNING` - BIND9 service is not running
- `LOG_FILE_NOT_FOUND` - DNS log file not accessible
- `DATABASE_ERROR` - Database operation failed
- `PERMISSION_DENIED` - Insufficient permissions
- `INVALID_PARAMETER` - Invalid request parameter

## Rate Limiting

API endpoints are rate-limited to prevent abuse:

- System endpoints: 60 requests per minute
- DNS endpoints: 120 requests per minute
- WebSocket connections: 10 per IP address

## Caching

Some responses are cached to improve performance:

- System statistics: 5 seconds
- DNS statistics: 10 seconds
- Historical data: 1 minute

## Data Retention

Historical data is automatically cleaned up:

- System monitoring data: 30 days
- DNS query logs: 7 days
- Error logs: 14 days

## Security Considerations

### Input Validation

All API inputs are validated and sanitized to prevent:
- SQL injection
- XSS attacks
- Path traversal
- Command injection

### HTTPS

In production, always use HTTPS:

```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/private.key;
    ...
}
```

### API Key Authentication (Future Enhancement)

```http
GET /api/system/stats
Authorization: Bearer YOUR_API_KEY
```

## Example Implementations

### Python

```python
import requests

# Get system stats
response = requests.get('http://localhost:5000/api/system/stats')
data = response.json()
print(f"CPU Usage: {data['cpu']['percent']}%")

# Get DNS queries
response = requests.get('http://localhost:5000/api/dns/queries?limit=10')
queries = response.json()
for query in queries:
    print(f"{query['timestamp']}: {query['domain']} ({query['query_type']})")
```

### JavaScript (Fetch)

```javascript
// Get system stats
fetch('/api/system/stats')
  .then(response => response.json())
  .then(data => {
    console.log(`CPU Usage: ${data.cpu.percent}%`);
  });

// Get DNS queries
fetch('/api/dns/queries?limit=10')
  .then(response => response.json())
  .then(queries => {
    queries.forEach(query => {
      console.log(`${query.timestamp}: ${query.domain} (${query.query_type})`);
    });
  });
```

### cURL

```bash
# Get system stats
curl -X GET http://localhost:5000/api/system/stats

# Get DNS queries with limit
curl -X GET "http://localhost:5000/api/dns/queries?limit=50"

# Get system history for last 12 hours
curl -X GET "http://localhost:5000/api/history/system?hours=12"
```

This API documentation provides comprehensive information for integrating with the DNS Monitor system. The API is designed to be RESTful, well-documented, and easy to use for both web interfaces and external applications.