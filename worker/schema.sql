-- D1 数据库初始化脚本
-- 财经日报系统

-- 日报表
CREATE TABLE IF NOT EXISTS daily_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_date TEXT NOT NULL,
    report_type TEXT NOT NULL,  -- 'noon' | 'daily'
    content TEXT NOT NULL,
    summary TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT,
    UNIQUE(report_date, report_type)
);

-- 监控标的表
CREATE TABLE IF NOT EXISTS symbols (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    market TEXT NOT NULL,  -- 'A 股' | '港股' | '美股'
    category TEXT DEFAULT 'stock',  -- 'stock' | 'index'
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now'))
);

-- 个股行情表
CREATE TABLE IF NOT EXISTS daily_quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    quote_date TEXT NOT NULL,
    price REAL,
    change REAL,
    change_pct REAL,
    volume REAL,
    amount REAL,
    high REAL,
    low REAL,
    open REAL,
    prev_close REAL,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(symbol, quote_date)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_reports_date ON daily_reports(report_date DESC);
CREATE INDEX IF NOT EXISTS idx_reports_type ON daily_reports(report_type);
CREATE INDEX IF NOT EXISTS idx_quotes_symbol ON daily_quotes(symbol);
CREATE INDEX IF NOT EXISTS idx_quotes_date ON daily_quotes(quote_date DESC);

-- 插入默认监控标的
INSERT OR IGNORE INTO symbols (symbol, name, market, category) VALUES
    ('sh000001', '上证指数', 'A 股', 'index'),
    ('sz399006', '创业板指', 'A 股', 'index'),
    ('sh000300', '沪深 300', 'A 股', 'index'),
    ('hk.HSI', '恒生指数', '港股', 'index'),
    ('US.SPX', '标普 500', '美股', 'index'),
    ('US.IXIC', '纳斯达克', '美股', 'index');
