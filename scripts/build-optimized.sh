#!/bin/bash
# DNS Monitor Optimized Build Script
# Automatically selects the fastest Chinese mirror source for Docker build

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Mirror sources configuration
declare -A APT_MIRRORS
APT_MIRRORS=(
    ["aliyun"]="mirrors.aliyun.com"
    ["tencent"]="mirrors.cloud.tencent.com"
    ["tsinghua"]="mirrors.tuna.tsinghua.edu.cn"
    ["ustc"]="mirrors.ustc.edu.cn"
    ["huawei"]="mirrors.huaweicloud.com"
)

declare -A PIP_MIRRORS
PIP_MIRRORS=(
    ["aliyun"]="mirrors.aliyun.com"
    ["tencent"]="mirrors.cloud.tencent.com"
    ["tsinghua"]="pypi.tuna.tsinghua.edu.cn"
    ["ustc"]="pypi.mirrors.ustc.edu.cn"
    ["huawei"]="mirrors.huaweicloud.com"
)

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCKER_CONTEXT="$PROJECT_DIR"
DOCKERFILE="$PROJECT_DIR/docker/Dockerfile"
COMPOSE_FILE="$PROJECT_DIR/docker/docker-compose.yml"
BUILD_TIMEOUT=300
USE_CHINA_MIRRORS=true

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

# Test mirror connectivity
test_mirror_speed() {
    local mirror=$1
    local timeout=5
    
    log_info "Testing mirror: $mirror"
    
    # Test HTTP connection speed
    local speed=$(timeout $timeout curl -s -o /dev/null -w "%{time_total}" "https://$mirror/" 2>/dev/null || echo "999")
    echo "$speed"
}

# Find fastest mirror
find_fastest_mirror() {
    local mirror_type=$1
    local -n mirrors=$2
    local fastest_mirror=""
    local fastest_speed=999
    
    log_info "Finding fastest $mirror_type mirror..."
    
    for name in "${!mirrors[@]}"; do
        local mirror_url="${mirrors[$name]}"
        local speed=$(test_mirror_speed "$mirror_url")
        
        # Use awk for floating point comparison
        if [ "$(echo "$speed" | awk -v f="$fastest_speed" '{print ($1 < f && $1 != 999)}')" -eq 1 ]; then
            fastest_speed=$speed
            fastest_mirror=$name
        fi
        
        log_info "$name ($mirror_url): ${speed}s"
    done
    
    if [ -n "$fastest_mirror" ]; then
        log_success "Fastest $mirror_type mirror: $fastest_mirror (${mirrors[$fastest_mirror]}) - ${fastest_speed}s"
        echo "$fastest_mirror"
    else
        log_warning "No working $mirror_type mirror found, using default"
        echo "aliyun"
    fi
}

# Build with selected mirrors
build_with_mirrors() {
    local apt_mirror=$1
    local pip_mirror=$2
    local build_method=$3
    local build_args=""
    
    if [ "$USE_CHINA_MIRRORS" = "true" ]; then
        build_args="--build-arg APT_MIRROR=${APT_MIRRORS[$apt_mirror]} --build-arg PIP_MIRROR=${PIP_MIRRORS[$pip_mirror]} --build-arg USE_CHINA_MIRRORS=true"
    else
        build_args="--build-arg USE_CHINA_MIRRORS=false"
    fi
    
    log_info "Building with mirrors: APT=${APT_MIRRORS[$apt_mirror]}, PIP=${PIP_MIRRORS[$pip_mirror]}"
    
    # Build the Docker image
    cd "$PROJECT_DIR"
    
    # Method 1: Direct docker build
    if [ "$build_method" = "docker" ]; then
        log_info "Building with docker build..."
        docker build -f "$DOCKERFILE" $build_args -t dns-monitor:latest .
    else
        # Method 2: Docker Compose build
        log_info "Building with docker compose..."
        export APT_MIRROR=${APT_MIRRORS[$apt_mirror]}
        export PIP_MIRROR=${PIP_MIRRORS[$pip_mirror]}
        export USE_CHINA_MIRRORS=$USE_CHINA_MIRRORS
        
        # Use docker compose (newer) or docker-compose (older)
        if command -v docker &> /dev/null && docker compose version &> /dev/null; then
            docker compose -f "$COMPOSE_FILE" build --no-cache dns-monitor
        elif command -v docker-compose &> /dev/null; then
            docker-compose -f "$COMPOSE_FILE" build --no-cache dns-monitor
        else
            log_warning "Neither 'docker compose' nor 'docker-compose' found, falling back to docker build"
            docker build -f "$DOCKERFILE" $build_args -t dns-monitor:latest .
        fi
    fi
}

# Create environment file for docker-compose
create_env_file() {
    local apt_mirror=$1
    local pip_mirror=$2
    local env_file="$PROJECT_DIR/.env"
    
    cat > "$env_file" << EOF
# Docker build optimization settings
APT_MIRROR=${APT_MIRRORS[$apt_mirror]}
PIP_MIRROR=${PIP_MIRRORS[$pip_mirror]}
USE_CHINA_MIRRORS=$USE_CHINA_MIRRORS

# Application settings
FLASK_ENV=production
FLASK_DEBUG=0
DNS_MONITOR_HOST=0.0.0.0
DNS_MONITOR_PORT=5000
BIND_LOG_PATH=/var/log/named/query.log
DATABASE_PATH=/app/backend/data/dns_monitor.db
EOF
    
    log_success "Environment file created: $env_file"
}

# Show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS] [COMMAND]

COMMANDS:
    build                   Build with automatic mirror selection
    build-fast              Build with fastest available mirrors
    build-specific <apt> <pip>  Build with specific mirror sources
    test-mirrors            Test all mirror speeds
    create-env              Create environment file only

OPTIONS:
    --no-china-mirrors      Disable Chinese mirror optimization
    --method <docker|compose>  Build method (default: compose)
    --help                  Show this help message

AVAILABLE MIRRORS:
    aliyun, tencent, tsinghua, ustc, huawei

EXAMPLES:
    $0 build                           # Auto-select fastest mirrors
    $0 build-specific aliyun tsinghua  # Use specific mirrors
    $0 test-mirrors                    # Test all mirrors
    $0 --no-china-mirrors build        # Build without Chinese mirrors
    $0 --method docker build           # Use docker build instead of compose
EOF
}

# Parse command line arguments
METHOD="compose"
COMMAND=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-china-mirrors)
            USE_CHINA_MIRRORS=false
            shift
            ;;
        --method)
            METHOD="$2"
            shift 2
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
        build|build-fast|test-mirrors|create-env)
            COMMAND="$1"
            shift
            ;;
        build-specific)
            COMMAND="$1"
            APT_MIRROR_NAME="$2"
            PIP_MIRROR_NAME="$3"
            shift 3
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
case $COMMAND in
    build|build-fast)
        log_info "Starting DNS Monitor optimized build..."
        
        if [ "$USE_CHINA_MIRRORS" = "true" ]; then
            # Find fastest mirrors
            apt_mirror=$(find_fastest_mirror "APT" APT_MIRRORS)
            pip_mirror=$(find_fastest_mirror "PIP" PIP_MIRRORS)
        else
            log_info "Chinese mirrors disabled, using default sources"
            apt_mirror="aliyun"
            pip_mirror="aliyun"
        fi
        
        # Create environment file
        create_env_file "$apt_mirror" "$pip_mirror"
        
        # Build with selected mirrors
        build_with_mirrors "$apt_mirror" "$pip_mirror" "$METHOD"
        
        log_success "Build completed successfully!"
        ;;
        
    build-specific)
        if [ -z "$APT_MIRROR_NAME" ] || [ -z "$PIP_MIRROR_NAME" ]; then
            log_error "Both APT and PIP mirror names are required for build-specific command"
            show_usage
            exit 1
        fi
        
        if [ -z "${APT_MIRRORS[$APT_MIRROR_NAME]}" ] || [ -z "${PIP_MIRRORS[$PIP_MIRROR_NAME]}" ]; then
            log_error "Invalid mirror name. Available mirrors: ${!APT_MIRRORS[@]}"
            exit 1
        fi
        
        log_info "Building with specific mirrors: APT=$APT_MIRROR_NAME, PIP=$PIP_MIRROR_NAME"
        
        # Create environment file
        create_env_file "$APT_MIRROR_NAME" "$PIP_MIRROR_NAME"
        
        # Build with specified mirrors
        build_with_mirrors "$APT_MIRROR_NAME" "$PIP_MIRROR_NAME" "$METHOD"
        
        log_success "Build completed successfully!"
        ;;
        
    test-mirrors)
        log_info "Testing all mirror speeds..."
        
        echo -e "\n${BLUE}APT Mirrors:${NC}"
        for name in "${!APT_MIRRORS[@]}"; do
            mirror_url="${APT_MIRRORS[$name]}"
            speed=$(test_mirror_speed "$mirror_url")
            echo -e "  $name ($mirror_url): ${speed}s"
        done
        
        echo -e "\n${BLUE}PIP Mirrors:${NC}"
        for name in "${!PIP_MIRRORS[@]}"; do
            mirror_url="${PIP_MIRRORS[$name]}"
            speed=$(test_mirror_speed "$mirror_url")
            echo -e "  $name ($mirror_url): ${speed}s"
        done
        ;;
        
    create-env)
        log_info "Creating environment file with fastest mirrors..."
        
        if [ "$USE_CHINA_MIRRORS" = "true" ]; then
            apt_mirror=$(find_fastest_mirror "APT" APT_MIRRORS)
            pip_mirror=$(find_fastest_mirror "PIP" PIP_MIRRORS)
        else
            apt_mirror="aliyun"
            pip_mirror="aliyun"
        fi
        
        create_env_file "$apt_mirror" "$pip_mirror"
        log_success "Environment file created successfully!"
        ;;
        
    *)
        log_error "No command specified"
        show_usage
        exit 1
        ;;
esac