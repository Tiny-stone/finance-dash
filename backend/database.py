from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), "finance.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class WatchItem(Base):
    """用户关注的标的"""
    __tablename__ = "watch_items"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)  # 代码
    name = Column(String(100), nullable=False)  # 名称
    market = Column(String(10), nullable=False)  # a股/hk/us/index
    item_type = Column(String(20), nullable=False)  # stock/index
    created_at = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)

class DailyReport(Base):
    """每日报告"""
    __tablename__ = "daily_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    report_type = Column(String(20), nullable=False)  # noon/close
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    data_snapshot = Column(Text)  # JSON格式存储当日数据
    created_at = Column(DateTime, default=datetime.now)

class MarketData(Base):
    """市场数据快照"""
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    name = Column(String(100))
    market = Column(String(10))
    price = Column(Float)
    change = Column(Float)  # 涨跌额
    change_pct = Column(Float)  # 涨跌幅%
    volume = Column(Float)
    data_time = Column(DateTime, default=datetime.now)
    report_date = Column(String(10), index=True)

def init_db():
    """初始化数据库"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()