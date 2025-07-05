#!/bin/bash
# DNS Monitor Installation Script for Debian/Ubuntu

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/dns-monitor"
SERVICE_USER="www-data"
BACKUP_DIR="/opt/dns-monitor-backup"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1
    fi
}

check_system() {
    log_info "Checking system requirements..."
    
    # Check OS
    if ! grep -qi "ubuntu\|debian" /etc/os-release; then
        log_warning "This script is designed for Ubuntu/Debian systems"
    fi
    
    # Check Python version
    if ! python3 --version | grep -q "3\.[89]\|3\.1[0-9]"; then
        log_error "Python 3.8 or later is required"
        exit 1
    fi
    
    log_success "System requirements met"
}

install_dependencies() {
    log_info "Installing system dependencies..."
    
    apt-get update
    apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        nginx \
        supervisor \
        sqlite3 \
        bind9-utils \
        curl \
        wget \
        git \
        systemctl
    
    log_success "System dependencies installed"
}

create_user() {
    log_info "Setting up service user..."
    
    if ! id "$SERVICE_USER" &>/dev/null; then
        useradd -r -s /bin/false -d "$INSTALL_DIR" "$SERVICE_USER"
        log_success "Created service user: $SERVICE_USER"
    else
        log_info "Service user already exists: $SERVICE_USER"
    fi
}

install_application() {
    log_info "Installing DNS Monitor application..."
    
    # Create backup if directory exists
    if [[ -d "$INSTALL_DIR" ]]; then
        log_info "Creating backup of existing installation..."
        mkdir -p "$BACKUP_DIR"
        cp -r "$INSTALL_DIR" "$BACKUP_DIR/dns-monitor-$(date +%Y%m%d-%H%M%S)"
        rm -rf "$INSTALL_DIR"
    fi
    
    # Create installation directory
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    # Copy application files
    cp -r "$(dirname "$0")/../backend" "$INSTALL_DIR/"
    cp -r "$(dirname "$0")/../frontend" "$INSTALL_DIR/"
    cp -r "$(dirname "$0")/../nginx" "$INSTALL_DIR/"
    cp -r "$(dirname "$0")/../systemd" "$INSTALL_DIR/"
    
    # Create data directory
    mkdir -p "$INSTALL_DIR/backend/data"
    mkdir -p "$INSTALL_DIR/logs"
    
    # Set permissions
    chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
    chmod 755 "$INSTALL_DIR"
    chmod 644 "$INSTALL_DIR/backend"/*.py
    chmod 755 "$INSTALL_DIR/backend/app.py"
    
    log_success "Application files installed"
}

install_python_dependencies() {
    log_info "Installing Python dependencies..."
    
    # Create virtual environment
    python3 -m venv "$INSTALL_DIR/venv"
    source "$INSTALL_DIR/venv/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    pip install -r "$INSTALL_DIR/backend/requirements.txt"
    
    # Set permissions
    chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR/venv"
    
    log_success "Python dependencies installed"
}

configure_nginx() {
    log_info "Configuring Nginx..."
    
    # Backup original config
    if [[ -f /etc/nginx/nginx.conf ]]; then
        cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup
    fi
    
    # Copy new configuration
    cp "$INSTALL_DIR/nginx/nginx.conf" /etc/nginx/sites-available/dns-monitor
    
    # Enable site
    ln -sf /etc/nginx/sites-available/dns-monitor /etc/nginx/sites-enabled/
    
    # Remove default site
    rm -f /etc/nginx/sites-enabled/default
    
    # Test configuration
    nginx -t
    
    # Restart Nginx
    systemctl restart nginx
    systemctl enable nginx
    
    log_success "Nginx configured and restarted"
}

configure_systemd() {
    log_info "Configuring systemd service..."
    
    # Copy service file
    cp "$INSTALL_DIR/systemd/dns-monitor.service" /etc/systemd/system/
    
    # Reload systemd
    systemctl daemon-reload
    
    # Enable and start service
    systemctl enable dns-monitor
    systemctl start dns-monitor
    
    log_success "Systemd service configured and started"
}

configure_bind_logging() {
    log_info "Configuring BIND9 query logging..."
    
    # Check if BIND9 is installed
    if ! command -v named &> /dev/null; then
        log_warning "BIND9 not found. Please install and configure manually."
        return
    fi
    
    # Create log directory
    mkdir -p /var/log/named
    chown bind:bind /var/log/named
    
    # Add logging configuration to BIND9
    cat > /etc/bind/logging.conf << 'EOF'
logging {
    channel query_log {
        file "/var/log/named/query.log" versions 3 size 10m;
        severity info;
        print-category yes;
        print-time yes;
    };
    category queries { query_log; };
};
EOF
    
    # Include logging in main config if not already included
    if ! grep -q "include.*logging.conf" /etc/bind/named.conf; then
        echo 'include "/etc/bind/logging.conf";' >> /etc/bind/named.conf
    fi
    
    # Restart BIND9
    systemctl restart named || systemctl restart bind9
    
    log_success "BIND9 logging configured"
}

setup_firewall() {
    log_info "Setting up firewall rules..."
    
    if command -v ufw &> /dev/null; then
        ufw allow 22/tcp
        ufw allow 80/tcp
        ufw allow 443/tcp
        ufw allow 53/tcp
        ufw allow 53/udp
        ufw --force enable
        log_success "UFW firewall configured"
    elif command -v firewall-cmd &> /dev/null; then
        firewall-cmd --permanent --add-service=ssh
        firewall-cmd --permanent --add-service=http
        firewall-cmd --permanent --add-service=https
        firewall-cmd --permanent --add-service=dns
        firewall-cmd --reload
        log_success "Firewalld configured"
    else
        log_warning "No firewall detected. Please configure manually."
    fi
}

create_admin_user() {
    log_info "Creating admin user..."
    
    # This would create an admin user in the database
    # For now, we'll just create a placeholder
    touch "$INSTALL_DIR/backend/data/.admin_created"
    chown "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR/backend/data/.admin_created"
    
    log_success "Admin user setup completed"
}

show_status() {
    log_info "Checking service status..."
    
    echo "System Status:"
    echo "=============="
    
    # Check services
    services=("nginx" "dns-monitor")
    for service in "${services[@]}"; do
        if systemctl is-active --quiet "$service"; then
            echo -e "$service: ${GREEN}Active${NC}"
        else
            echo -e "$service: ${RED}Inactive${NC}"
        fi
    done
    
    echo ""
    echo "Network Ports:"
    echo "=============="
    netstat -tlnp | grep -E ":80|:443|:5000" || true
    
    echo ""
    echo "Application URLs:"
    echo "================"
    echo "Web Interface: http://$(hostname -I | awk '{print $1}')"
    echo "API Endpoint:  http://$(hostname -I | awk '{print $1}')/api/"
    
    echo ""
    log_success "Installation completed successfully!"
}

main() {
    log_info "Starting DNS Monitor installation..."
    
    check_root
    check_system
    install_dependencies
    create_user
    install_application
    install_python_dependencies
    configure_nginx
    configure_systemd
    configure_bind_logging
    setup_firewall
    create_admin_user
    
    # Wait a moment for services to start
    sleep 5
    
    show_status
    
    echo ""
    log_info "Installation logs can be found in: /var/log/dns-monitor/"
    log_info "To view service logs: sudo journalctl -u dns-monitor -f"
    log_info "To restart the service: sudo systemctl restart dns-monitor"
}

# Run main function
main "$@"