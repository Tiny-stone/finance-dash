# 数据库迁移说明

## 新增字段

需要在 `daily_reports` 表中添加 `hot_summary` 字段：

```sql
-- 添加 hot_summary 字段
ALTER TABLE daily_reports ADD COLUMN hot_summary TEXT;
```

## 完整表结构

### daily_reports 表

```sql
CREATE TABLE daily_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_date TEXT NOT NULL,
    report_type TEXT NOT NULL,  -- 'premarket', 'noon', 'daily'
    content TEXT NOT NULL,
    summary TEXT,
    hot_summary TEXT,           -- 新增：AI生成的市场热点总结
    metadata TEXT,              -- JSON格式存储额外数据
    created_at TEXT NOT NULL,
    updated_at TEXT
);

-- 创建复合索引
CREATE INDEX idx_daily_reports_date_type ON daily_reports(report_date, report_type);
CREATE INDEX idx_daily_reports_date ON daily_reports(report_date);
```

### market_summary 表

```sql
CREATE TABLE market_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    market TEXT NOT NULL,
    up_count INTEGER DEFAULT 0,
    down_count INTEGER DEFAULT 0,
    flat_count INTEGER DEFAULT 0,
    limit_up INTEGER DEFAULT 0,
    limit_down INTEGER DEFAULT 0,
    up_ratio REAL DEFAULT 0,
    indices TEXT,               -- JSON格式存储指数数据
    metadata TEXT,              -- JSON格式存储额外数据
    created_at TEXT NOT NULL,
    updated_at TEXT
);
```

## metadata JSON 结构示例

```json
{
  "indices": [
    {"name": "上证指数", "value": "3050.23", "change": 0.52},
    {"name": "深证成指", "value": "9780.45", "change": -0.31}
  ],
  "market_stats": {
    "up": 2345,
    "down": 1890,
    "flat": 456
  },
  "watchlist": [
    {"name": "贵州茅台", "code": "600519", "price": "1680.50", "change": 1.23},
    {"name": "腾讯控股", "code": "00700", "price": "298.40", "change": -0.85}
  ]
}
```

## 数据推送示例

```bash
# 推送盘前简报
curl -X POST https://your-worker.workers.dev/api/internal/push-report \
  -H "Authorization: Bearer YOUR_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "report_date": "2026-03-11",
    "report_type": "premarket",
    "content": "详细报告内容...",
    "summary": "报告摘要",
    "hot_summary": "1. 美股昨夜大涨，科技股领涨。2. 港股ADR表现强劲。3. 今日关注：美联储利率决议。4. 板块热点：AI芯片、新能源。5. 风险提示：地缘政治紧张。",
    "metadata": {
      "indices": [...],
      "market_stats": {...},
      "watchlist": [...]
    }
  }'
```
