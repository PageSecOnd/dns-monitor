# Multi-stage build for optimized image size
FROM python:3.11-slim as builder

# Build arguments for mirror selection
ARG APT_MIRROR=mirrors.aliyun.com
ARG PIP_MIRROR=mirrors.aliyun.com
ARG USE_CHINA_MIRRORS=true

# Configure Chinese mirror sources for faster package installation
RUN if [ "$USE_CHINA_MIRRORS" = "true" ]; then \
    # Check if sources.list exists, if not create it
    if [ ! -f /etc/apt/sources.list ]; then \
        # For newer Debian versions that use DEB822 format
        if [ -d /etc/apt/sources.list.d ]; then \
            echo "deb https://$APT_MIRROR/debian/ bookworm main" > /etc/apt/sources.list && \
            echo "deb https://$APT_MIRROR/debian/ bookworm-updates main" >> /etc/apt/sources.list && \
            echo "deb https://$APT_MIRROR/debian-security/ bookworm-security main" >> /etc/apt/sources.list; \
        fi; \
    else \
        # Backup original sources
        cp /etc/apt/sources.list /etc/apt/sources.list.bak && \
        # Replace with Chinese mirror sources
        sed -i "s/deb.debian.org/$APT_MIRROR/g" /etc/apt/sources.list && \
        sed -i "s/security.debian.org/$APT_MIRROR/g" /etc/apt/sources.list && \
        sed -i "s|http://|https://|g" /etc/apt/sources.list; \
    fi; \
    fi

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Configure pip to use Chinese mirror sources
RUN if [ "$USE_CHINA_MIRRORS" = "true" ]; then \
    mkdir -p /root/.pip && \
    echo "[global]" > /root/.pip/pip.conf && \
    echo "index-url = https://$PIP_MIRROR/pypi/simple/" >> /root/.pip/pip.conf && \
    echo "trusted-host = $PIP_MIRROR" >> /root/.pip/pip.conf && \
    echo "timeout = 60" >> /root/.pip/pip.conf && \
    echo "retries = 5" >> /root/.pip/pip.conf; \
    fi

# Copy requirements and install Python dependencies
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Production stage
FROM python:3.11-slim

LABEL maintainer="DNS Monitor Team"
LABEL description="DNS Server Monitoring System"

# Build arguments for mirror selection
ARG APT_MIRROR=mirrors.aliyun.com
ARG USE_CHINA_MIRRORS=true

# Set working directory
WORKDIR /app

# Configure Chinese mirror sources for faster package installation
RUN if [ "$USE_CHINA_MIRRORS" = "true" ]; then \
    # Check if sources.list exists, if not create it
    if [ ! -f /etc/apt/sources.list ]; then \
        # For newer Debian versions that use DEB822 format
        if [ -d /etc/apt/sources.list.d ]; then \
            echo "deb https://$APT_MIRROR/debian/ bookworm main" > /etc/apt/sources.list && \
            echo "deb https://$APT_MIRROR/debian/ bookworm-updates main" >> /etc/apt/sources.list && \
            echo "deb https://$APT_MIRROR/debian-security/ bookworm-security main" >> /etc/apt/sources.list; \
        fi; \
    else \
        # Backup original sources
        cp /etc/apt/sources.list /etc/apt/sources.list.bak && \
        # Replace with Chinese mirror sources
        sed -i "s/deb.debian.org/$APT_MIRROR/g" /etc/apt/sources.list && \
        sed -i "s/security.debian.org/$APT_MIRROR/g" /etc/apt/sources.list && \
        sed -i "s|http://|https://|g" /etc/apt/sources.list; \
    fi; \
    fi

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    nginx \
    supervisor \
    bind9-utils \
    procps \
    net-tools \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

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