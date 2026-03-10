# 全球市场财经日报系统

纯文字版全球市场监控与日报生成系统，A 股/港股为主，覆盖全球主要市场。

## 系统架构

```
finance-dash/
├── backend/
│   ├── data/           # 数据抓取层
│   │   ├── akshare_fetcher.py   # A 股/港股数据（AKShare）
│   │   └── yfinance_fetcher.py  # 美股/全球数据（yfinance）
│   ├── reports/        # 报告生成层
│   │   └── report_generator.py  # 午间速览 + 全天复盘
│   └── api/            # API 服务层
│       └── main.py              # FastAPI 接口
├── frontend/           # 前端展示层
│   └── index.html      # 纯文字报告页面
├── scheduler/          # 定时任务层
│   └── tasks.py        # APScheduler 调度
├── database/           # 数据存储层
│   ├── models.py       # SQLite 数据模型
│   └── finance.db      # 数据库文件（自动生成）
├── requirements.txt    # Python 依赖
└── README.md           # 本文档
```

## 功能特性

### 数据覆盖
- **A 股**：上证指数、创业板指、沪深 300、科创 50 等指数 + 个股监控
- **港股**：恒生指数、恒生国企 + 腾讯、阿里等龙头股
- **美股**：标普 500、纳斯达克、道琼斯 + 特斯拉、英伟达等科技股
- **全球**：日经 225、富时 100、德国 DAX 等主要指数
- **其他**：汇率、大宗商品、加密货币（可选）

### 报告类型
1. **午间速览**（11:30）- A 股午盘收盘后
   - A 股市场概览（涨跌比、涨停跌停）
   - 主要指数表现
   - 异动关注
   - 午间快讯

2. **全天复盘**（15:30）- A 股收盘后
   - 核心观点
   - 全球市场概览
   - 指数表现
   - 个股监控
   - 资金流向
   - 重要新闻
   - 明日关注

### 技术特点
- ✅ 纯文字报告，简洁高效
- ✅ 定时自动生成
- ✅ Web 页面随时查看
- ✅ SQLite 存储，轻量可扩展
- ✅ 模块化设计，易于扩展

## 快速开始

### 1. 安装依赖

```bash
cd finance-dash
pip3 install -r requirements.txt
```

### 2. 初始化数据库

```bash
python3 -c "from database.models import init_db; init_db()"
```

### 3. 启动 API 服务

```bash
# 方式一：直接运行
cd backend/api
python3 main.py

# 方式二：使用 uvicorn
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
```

访问：http://localhost:8000

### 4. 启动定时任务

```bash
# 新终端窗口
python3 scheduler/tasks.py
```

### 5. 手动生成报告（测试）

```bash
# 生成午间速览
curl http://localhost:8000/api/generate/noon

# 生成全天复盘
curl http://localhost:8000/api/generate/daily
```

## API 接口

### 报告相关
- `GET /api/reports` - 获取报告列表
- `GET /api/reports/latest` - 获取最新报告
- `GET /api/reports/{id}` - 获取报告详情
- `GET /api/generate/{type}` - 手动生成报告

### 标的管理
- `GET /api/symbols` - 获取监控标的列表
- `POST /api/symbols` - 添加监控标的
- `DELETE /api/symbols/{id}` - 删除监控标的

### 系统
- `GET /api/health` - 健康检查

## 定时任务时间

| 任务 | 时间 | 说明 |
|------|------|------|
| 午间速览 | 周一~周五 11:30 | A 股午盘收盘后 |
| 全天复盘 | 周一~周五 15:30 | A 股收盘后 |
| 美股复盘 | 周一~周五 10:00 | 美股收盘后（次日早） |

## 配置说明

### 修改监控标的

编辑 `backend/reports/report_generator.py` 中的 `_load_symbols()` 方法：

```python
return [
    {'symbol': 'sh000001', 'name': '上证指数', 'market': 'A 股', 'type': 'index'},
    {'symbol': '00700', 'name': '腾讯控股', 'market': '港股', 'type': 'stock'},
    # 添加更多标的...
]
```

### 修改报告时间

编辑 `scheduler/tasks.py` 中的 CronTrigger 配置：

```python
scheduler.add_job(
    job_daily_report,
    CronTrigger(hour=15, minute=30, day_of_week='mon-fri'),  # 修改时间
    ...
)
```

### 推送通知（待实现）

在 `report_generator.py` 的 `save_report()` 方法中添加推送逻辑：

```python
# 发送到 Feishu
send_to_feishu(content)

# 发送邮件
send_email(content)
```

## 扩展方向

1. **数据源扩展**
   - 接入 Tushare（更全面的 A 股数据）
   - 接入 Alpha Vantage（美股 API）
   - 接入新浪财经 API（实时数据）

2. **分析增强**
   - 技术指标计算（MA、MACD、RSI）
   - 资金流向分析
   - 板块热度排行

3. **推送渠道**
   - Feishu 机器人
   - 邮件推送
   - Telegram Bot
   - 微信推送

4. **前端优化**
   - 图表展示（ECharts）
   - 移动端适配
   - 暗黑模式

## 技术栈

- **后端**：Python 3.8+
- **Web 框架**：FastAPI
- **数据抓取**：AKShare、yfinance
- **数据库**：SQLite（可切换 PostgreSQL）
- **定时任务**：APScheduler
- **前端**：原生 HTML/CSS/JS

## 注意事项

1. **数据延迟**：免费数据源可能有 15 分钟延迟
2. **API 限制**：AKShare 和 yfinance 有频率限制，避免高频调用
3. **交易日历**：当前未处理节假日，需手动添加交易日历判断
4. **时区**：所有时间默认为 Asia/Shanghai（北京时间）

## 许可证

MIT License
