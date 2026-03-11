# Finance Dash - 全球市场财经日报系统

Cloudflare 全栈架构的财经数据抓取与报告系统。

## 架构概览

```
finance-dash/
├── fetcher/                # 数据抓取服务（Python）
│   ├── main.py            # 抓取服务入口
│   ├── report_generator.py # 报告生成器（推送 D1）
│   ├── akshare_fetcher.py  # A股/港股数据（AKShare）
│   ├── yfinance_fetcher.py # 美股/全球数据（yfinance）
│   ├── push_client.py      # D1 推送客户端
│   └── requirements.txt    # Python 依赖
├── web/                    # 前端（Cloudflare Pages）
│   ├── frontend/
│   │   └── index.html      # 报告展示页面
│   └── package.json        # Pages 部署配置
├── worker/                 # Cloudflare Worker API
│   ├── index.js           # Worker 入口
│   └── schema.sql         # D1 数据库 Schema
├── package.json           # 根项目配置
└── wrangler.toml          # Cloudflare 配置
```

## 数据流向

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   fetcher   │────▶│  D1PushClient│────▶│  D1 Database│
│  (Python)   │     │  (HTTP API)  │     │  (Cloudflare)│
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │   Worker    │
                                        │   (API)     │
                                        └─────────────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │   Pages     │
                                        │  (Frontend) │
                                        └─────────────┘
```

## 快速开始

### 1. 配置环境变量

创建 `fetcher/.env`：

```bash
D1_API_BASE=https://finance-dash-api.your-account.workers.dev
D1_FETCHER_SECRET=your-secret-key
```

### 2. 安装抓取服务依赖

```bash
cd fetcher
pip install -r requirements.txt
```

### 3. 测试抓取服务

```bash
# 检查 API 健康状态
python main.py health

# 生成并推送午间速览
python main.py noon

# 生成并推送全天复盘
python main.py daily

# 推送市场概览
python main.py market

# 执行全部任务
python main.py all
```

### 4. 部署前端

```bash
cd web
npm run deploy
```

## 定时任务配置

使用 cron 配置定时抓取：

```bash
# 编辑 crontab
crontab -e

# 添加定时任务（北京时间）
# 午间速览：工作日 11:35
35 11 * * 1-5 cd /path/to/finance-dash/fetcher && python main.py noon >> /var/log/finance-dash.log 2>&1

# 全天复盘：工作日 15:35
35 15 * * 1-5 cd /path/to/finance-dash/fetcher && python main.py daily >> /var/log/finance-dash.log 2>&1

# 市场数据：每小时推送一次
0 * * * * cd /path/to/finance-dash/fetcher && python main.py market >> /var/log/finance-dash.log 2>&1
```

## API 接口

### 内部推送接口（fetcher 使用）

- `POST /api/internal/push-report` - 推送日报
- `POST /api/internal/push-market-data` - 推送市场数据

### 公开查询接口

- `GET /api/health` - 健康检查
- `GET /api/reports/latest?report_type={noon|daily}` - 获取最新报告
- `GET /api/reports?report_type={noon|daily}&limit=10` - 获取报告列表
- `GET /api/market-summary?date=YYYY-MM-DD` - 获取市场概览

## 数据覆盖

### A 股
- 指数：上证指数、创业板指、沪深300、科创50
- 个股：可配置监控列表
- 数据：实时行情、涨跌幅、成交量

### 港股
- 指数：恒生指数、恒生国企
- 个股：腾讯、阿里等龙头股

### 美股
- 指数：标普500、纳斯达克、道琼斯
- 个股：特斯拉、英伟达等科技股

### 全球市场
- 日经225、富时100、德国DAX、法国CAC40

## 技术栈

- **抓取服务**：Python 3.8+ + AKShare + yfinance
- **数据库**：Cloudflare D1 (SQLite)
- **API**：Cloudflare Workers
- **前端**：Cloudflare Pages + 原生 JS
- **部署**：Wrangler CLI

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `D1_API_BASE` | Worker API 地址 | - |
| `D1_FETCHER_SECRET` | API 认证密钥 | - |

## 目录说明

### fetcher/
数据抓取服务的核心代码，独立于后端运行。

- `main.py` - CLI 入口，支持多种命令
- `report_generator.py` - 生成报告并推送到 D1
- `akshare_fetcher.py` - A股/港股数据抓取
- `yfinance_fetcher.py` - 美股/全球数据抓取
- `push_client.py` - D1 HTTP API 客户端

### web/
前端代码，部署到 Cloudflare Pages。

- `frontend/index.html` - 纯静态页面，从 Worker API 获取数据
- `package.json` - Pages 部署脚本

### worker/
Cloudflare Worker 代码，提供 API 服务。

## 迁移说明

从旧架构（本地 SQLite）迁移到新架构（Cloudflare D1）：

1. 数据存储从本地 SQLite 改为 Cloudflare D1
2. 抓取服务通过 HTTP API 推送数据，不再直接操作数据库
3. 前端通过 Worker API 查询数据，不再直接连接数据库
4. 删除 `backend/data/` 和 `backend/reports/` 目录（已迁移到 `fetcher/`）

## License

MIT
