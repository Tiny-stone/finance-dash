"""
定时任务调度器
- 午间速览：11:30（A 股午盘收盘后）
- 全天复盘：15:30（A 股收盘后）
- 美股复盘：次日 10:00（美股收盘后）
"""
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import sys
import os

# 添加项目根目录到路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# 直接导入
sys.path.insert(0, os.path.join(BASE_DIR, 'database'))
sys.path.insert(0, os.path.join(BASE_DIR, 'backend'))

from reports.report_generator import ReportGenerator
from models import init_db


def job_noon_report():
    """午间速览任务"""
    print(f"\n[{datetime.now()}] 开始生成午间速览...")
    try:
        generator = ReportGenerator()
        report = generator.generate_noon_report()
        generator.save_report(report, report_type='noon')
        print(f"[{datetime.now()}] 午间速览生成完成")
        
        # TODO: 发送到 Feishu/邮件
        # send_to_feishu(report)
    except Exception as e:
        print(f"[{datetime.now()}] 午间速览生成失败：{e}")


def job_daily_report():
    """全天复盘任务"""
    print(f"\n[{datetime.now()}] 开始生成全天复盘...")
    try:
        generator = ReportGenerator()
        report = generator.generate_daily_report()
        generator.save_report(report, report_type='daily')
        print(f"[{datetime.now()}] 全天复盘生成完成")
        
        # TODO: 发送到 Feishu/邮件
        # send_to_feishu(report)
    except Exception as e:
        print(f"[{datetime.now()}] 全天复盘生成失败：{e}")


def job_us_report():
    """美股复盘任务（次日早）"""
    print(f"\n[{datetime.now()}] 开始生成美股复盘...")
    try:
        # TODO: 实现美股专属报告
        print("美股复盘待实现")
    except Exception as e:
        print(f"[{datetime.now()}] 美股复盘生成失败：{e}")


def warmup_cache():
    """预加载数据缓存（加速首次报告生成）"""
    print("\n" + "=" * 60)
    print("预加载数据缓存...")
    print("=" * 60)
    
    try:
        from backend.data.akshare_fetcher import get_all_a_stocks, get_all_hk_stocks, get_all_a_stock_indices, get_all_hk_indices, get_market_summary
        from backend.data.yfinance_fetcher import get_us_indices_batch
        
        print("• 加载 A 股数据...")
        get_all_a_stocks()
        
        print("• 加载港股数据...")
        get_all_hk_stocks()
        
        print("• 加载 A 股指数...")
        get_all_a_stock_indices()
        
        print("• 加载港股指数...")
        get_all_hk_indices()
        
        print("• 加载美股指数...")
        get_us_indices_batch()
        
        print("• 加载市场概览...")
        get_market_summary()
        
        print("✓ 缓存预加载完成\n")
    except Exception as e:
        print(f"✗ 缓存预加载失败：{e}\n")


def start_scheduler():
    """启动定时任务"""
    # 初始化数据库
    init_db()
    print("✓ 数据库初始化完成")
    
    # 预加载缓存
    warmup_cache()
    
    # 创建调度器
    scheduler = BlockingScheduler(timezone='Asia/Shanghai')
    
    # 午间速览：周一到周五 11:30
    scheduler.add_job(
        job_noon_report,
        CronTrigger(hour=11, minute=30, day_of_week='mon-fri'),
        id='noon_report',
        name='午间速览'
    )
    print("✓ 午间速览任务已注册 (11:30)")
    
    # 全天复盘：周一到周五 15:30
    scheduler.add_job(
        job_daily_report,
        CronTrigger(hour=15, minute=30, day_of_week='mon-fri'),
        id='daily_report',
        name='全天复盘'
    )
    print("✓ 全天复盘任务已注册 (15:30)")
    
    # 美股复盘：周一到周五 10:00（美股次日早）
    scheduler.add_job(
        job_us_report,
        CronTrigger(hour=10, minute=0, day_of_week='mon-fri'),
        id='us_report',
        name='美股复盘'
    )
    print("✓ 美股复盘任务已注册 (10:00)")
    
    print("\n" + "=" * 60)
    print("定时任务调度器已启动")
    print("按 Ctrl+C 退出")
    print("=" * 60 + "\n")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n调度器已停止")


if __name__ == '__main__':
    start_scheduler()
