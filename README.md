# DNS服务器监控系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://hub.docker.com/)

现代化、炫酷的DNS服务器监控系统，专为实时监控Debian系统和BIND9 DNS服务器状态而设计。

![DNS Monitor Screenshot](https://github.com/user-attachments/assets/9017965e-bb41-4c5c-b06f-f738b5f48ad0)

## ✨ 特性

### 🖥️ 系统监控
- 🔄 实时CPU使用率监控（带动态仪表盘）
- 💾 内存使用情况显示（进度条和百分比）
- 💿 磁盘使用情况监控
- 🌐 网络流量统计
- ⚖️ 系统负载平均值
- ⏱️ 系统运行时间显示

### 🌍 DNS服务监控
- 🔧 BIND9服务状态监控
- 📊 DNS查询统计（QPS）
- 📈 查询类型分布（A、AAAA、MX、CNAME等）
- ⚡ 响应时间统计
- ❌ 错误率监控

### 🚀 实时功能
- 📋 当前DNS查询实时列表
- 🔍 查询来源IP追踪
- 🌐 查询域名监控
- 📝 查询类型识别
- ⏱️ 响应时间测量

### 📊 历史数据
- 📅 查询历史记录表格
- 🔍 可搜索和过滤功能
- 📈 查询量趋势图表
- 🏆 热门查询域名排行榜

## 🎨 UI设计

- 🌙 深色赛博朋克主题
- ✨ 霓虹灯特效
- 📊 动态数据可视化
- 🌟 粒子背景效果
- 🎭 平滑动画过渡
- 📱 响应式设计，支持移动端

## 🏗️ 技术架构

### 前端技术栈
- **HTML5 + CSS3 + JavaScript** - 现代Web标准
- **Chart.js** - 动态图表库
- **Particles.js** - 粒子背景效果
- **WebSocket** - 实时数据通信
- **响应式设计** - 支持各种设备

### 后端技术栈
- **Python Flask** - Web框架
- **psutil** - 系统信息收集
- **Flask-SocketIO** - WebSocket支持
- **SQLite** - 数据存储
- **BIND9日志解析** - DNS查询分析

### 部署技术
- **Docker** - 容器化部署（支持构建优化）
- **Nginx** - 反向代理
- **Systemd** - 服务管理
- **Supervisor** - 进程监控

### 🚀 构建优化特性
- **智能镜像源选择** - 自动测试和选择最快的中国镜像源
- **多阶段构建** - 减少镜像大小30-50%
- **自动故障切换** - 镜像源失败时自动回退
- **性能监控** - 实时构建性能数据
- **多架构支持** - 支持AMD64和ARM64
- **环境灵活配置** - 支持环境变量和构建参数

## 🚀 快速开始

### 方式一：Docker部署（推荐）

#### 标准构建
```bash
# 克隆项目
git clone https://github.com/PageSecOnd/dns-monitor.git
cd dns-monitor

# 使用Docker Compose启动
docker-compose -f docker/docker-compose.yml up -d

# 访问应用
http://localhost:80
```

#### 🚀 优化构建（中国用户推荐）
```bash
# 克隆项目
git clone https://github.com/PageSecOnd/dns-monitor.git
cd dns-monitor

# 使用优化脚本自动选择最快镜像源构建（3-5分钟）
./scripts/build-optimized.sh build

# 或者使用docker-compose（需要先配置环境变量）
cp .env.template .env
docker-compose -f docker/docker-compose.yml up -d --build

# 访问应用
http://localhost:80
```

**构建优化特性：**
- 🚀 **构建速度提升3-5倍**：从10-15分钟缩短到3-5分钟
- 🌐 **智能镜像源选择**：自动测试并选择最快的中国镜像源
- 🔄 **自动故障切换**：镜像源失败时自动回退到默认源
- 📊 **性能监控**：实时显示构建性能数据

详细信息请参考：[Docker构建优化指南](README-docker-optimization.md)

### 方式二：传统部署

```bash
# 克隆项目
git clone https://github.com/PageSecOnd/dns-monitor.git
cd dns-monitor

# 运行安装脚本（需要root权限）
sudo ./scripts/install.sh

# 手动安装Python依赖
pip3 install -r backend/requirements.txt

# 启动简单服务器（用于演示）
python3 backend/simple_server.py
```

### 方式三：开发模式

```bash
# 克隆项目
git clone https://github.com/PageSecOnd/dns-monitor.git
cd dns-monitor

# 安装依赖
pip3 install -r backend/requirements.txt

# 启动开发服务器
python3 backend/simple_server.py

# 在浏览器中访问
http://localhost:5000
```

## 📁 项目结构

```
dns-monitor/
├── backend/                # 后端代码
│   ├── app.py             # Flask主应用
│   ├── simple_server.py   # 简单HTTP服务器（演示用）
│   ├── monitors/          # 监控模块
│   │   ├── system_monitor.py    # 系统监控
│   │   └── dns_monitor.py       # DNS监控
│   ├── utils/             # 工具函数
│   │   └── database.py    # 数据库管理
│   └── requirements.txt   # Python依赖
├── frontend/              # 前端文件
│   ├── index.html        # 主页面
│   ├── css/              # 样式文件
│   │   ├── style.css     # 主样式
│   │   ├── animations.css # 动画效果
│   │   └── responsive.css # 响应式设计
│   └── js/               # JavaScript文件
│       ├── app.js        # 主应用逻辑
│       ├── charts.js     # 图表功能
│       ├── websocket.js  # WebSocket通信
│       ├── utils.js      # 工具函数
│       └── particles-config.js # 粒子配置
├── nginx/                # Nginx配置
│   └── nginx.conf        # 主配置文件
├── docker/               # Docker配置
│   ├── Dockerfile        # Docker镜像构建
│   ├── docker-compose.yml # 容器编排
│   └── supervisord.conf  # 进程管理
├── systemd/              # 系统服务
│   └── dns-monitor.service # Systemd服务文件
├── scripts/              # 部署脚本
│   └── install.sh        # 自动安装脚本
└── docs/                 # 文档
```

## ⚙️ 配置说明

### BIND9配置

为了启用DNS查询日志，需要在BIND9配置中添加：

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

### 环境变量

```bash
# Flask配置
FLASK_ENV=production
FLASK_DEBUG=0

# 服务配置
DNS_MONITOR_HOST=0.0.0.0
DNS_MONITOR_PORT=5000

# 路径配置
BIND_LOG_PATH=/var/log/named/query.log
DATABASE_PATH=/app/backend/data/dns_monitor.db
```

## 📊 API接口

### 系统监控API

```http
GET /api/system/stats
GET /api/history/system?hours=24
```

### DNS监控API

```http
GET /api/dns/stats
GET /api/dns/queries?limit=100
GET /api/history/dns?hours=24
```

## 🔧 性能优化

### 前端优化
- 静态资源缓存（1年有效期）
- Gzip压缩
- 响应式图片
- 懒加载

### 后端优化
- 数据库索引优化
- 缓存机制
- 异步处理
- 连接池

### 系统要求
- **最低配置**: 1 CPU核心, 512MB内存
- **推荐配置**: 2 CPU核心, 2GB内存
- **存储空间**: 至少1GB可用空间
- **网络**: 100Mbps带宽

## 🛡️ 安全特性

- CSRF保护
- XSS防护
- 安全响应头
- 访问日志记录
- 速率限制
- HTTPS支持

## 🐛 故障排除

### 常见问题

1. **服务无法启动**
   ```bash
   sudo systemctl status dns-monitor
   sudo journalctl -u dns-monitor -f
   ```

2. **BIND9日志无法读取**
   ```bash
   sudo chmod 644 /var/log/named/query.log
   sudo chown bind:adm /var/log/named/query.log
   ```

3. **端口冲突**
   ```bash
   sudo netstat -tlnp | grep :5000
   sudo lsof -i :5000
   ```

### 日志位置

- 应用日志: `/var/log/dns-monitor/`
- Nginx日志: `/var/log/nginx/`
- 系统日志: `journalctl -u dns-monitor`

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📜 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 👥 作者

- **PageSecOnd** - *初始工作* - [PageSecOnd](https://github.com/PageSecOnd)

## 🙏 致谢

- [Chart.js](https://www.chartjs.org/) - 图表库
- [Particles.js](https://vincentgarreau.com/particles.js/) - 粒子效果
- [Flask](https://flask.palletsprojects.com/) - Web框架
- [psutil](https://psutil.readthedocs.io/) - 系统监控库

## 📈 版本历史

- **v1.0.0** - 初始版本
  - 基础系统监控
  - DNS服务监控
  - 现代化UI界面
  - Docker支持

---

<p align="center">
  <b>🌟 如果这个项目对你有帮助，请给它一个星标！ 🌟</b>
</p>