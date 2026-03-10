"""
日报生成器 - 生成午间速览和全天复盘
优化：批量获取数据，减少 API 调用次数
"""
from datetime import datetime, timedelta
from typing import List, Dict
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.akshare_fetcher import (
    get_stock_spot, get_index_spot, get_market_summary, get_news_flash,
    get_all_a_stocks, get_all_hk_stocks, get_all_a_stock_indices, get_all_hk_indices,
    get_stocks_by_symbols
)
from data.yfinance_fetcher import get_stock_spot as get_us_stock_spot, get_market_status, get_us_indices_batch


class ReportGenerator:
    """日报生成器"""
    
    def __init__(self, db_session=None):
        self.db_session = db_session
        self.symbols = self._load_symbols()
    
    def _load_symbols(self) -> List[Dict]:
        """加载监控标的列表"""
        # 默认标的池（可从数据库加载）
        return [
            # A 股指数
            {'symbol': 'sh000001', 'name': '上证指数', 'market': 'A 股', 'type': 'index'},
            {'symbol': 'sz399006', 'name': '创业板指', 'market': 'A 股', 'type': 'index'},
            {'symbol': 'sh000300', 'name': '沪深 300', 'market': 'A 股', 'type': 'index'},
            {'symbol': 'sh000688', 'name': '科创 50', 'market': 'A 股', 'type': 'index'},
            
            # 港股指数
            {'symbol': 'hk.HSI', 'name': '恒生指数', 'market': '港股', 'type': 'index'},
            {'symbol': 'hk.HSCEI', 'name': '恒生国企', 'market': '港股', 'type': 'index'},
            
            # 美股指数
            {'symbol': 'US.SPX', 'name': '标普 500', 'market': '美股', 'type': 'index'},
            {'symbol': 'US.IXIC', 'name': '纳斯达克', 'market': '美股', 'type': 'index'},
            {'symbol': 'US.DJI', 'name': '道琼斯', 'market': '美股', 'type': 'index'},
            
            # A 股个股（示例）
            {'symbol': '000001', 'name': '平安银行', 'market': 'A 股', 'type': 'stock'},
            {'symbol': '600519', 'name': '贵州茅台', 'market': 'A 股', 'type': 'stock'},
            {'symbol': '00700', 'name': '腾讯控股', 'market': '港股', 'type': 'stock'},
            {'symbol': '09988', 'name': '阿里巴巴', 'market': '港股', 'type': 'stock'},
            {'symbol': 'TSLA', 'name': '特斯拉', 'market': '美股', 'type': 'stock'},
            {'symbol': 'NVDA', 'name': '英伟达', 'market': '美股', 'type': 'stock'},
        ]
    
    def generate_noon_report(self, date: str = None) -> str:
        """
        生成午间速览（11:30 A 股收盘后）
        优化：批量获取数据，减少 API 调用
        """
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        report = []
        report.append(f"📊 午间速览 | {date}")
        report.append("=" * 60)
        report.append("")
        
        # 1. A 股市场概览
        report.append("🇨🇳 A 股市场")
        report.append("-" * 40)
        market_summary = get_market_summary()
        if market_summary:
            report.append(f"涨跌比：{market_summary.get('up', 0)}↑ / {market_summary.get('down', 0)}↓")
            report.append(f"涨停/跌停：{market_summary.get('limit_up', 0)} / {market_summary.get('limit_down', 0)}")
            report.append(f"上涨比例：{market_summary.get('up_ratio', 0)}%")
        report.append("")
        
        # 2. 主要指数表现（批量获取）
        report.append("📈 主要指数")
        report.append("-" * 40)
        
        # 批量获取 A 股指数
        a_indices_df = get_all_a_stock_indices()
        hk_indices_df = get_all_hk_indices()
        
        for item in self.symbols:
            if item['type'] == 'index' and item['market'] in ['A 股', '港股']:
                data = None
                if item['market'] == 'A 股' and not a_indices_df.empty:
                    row = a_indices_df[a_indices_df['代码'] == item['symbol']]
                    if not row.empty:
                        r = row.iloc[0]
                        data = {
                            'name': r['名称'],
                            'price': float(r['最新价']),
                            'change_pct': float(r['涨跌幅']),
                        }
                elif item['market'] == '港股' and not hk_indices_df.empty:
                    symbol = item['symbol'].replace('hk.', '')
                    row = hk_indices_df[hk_indices_df['代码'] == symbol]
                    if not row.empty:
                        r = row.iloc[0]
                        data = {
                            'name': r['名称'],
                            'price': float(r['最新价']),
                            'change_pct': float(r['涨跌幅']),
                        }
                
                if data:
                    sign = "↑" if data.get('change_pct', 0) > 0 else "↓" if data.get('change_pct', 0) < 0 else "−"
                    report.append(f"{data['name']}: {data['price']:.2f} {sign}{abs(data.get('change_pct', 0)):.2f}%")
        report.append("")
        
        # 3. 异动个股（从批量数据中筛选）
        report.append("⚡ 异动关注")
        report.append("-" * 40)
        a_stocks_df = get_all_a_stocks()
        if not a_stocks_df.empty:
            # 筛选涨跌幅 > 5% 的股票
            volatile = a_stocks_df[abs(a_stocks_df['涨跌幅']) > 5].head(10)
            if not volatile.empty:
                for _, row in volatile.iterrows():
                    sign = "↑" if row['涨跌幅'] > 0 else "↓"
                    report.append(f"{row['名称']}: {sign}{abs(row['涨跌幅']):.2f}% (现价：{row['最新价']})")
            else:
                report.append("今日无大幅异动个股（涨跌幅>5%）")
        else:
            report.append("（数据获取中...）")
        report.append("")
        
        # 4. 午间新闻
        report.append("📰 午间快讯")
        report.append("-" * 40)
        news = get_news_flash()
        for n in news[:5]:
            report.append(f"• {n.get('title', '')}")
        report.append("")
        
        report.append("=" * 60)
        report.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        return "\n".join(report)
    
    def generate_daily_report(self, date: str = None) -> str:
        """
        生成全天复盘（15:30 A 股收盘后）
        优化：批量获取数据，减少 API 调用
        """
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        report = []
        report.append(f"📈 全球市场日报 | {date}")
        report.append("=" * 60)
        report.append("")
        
        # 1. 核心观点
        report.append("💡 核心观点")
        report.append("-" * 40)
        report.append("（待 AI 总结生成）")
        report.append("")
        
        # 2. 全球市场概览
        report.append("🌍 全球市场")
        report.append("-" * 40)
        
        # A 股
        report.append("\n【A 股】")
        market_summary = get_market_summary()
        if market_summary:
            report.append(f"涨跌比：{market_summary.get('up', 0)}↑ / {market_summary.get('down', 0)}↓")
            report.append(f"涨停/跌停：{market_summary.get('limit_up', 0)} / {market_summary.get('limit_down', 0)}")
        
        # 港股
        report.append("\n【港股】")
        # TODO: 获取港股市场概览
        
        # 美股（前一交易日）- 批量获取
        report.append("\n【美股】")
        us_data = get_us_indices_batch()  # 批量获取，带缓存
        for item in self.symbols:
            if item['type'] == 'index' and item['market'] == '美股':
                data = us_data.get(item['symbol'])
                if data:
                    sign = "↑" if data.get('change_pct', 0) > 0 else "↓" if data.get('change_pct', 0) < 0 else "−"
                    report.append(f"{data['name']}: {data['price']:.2f} {sign}{abs(data.get('change_pct', 0)):.2f}%")
        report.append("")
        
        # 3. 主要指数（批量获取）
        report.append("📊 指数表现")
        report.append("-" * 40)
        
        a_indices_df = get_all_a_stock_indices()
        hk_indices_df = get_all_hk_indices()
        us_indices = get_us_indices_batch()  # 批量获取美股
        
        for item in self.symbols:
            if item['type'] == 'index':
                data = None
                if item['market'] == 'A 股' and not a_indices_df.empty:
                    row = a_indices_df[a_indices_df['代码'] == item['symbol']]
                    if not row.empty:
                        r = row.iloc[0]
                        data = {'name': r['名称'], 'price': float(r['最新价']), 'change_pct': float(r['涨跌幅'])}
                elif item['market'] == '港股' and not hk_indices_df.empty:
                    symbol = item['symbol'].replace('hk.', '')
                    row = hk_indices_df[hk_indices_df['代码'] == symbol]
                    if not row.empty:
                        r = row.iloc[0]
                        data = {'name': r['名称'], 'price': float(r['最新价']), 'change_pct': float(r['涨跌幅'])}
                elif item['market'] == '美股':
                    data = us_indices.get(item['symbol'])
                
                if data:
                    sign = "↑" if data.get('change_pct', 0) > 0 else "↓" if data.get('change_pct', 0) < 0 else "−"
                    report.append(f"{item['name']:12s}: {data['price']:>10.2f}  {sign}{abs(data.get('change_pct', 0)):>6.2f}%")
        report.append("")
        
        # 4. 个股监控（批量获取）
        report.append("🎯 个股监控")
        report.append("-" * 40)
        
        a_stocks_df = get_all_a_stocks()
        hk_stocks_df = get_all_hk_stocks()
        us_indices = get_us_indices_batch()  # 美股个股也用批量（如果有）
        
        for item in self.symbols:
            if item['type'] == 'stock':
                data = None
                if item['market'] == 'A 股' and not a_stocks_df.empty:
                    row = a_stocks_df[a_stocks_df['代码'] == item['symbol']]
                    if not row.empty:
                        r = row.iloc[0]
                        data = {'name': r['名称'], 'price': float(r['最新价']), 'change_pct': float(r['涨跌幅'])}
                elif item['market'] == '港股' and not hk_stocks_df.empty:
                    row = hk_stocks_df[hk_stocks_df['代码'] == item['symbol']]
                    if not row.empty:
                        r = row.iloc[0]
                        data = {'name': r['名称'], 'price': float(r['最新价']), 'change_pct': float(r['涨跌幅'])}
                elif item['market'] == '美股':
                    # 美股个股单独获取（数量少，不影响性能）
                    data = get_us_stock_spot(item['symbol'])
                
                if data:
                    sign = "↑" if data.get('change_pct', 0) > 0 else "↓" if data.get('change_pct', 0) < 0 else "−"
                    report.append(f"{data['name']:12s}: {data['price']:>10.2f}  {sign}{abs(data.get('change_pct', 0)):>6.2f}%")
        report.append("")
        
        # 5. 资金流向
        report.append("💰 资金流向")
        report.append("-" * 40)
        report.append("北向资金：待接入")
        report.append("南向资金：待接入")
        report.append("")
        
        # 6. 财经新闻
        report.append("📰 重要新闻")
        report.append("-" * 40)
        news = get_news_flash()
        for i, n in enumerate(news[:10], 1):
            report.append(f"{i}. {n.get('title', '')}")
        report.append("")
        
        # 7. 明日关注
        report.append("🔍 明日关注")
        report.append("-" * 40)
        report.append("• 经济数据：待补充")
        report.append("• 重要事件：待补充")
        report.append("")
        
        report.append("=" * 60)
        report.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(report)
    
    def save_report(self, content: str, report_type: str = 'daily'):
        """保存报告到数据库"""
        from database.models import DailyReport, get_session
        
        date = datetime.now().strftime('%Y-%m-%d')
        session = get_session()
        
        try:
            # 检查是否已存在
            existing = session.query(DailyReport).filter(
                DailyReport.report_date == date,
                DailyReport.report_type == report_type
            ).first()
            
            if existing:
                existing.content = content
                existing.updated_at = datetime.now()
            else:
                report = DailyReport(
                    report_date=date,
                    report_type=report_type,
                    content=content,
                    summary=content[:200] + "..."
                )
                session.add(report)
            
            session.commit()
            print(f"✓ 报告已保存：{report_type} - {date}")
        except Exception as e:
            session.rollback()
            print(f"✗ 保存报告失败：{e}")
        finally:
            session.close()


if __name__ == '__main__':
    # 测试生成
    generator = ReportGenerator()
    
    print("生成午间速览...")
    noon_report = generator.generate_noon_report()
    print(noon_report)
    print("\n\n")
    
    print("生成全天复盘...")
    daily_report = generator.generate_daily_report()
    print(daily_report)
