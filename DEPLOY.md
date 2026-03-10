# 财经日报系统 - Cloudflare 部署指南

## 架构

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│  Cloudflare     │────▶│  Cloudflare      │────▶│  Cloudflare │
│  Pages (前端)   │     │  Workers (API)   │     │  D1 (DB)    │
└─────────────────┘     └──────────────────┘     └─────────────┘
```

## 首次部署步骤

### 1. 登录 Cloudflare

```bash
cd /root/.openclaw/workspace/finance-dash
wrangler login
```

### 2. 创建 D1 数据库

```bash
wrangler d1 create finance-dash-db
```

输出示例：
```
✅ Successfully created DB 'finance-dash-db' in region UNKNOWN
database_id: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**重要**：复制 `database_id`，填入 `wrangler.toml` 的 `database_id` 字段。

### 3. 初始化数据库

```bash
wrangler d1 execute finance-dash-db --file=worker/schema.sql
```

### 4. 部署

```bash
# 部署前端 + Worker + API
wrangler deploy
```

部署成功后会输出：
```
Deployed finance-dash triggers:
- https://finance-dash.xxxxx.workers.dev (Worker API)
- https://finance-dash.pages.dev (前端 Pages)
```

## 日常开发

### 本地开发

```bash
# 启动本地开发服务器（热重载）
wrangler dev
```

访问：http://localhost:8787

### 修改代码后部署

```bash
# 直接部署
wrangler deploy

# 或者用 npm 脚本
npm run deploy
```

## 项目结构

```
finance-dash/
├── frontend/          # 前端静态文件（自动部署到 Pages）
│   └── index.html
├── worker/            # Worker API 代码
│   ├── index.js       # 主入口
│   └── schema.sql     # 数据库结构
├── wrangler.toml      # Cloudflare 配置
└── package.json       # 项目配置
```

## 环境变量

在 `wrangler.toml` 中配置：

```toml
[vars]
TZ = "Asia/Shanghai"
API_KEY = "your-api-key"  # 如需接入外部 API
```

## 定时任务（Cron）

Cloudflare Workers 支持 Cron Triggers：

```toml
# wrangler.toml 添加
[triggers]
crons = ["30 11 * * 1-5", "30 15 * * 1-5"]  # 午间 11:30 / 全天 15:30
```

然后在 Worker 中处理：

```js
export default {
  async scheduled(event, env, ctx) {
    // 定时生成报告
    await generateReport(env, 'noon');
  }
}
```

## 费用

Cloudflare 免费额度：
- Pages: 100GB 带宽/月
- Workers: 100,000 请求/天
- D1: 5GB 存储

个人使用完全免费。

## 访问地址

- 前端：https://finance-dash.pages.dev
- API: https://finance-dash.xxxxx.workers.dev/api/health
