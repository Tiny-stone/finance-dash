#!/usr/bin/env python3
"""
抓取服务主入口
用于定时任务或手动触发数据抓取和报告生成
"""
import sys
import os
from datetime import datetime

# 确保可以导入 fetcher 模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from report_generator import ReportGenerator
from akshare_fetcher import get_market_summary
from push_client import D1PushClient


def fetch_and_push_market_data():
    """获取并推送市场概览数据"""
    print(f"[{datetime.now()}] 开始获取市场数据...")

    generator = ReportGenerator()

    try:
        # 推送市场概览
        generator.push_market_summary()
        print(f"[{datetime.now()}] ✓ 市场数据推送完成")
        return True
    except Exception as e:
        print(f"[{datetime.now()}] ✗ 市场数据推送失败: {e}")
        return False


def generate_and_push_noon_report():
    """生成并推送午间速览"""
    print(f"[{datetime.now()}] 开始生成午间速览...")

    generator = ReportGenerator()

    try:
        # 生成报告
        content = generator.generate_noon_report()

        # 推送到 D1
        generator.save_and_push_report(content, 'noon')

        print(f"[{datetime.now()}] ✓ 午间速览推送完成")
        print("\n" + "="*60)
        print(content[:500] + "..." if len(content) > 500 else content)
        print("="*60)
        return True
    except Exception as e:
        print(f"[{datetime.now()}] ✗ 午间速览生成失败: {e}")
        return False


def generate_and_push_daily_report():
    """生成并推送全天复盘"""
    print(f"[{datetime.now()}] 开始生成全天复盘...")

    generator = ReportGenerator()

    try:
        # 生成报告
        content = generator.generate_daily_report()

        # 推送到 D1
        generator.save_and_push_report(content, 'daily')

        print(f"[{datetime.now()}] ✓ 全天复盘推送完成")
        print("\n" + "="*60)
        print(content[:500] + "..." if len(content) > 500 else content)
        print("="*60)
        return True
    except Exception as e:
        print(f"[{datetime.now()}] ✗ 全天复盘生成失败: {e}")
        return False


def check_api_health():
    """检查 D1 API 健康状态"""
    client = D1PushClient()
    health = client.check_health()

    if health:
        print(f"[{datetime.now()}] ✓ API 健康状态: {health}")
        return True
    else:
        print(f"[{datetime.now()}] ✗ API 健康检查失败")
        return False


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Finance Dash 抓取服务 - 获取市场数据并推送到 D1',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py noon              # 生成午间速览
  python main.py daily             # 生成全天复盘
  python main.py market            # 推送市场概览数据
  python main.py health            # 检查 API 健康状态
  python main.py all               # 执行全部任务
        """
    )

    parser.add_argument(
        'command',
        choices=['noon', 'daily', 'market', 'health', 'all'],
        help='要执行的命令'
    )

    parser.add_argument(
        '--env',
        default='.env',
        help='环境变量文件路径 (默认: .env)'
    )

    args = parser.parse_args()

    # 加载环境变量
    if os.path.exists(args.env):
        from dotenv import load_dotenv
        load_dotenv(args.env)
        print(f"[{datetime.now()}] 已加载环境变量: {args.env}")

    print(f"[{datetime.now()}] Finance Dash 抓取服务启动")
    print("-" * 60)

    success = True

    if args.command == 'health':
        success = check_api_health()

    elif args.command == 'market':
        success = fetch_and_push_market_data()

    elif args.command == 'noon':
        success = generate_and_push_noon_report()

    elif args.command == 'daily':
        success = generate_and_push_daily_report()

    elif args.command == 'all':
        # 执行全部任务
        print("执行全部任务...\n")

        # 1. 检查 API
        if not check_api_health():
            print("API 不可用，中止任务")
            sys.exit(1)

        # 2. 推送市场数据
        fetch_and_push_market_data()
        print()

        # 3. 生成报告（根据时间决定）
        hour = datetime.now().hour
        if 11 <= hour < 15:
            # 午间时段
            generate_and_push_noon_report()
        else:
            # 其他时段生成全天复盘
            generate_and_push_daily_report()

    print("-" * 60)
    print(f"[{datetime.now()}] 任务完成")

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
