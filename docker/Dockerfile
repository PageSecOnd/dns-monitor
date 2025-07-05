FROM python:3.11-slim

LABEL maintainer="DNS Monitor Team"
LABEL description="DNS Server Monitoring System"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    nginx \
    supervisor \
    bind9-utils \
    procps \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/
COPY nginx/ /app/nginx/
COPY scripts/ /app/scripts/

# Create necessary directories
RUN mkdir -p /app/backend/data \
    /app/logs \
    /var/log/supervisor

# Copy configuration files
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY docker/nginx.conf /etc/nginx/nginx.conf

# Set permissions
RUN chmod +x /app/scripts/*.sh
RUN chown -R www-data:www-data /app/frontend
RUN chown -R www-data:www-data /app/logs

# Create non-root user
RUN useradd -m -u 1000 dnsmonitor && \
    chown -R dnsmonitor:dnsmonitor /app

# Expose ports
EXPOSE 80 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/ || exit 1

# Use supervisor to manage processes
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]