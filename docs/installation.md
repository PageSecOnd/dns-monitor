# DNS Monitor Installation Guide

## 系统要求

### 硬件要求
- **最低配置**: 1 CPU核心, 512MB内存, 1GB存储空间
- **推荐配置**: 2 CPU核心, 2GB内存, 10GB存储空间
- **网络**: 100Mbps带宽

### 软件要求
- **操作系统**: Ubuntu 18.04+, Debian 10+, CentOS 7+
- **Python**: 3.8+
- **数据库**: SQLite 3.x
- **Web服务器**: Nginx (可选)
- **DNS服务器**: BIND9 (如需监控DNS)

## 安装方式

### 方式一：自动安装脚本（推荐）

```bash
# 下载项目
git clone https://github.com/PageSecOnd/dns-monitor.git
cd dns-monitor

# 运行安装脚本（需要root权限）
sudo chmod +x scripts/install.sh
sudo ./scripts/install.sh
```

安装脚本将自动：
- 安装系统依赖
- 创建服务用户
- 配置Python环境
- 设置Nginx反向代理
- 配置Systemd服务
- 启动所有服务

### 方式二：Docker部署

```bash
# 下载项目
git clone https://github.com/PageSecOnd/dns-monitor.git
cd dns-monitor

# 构建并启动容器
docker-compose -f docker/docker-compose.yml up -d

# 查看运行状态
docker-compose -f docker/docker-compose.yml ps
```

### 方式三：手动安装

#### 1. 安装系统依赖

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv nginx sqlite3 bind9-utils
```

**CentOS/RHEL:**
```bash
sudo yum install python3 python3-pip nginx sqlite bind-utils
```

#### 2. 创建安装目录

```bash
sudo mkdir -p /opt/dns-monitor
sudo chown $USER:$USER /opt/dns-monitor
```

#### 3. 安装应用

```bash
# 复制文件
cp -r backend frontend nginx systemd /opt/dns-monitor/

# 创建虚拟环境
cd /opt/dns-monitor
python3 -m venv venv
source venv/bin/activate

# 安装Python依赖
pip install -r backend/requirements.txt
```

#### 4. 配置服务

```bash
# 配置Systemd服务
sudo cp systemd/dns-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable dns-monitor

# 配置Nginx
sudo cp nginx/nginx.conf /etc/nginx/sites-available/dns-monitor
sudo ln -s /etc/nginx/sites-available/dns-monitor /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

#### 5. 启动服务

```bash
sudo systemctl start dns-monitor
sudo systemctl status dns-monitor
```

## BIND9配置

### 启用查询日志

1. 编辑BIND9配置文件：

```bash
sudo nano /etc/bind/named.conf
```

2. 添加日志配置：

```bind
logging {
    channel query_log {
        file "/var/log/named/query.log" versions 3 size 10m;
        severity info;
        print-category yes;
        print-time yes;
    };
    category queries { query_log; };
};
```

3. 创建日志目录：

```bash
sudo mkdir -p /var/log/named
sudo chown bind:bind /var/log/named
sudo chmod 755 /var/log/named
```

4. 重启BIND9：

```bash
sudo systemctl restart named
# 或者
sudo systemctl restart bind9
```

### 验证日志记录

```bash
# 检查日志文件是否创建
ls -la /var/log/named/

# 查看查询日志
sudo tail -f /var/log/named/query.log
```

## 配置文件

### 环境变量

创建配置文件 `/opt/dns-monitor/.env`：

```bash
# Flask配置
FLASK_ENV=production
FLASK_DEBUG=0

# 服务配置
DNS_MONITOR_HOST=0.0.0.0
DNS_MONITOR_PORT=5000

# 路径配置
BIND_LOG_PATH=/var/log/named/query.log
DATABASE_PATH=/opt/dns-monitor/backend/data/dns_monitor.db

# 安全配置
SECRET_KEY=your-secret-key-here
```

### Nginx配置优化

编辑 `/etc/nginx/sites-available/dns-monitor`：

```nginx
# 添加SSL支持
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/your/cert.pem;
    ssl_certificate_key /path/to/your/private.key;
    
    # SSL优化配置
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers on;
    
    # 其他配置...
}

# HTTP重定向到HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

## 防火墙配置

### UFW (Ubuntu/Debian)

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 53/tcp
sudo ufw allow 53/udp
sudo ufw enable
```

### Firewalld (CentOS/RHEL)

```bash
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-service=dns
sudo firewall-cmd --reload
```

## 性能优化

### 系统优化

1. **调整系统限制**：

编辑 `/etc/security/limits.conf`：

```
* soft nofile 65536
* hard nofile 65536
```

2. **优化内核参数**：

编辑 `/etc/sysctl.conf`：

```
net.core.somaxconn = 1024
net.core.netdev_max_backlog = 5000
```

### 数据库优化

```bash
# 定期清理旧数据
sqlite3 /opt/dns-monitor/backend/data/dns_monitor.db "DELETE FROM system_monitoring WHERE timestamp < datetime('now', '-30 days');"

# 重建索引
sqlite3 /opt/dns-monitor/backend/data/dns_monitor.db "REINDEX;"

# 清理数据库
sqlite3 /opt/dns-monitor/backend/data/dns_monitor.db "VACUUM;"
```

## 监控和维护

### 日志轮转

创建 `/etc/logrotate.d/dns-monitor`：

```
/opt/dns-monitor/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload dns-monitor
    endscript
}
```

### 健康检查

创建健康检查脚本 `/opt/dns-monitor/scripts/health-check.sh`：

```bash
#!/bin/bash

# 检查服务状态
if ! systemctl is-active --quiet dns-monitor; then
    echo "DNS Monitor service is not running"
    exit 1
fi

# 检查HTTP响应
if ! curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "DNS Monitor web interface is not responding"
    exit 1
fi

echo "All checks passed"
exit 0
```

### 备份脚本

创建备份脚本 `/opt/dns-monitor/scripts/backup.sh`：

```bash
#!/bin/bash

BACKUP_DIR="/backup/dns-monitor"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
sqlite3 /opt/dns-monitor/backend/data/dns_monitor.db ".backup $BACKUP_DIR/dns_monitor_$DATE.db"

# 备份配置文件
tar -czf $BACKUP_DIR/config_$DATE.tar.gz /opt/dns-monitor/backend/ /etc/nginx/sites-available/dns-monitor

# 清理旧备份
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

## 故障排除

### 常见问题

1. **服务无法启动**

```bash
# 检查服务状态
sudo systemctl status dns-monitor

# 查看详细日志
sudo journalctl -u dns-monitor -f

# 检查配置文件
python3 -m py_compile /opt/dns-monitor/backend/app.py
```

2. **数据库权限问题**

```bash
sudo chown -R www-data:www-data /opt/dns-monitor/backend/data
sudo chmod 755 /opt/dns-monitor/backend/data
sudo chmod 644 /opt/dns-monitor/backend/data/dns_monitor.db
```

3. **BIND9日志无法读取**

```bash
sudo chmod 644 /var/log/named/query.log
sudo chown bind:adm /var/log/named/query.log
```

4. **端口占用**

```bash
# 检查端口占用
sudo netstat -tlnp | grep :5000
sudo lsof -i :5000

# 修改配置文件中的端口
sudo nano /opt/dns-monitor/.env
```

### 调试模式

启用调试模式：

```bash
# 编辑环境变量
sudo nano /opt/dns-monitor/.env

# 设置调试模式
FLASK_DEBUG=1
FLASK_ENV=development

# 重启服务
sudo systemctl restart dns-monitor
```

## 安全加固

### 1. 用户权限

```bash
# 创建专用用户
sudo useradd -r -s /bin/false dnsmonitor
sudo chown -R dnsmonitor:dnsmonitor /opt/dns-monitor
```

### 2. 文件权限

```bash
# 设置正确的文件权限
sudo chmod 750 /opt/dns-monitor
sudo chmod 640 /opt/dns-monitor/.env
sudo chmod 644 /opt/dns-monitor/backend/*.py
```

### 3. SELinux配置（CentOS/RHEL）

```bash
# 设置SELinux上下文
sudo setsebool -P httpd_can_network_connect 1
sudo semanage port -a -t http_port_t -p tcp 5000
```

## 升级和更新

### 自动更新脚本

创建 `/opt/dns-monitor/scripts/update.sh`：

```bash
#!/bin/bash

cd /opt/dns-monitor

# 停止服务
sudo systemctl stop dns-monitor

# 备份当前版本
cp -r backend backend.backup.$(date +%Y%m%d)

# 拉取最新代码
git pull origin main

# 更新依赖
source venv/bin/activate
pip install -r backend/requirements.txt

# 启动服务
sudo systemctl start dns-monitor

echo "Update completed"
```

这个安装指南涵盖了DNS监控系统的完整安装、配置和维护过程。根据你的具体环境选择合适的安装方式。