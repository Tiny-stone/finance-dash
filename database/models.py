"""
数据库模型 - SQLite
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'database', 'finance.db')

engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Symbol(Base):
    """监控标的表"""
    __tablename__ = 'symbols'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), unique=True, nullable=False, comment='股票代码')
    name = Column(String(100), nullable=False, comment='名称')
    market = Column(String(20), nullable=False, comment='市场：A 股/港股/美股/指数')
    category = Column(String(50), default='stock', comment='类别：stock/index/crypto')
    is_active = Column(Integer, default=1, comment='是否启用：1=是，0=否')
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class DailyQuote(Base):
    """每日行情表"""
    __tablename__ = 'daily_quotes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True, comment='股票代码')
    trade_date = Column(String(10), nullable=False, index=True, comment='交易日期 YYYY-MM-DD')
    open = Column(Float, comment='开盘价')
    high = Column(Float, comment='最高价')
    low = Column(Float, comment='最低价')
    close = Column(Float, comment='收盘价')
    volume = Column(Float, comment='成交量')
    amount = Column(Float, comment='成交额')
    change_pct = Column(Float, comment='涨跌幅%')
    change = Column(Float, comment='涨跌额')
    turnover_rate = Column(Float, comment='换手率%')
    created_at = Column(DateTime, default=datetime.now)


class DailyReport(Base):
    """日报表"""
    __tablename__ = 'daily_reports'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    report_date = Column(String(10), unique=True, nullable=False, index=True, comment='报告日期 YYYY-MM-DD')
    report_type = Column(String(20), default='daily', comment='报告类型：daily/weekly/monthly')
    content = Column(Text, comment='报告内容（Markdown 格式）')
    summary = Column(Text, comment='摘要')
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class NewsFlash(Base):
    """新闻快讯表"""
    __tablename__ = 'news_flashes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False, comment='标题')
    content = Column(Text, comment='内容')
    source = Column(String(100), comment='来源')
    publish_time = Column(DateTime, comment='发布时间')
    category = Column(String(50), comment='分类：宏观/行业/公司/政策')
    impact = Column(String(20), default='normal', comment='影响程度：high/medium/normal')
    created_at = Column(DateTime, default=datetime.now)


def init_db():
    """初始化数据库"""
    Base.metadata.create_all(engine)


def get_session():
    """获取数据库会话"""
    return SessionLocal()
