-- D1 数据库结构

-- 日报表
CREATE TABLE IF NOT EXISTS daily_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_date TEXT NOT NULL,
    report_type TEXT NOT NULL,  -- 'noon' 或 'daily'
    content TEXT NOT NULL,
    summary TEXT,
    metadata TEXT,  -- JSON 格式存储额外数据
    created_at TEXT NOT NULL,
    updated_at TEXT
);

-- 监控标的表
CREATE TABLE IF NOT EXISTS symbols (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    market TEXT NOT NULL,  -- 'A股', '港股', '美股'
    category TEXT DEFAULT 'stock',  -- 'stock', 'index', 'etf'
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 市场概览数据表（新增）
CREATE TABLE IF NOT EXISTS market_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    market TEXT NOT NULL,  -- 'A股', '港股', '美股'
    up_count INTEGER DEFAULT 0,
    down_count INTEGER DEFAULT 0,
    flat_count INTEGER DEFAULT 0,
    limit_up INTEGER DEFAULT 0,
    limit_down INTEGER DEFAULT 0,
    up_ratio REAL DEFAULT 0,
    indices TEXT,  -- JSON 格式存储指数数据
    metadata TEXT,  -- JSON 格式存储额外数据
    created_at TEXT NOT NULL,
    updated_at TEXT
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_reports_date ON daily_reports(report_date);
CREATE INDEX IF NOT EXISTS idx_reports_type ON daily_reports(report_type);
CREATE INDEX IF NOT EXISTS idx_reports_date_type ON daily_reports(report_date, report_type);
CREATE INDEX IF NOT EXISTS idx_market_summary_date ON market_summary(date);
CREATE INDEX IF NOT EXISTS idx_market_summary_market ON market_summary(market);

-- 插入默认监控标的
INSERT OR IGNORE INTO symbols (symbol, name, market, category) VALUES
-- A股指数
('sh000001', '上证指数', 'A股', 'index'),
('sz399006', '创业板指', 'A股', 'index'),
('sh000300', '沪深300', 'A股', 'index'),
('sh000688', '科创50', 'A股', 'index'),
('sz399001', '深证成指', 'A股', 'index'),
('sh000016', '上证50', 'A股', 'index'),

-- 港股指数
('hk.HSI', '恒生指数', '港股', 'index'),
('hk.HSCEI', '恒生国企', '港股', 'index'),
('hk.HSTECH', '恒生科技', '港股', 'index'),

-- 美股指数
('US.SPX', '标普500', '美股', 'index'),
('US.IXIC', '纳斯达克', '美股', 'index'),
('US.DJI', '道琼斯', '美股', 'index'),

-- A股个股
('000001', '平安银行', 'A股', 'stock'),
('600519', '贵州茅台', 'A股', 'stock'),
('000858', '五粮液', 'A股', 'stock'),
('002594', '比亚迪', 'A股', 'stock'),
('300750', '宁德时代', 'A股', 'stock'),
('601012', '隆基绿能', 'A股', 'stock'),

-- 港股个股
('00700', '腾讯控股', '港股', 'stock'),
('09988', '阿里巴巴', '港股', 'stock'),
('03690', '美团', '港股', 'stock'),
('01810', '小米集团', '港股', 'stock'),

-- 美股个股
('TSLA', '特斯拉', '美股', 'stock'),
('NVDA', '英伟达', '美股', 'stock'),
('AAPL', '苹果', '美股', 'stock'),
('MSFT', '微软', '美股', 'stock'),
('GOOGL', '谷歌', '美股', 'stock'),
('AMZN', '亚马逊', '美股', 'stock'),
('META', 'Meta', '美股', 'stock'),
('BABA', '阿里巴巴', '美股', 'stock');
