# Finance Dash 抓取服务

自动获取 A 股、港股、美股市场数据，生成午间速览和全天复盘报告，并推送到 D1 数据库。

## 功能特性

- 📊 **市场数据抓取** - A 股、港股、美股实时数据
- 📝 **智能报告生成** - 午间速览（11:35）和全天复盘（15:35）
- ☁️ **云端存储** - 数据直接推送到 Cloudflare D1
- ⏰ **定时任务** - 自动运行，无需人工干预
- 🐳 **systemd 服务** - 支持后台运行和管理

## 快速开始

### 1. 克隆项目

```bash
cd /opt
git clone <your-repo-url> finance-dash
cd finance-dash/fetcher
```

### 2. 运行部署脚本

```bash
# 使用默认路径 /opt/finance-dash/fetcher
sudo ./deploy.sh

# 或使用自定义路径
sudo ./deploy.sh /your/custom/path
```

部署脚本会自动：
- ✅ 检查 Python 环境
- ✅ 安装依赖包
- ✅ 创建日志目录
- ✅ 配置定时任务

### 3. 配置环境变量

```bash
cp .env.example .env
nano .env
```

编辑 `.env` 文件：

```env
D1_API_BASE=https://finance-dash.yafeng-ten.workers.dev
D1_FETCHER_SECRET=your-secret-key
```

### 4. 测试运行

```bash
# 测试 API 连通性
./test.sh health

# 测试生成午间速览
./test.sh noon

# 运行全部测试
./test.sh all
```

## 手动运行

```bash
# 检查 API 健康状态
python3 main.py health

# 推送市场概览数据
python3 main.py market

# 生成午间速览
python3 main.py noon

# 生成全天复盘
python3 main.py daily

# 执行全部任务
python3 main.py all
```

## 定时任务配置

部署脚本会自动配置以下定时任务：

| 时间 | 任务 | 说明 |
|------|------|------|
| 11:35 | `main.py noon` | 生成午间速览（工作日） |
| 15:35 | `main.py daily` | 生成全天复盘（工作日） |
| 每小时 | `main.py market` | 推送市场数据（工作日 9-15点） |

### 查看定时任务

```bash
crontab -l
```

### 手动编辑定时任务

```bash
# 编辑当前用户的 crontab
crontab -e

# 或从文件导入
crontab crontab.txt
```

## systemd 服务（可选）

### 安装服务

```bash
sudo cp finance-dash-fetcher.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable finance-dash-fetcher
sudo systemctl start finance-dash-fetcher
```

### 服务管理命令

```bash
# 启动服务
sudo systemctl start finance-dash-fetcher

# 停止服务
sudo systemctl stop finance-dash-fetcher

# 重启服务
sudo systemctl restart finance-dash-fetcher

# 查看状态
sudo systemctl status finance-dash-fetcher

# 查看日志
sudo journalctl -u finance-dash-fetcher -f
```

## 日志查看

### 日志文件位置

- 标准输出：`/var/log/finance-dash/fetcher.log`
- 错误日志：`/var/log/finance-dash/fetcher-error.log`

### 查看日志

```bash
# 实时查看日志
tail -f /var/log/finance-dash/fetcher.log

# 查看最近 100 行
tail -n 100 /var/log/finance-dash/fetcher.log

# 查看错误日志
tail -f /var/log/finance-dash/fetcher-error.log

# 搜索特定内容
grep "ERROR" /var/log/finance-dash/fetcher.log
```

### 日志轮转

建议配置 logrotate 防止日志文件过大：

```bash
sudo tee /etc/logrotate.d/finance-dash << 'EOF'
/var/log/finance-dash/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
EOF
```

## 项目结构

```
fetcher/
├── main.py                     # 主入口
├── report_generator.py         # 报告生成器
├── push_client.py              # D1 推送客户端
├── akshare_fetcher.py          # A 股/港股数据获取
├── yfinance_fetcher.py         # 美股数据获取
├── requirements.txt            # Python 依赖
├── .env.example                # 环境变量模板
├── deploy.sh                   # 部署脚本
├── test.sh                     # 测试脚本
├── finance-dash-fetcher.service # systemd 服务文件
└── README.md                   # 本文档
```

## 依赖说明

- Python 3.8+
- akshare >= 1.11.0 (A 股/港股数据)
- yfinance >= 0.2.28 (美股数据)
- pandas >= 2.0.0
- requests >= 2.31.0
- python-dotenv >= 1.0.0

## 故障排查

### API 连接失败

```bash
# 检查网络连通性
curl https://finance-dash.yafeng-ten.workers.dev/api/health

# 检查环境变量配置
cat /opt/finance-dash/fetcher/.env
```

### 定时任务未执行

```bash
# 检查 crontab 是否安装
which crontab

# 查看当前用户的定时任务
crontab -l

# 检查 cron 服务状态
sudo service cron status
```

### 依赖安装失败

```bash
# 升级 pip
pip3 install --upgrade pip

# 单独安装依赖
pip3 install akshare yfinance pandas requests python-dotenv
```

## 更新部署

```bash
cd /opt/finance-dash/fetcher
git pull
pip3 install -r requirements.txt
sudo systemctl restart finance-dash-fetcher
```

## License

MIT
