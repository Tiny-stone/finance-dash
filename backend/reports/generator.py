"""
报告生成模块 - 生成午间和收盘报告
"""
from datetime import datetime
from typing import List, Dict
from backend.data.fetcher import DataFetcher
import json

class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        self.fetcher = DataFetcher()
    
    def _format_change(self, change_pct: float) -> str:
        """格式化涨跌幅，带颜色标记"""
        if change_pct > 0:
            return f"+{change_pct:.2f}% 📈"
        elif change_pct < 0:
            return f"{change_pct:.2f}% 📉"
        else:
            return "0.00% ➖"
    
    def _generate_summary(self, data_list: List[Dict]) -> str:
        """生成数据摘要"""
        if not data_list:
            return "暂无数据"
        
        up_count = sum(1 for d in data_list if d.get('change_pct', 0) > 0)
        down_count = sum(1 for d in data_list if d.get('change_pct', 0) < 0)
        flat_count = len(data_list) - up_count - down_count
        
        avg_change = sum(d.get('change_pct', 0) for d in data_list) / len(data_list)
        
        # 找出涨跌幅最大
        sorted_by_change = sorted(data_list, key=lambda x: x.get('change_pct', 0), reverse=True)
        top_gainer = sorted_by_change[0] if sorted_by_change else None
        top_loser = sorted_by_change[-1] if sorted_by_change else None
        
        summary = f"""
📊 **市场整体情况**
- 上涨: {up_count} 只/指数
- 下跌: {down_count} 只/指数  
- 平盘: {flat_count} 只/指数
- 平均涨跌幅: {self._format_change(avg_change)}

🏆 **涨幅最大**: {top_gainer['name'] if top_gainer else 'N/A'} ({self._format_change(top_gainer.get('change_pct', 0)) if top_gainer else 'N/A'})
📉 **跌幅最大**: {top_loser['name'] if top_loser else 'N/A'} ({self._format_change(top_loser.get('change_pct', 0)) if top_loser else 'N/A'})
"""
        return summary
    
    def generate_noon_report(self, watchlist: List[Dict] = None) -> Dict:
        """生成午间报告 (11:30)"""
        now = datetime.now()
        date_str = now.strftime("%Y年%m月%d日")
        
        # 获取A股主要指数
        a_share_indices = self.fetcher.get_all_a_share_indices()
        
        # 获取关注列表数据
        watchlist_data = []
        if watchlist:
            watchlist_data = self.fetcher.fetch_watchlist(watchlist)
        
        # 生成报告内容
        report_content = f"""# 📈 午间市场总结 ({date_str})

## 🕦 报告时间
{now.strftime("%Y-%m-%d %H:%M")}

## 🇨🇳 A股主要指数

"""
        
        for idx in a_share_indices:
            report_content += f"- **{idx['name']}**: {idx['price']:.2f} ({self._format_change(idx.get('change_pct', 0))})\n"
        
        report_content += f"\n## 📋 市场摘要\n{self._generate_summary(a_share_indices)}\n"
        
        if watchlist_data:
            report_content += f"\n## ⭐ 关注标的\n\n"
            for item in watchlist_data:
                report_content += f"- **{item['name']}** ({item['symbol']}): {item['price']:.2f} ({self._format_change(item.get('change_pct', 0))})\n"
            
            report_content += f"\n### 关注列表摘要\n{self._generate_summary(watchlist_data)}\n"
        
        report_content += f"""
---
💡 **提示**: 下午13:00 A股继续交易，15:00收盘后将生成全天总结报告。
"""
        
        return {
            "title": f"午间市场总结 - {date_str}",
            "report_type": "noon",
            "report_date": now.strftime("%Y-%m-%d"),
            "content": report_content,
            "summary": self._generate_summary(a_share_indices),
            "data_snapshot": json.dumps({
                "a_share_indices": a_share_indices,
                "watchlist": watchlist_data,
            }, ensure_ascii=False),
        }
    
    def generate_close_report(self, watchlist: List[Dict] = None) -> Dict:
        """生成收盘报告 (收盘后)"""
        now = datetime.now()
        date_str = now.strftime("%Y年%m月%d日")
        
        # 获取A股主要指数
        a_share_indices = self.fetcher.get_all_a_share_indices()
        
        # 获取全球主要指数
        global_indices = self.fetcher.get_all_global_indices()
        
        # 获取关注列表数据
        watchlist_data = []
        if watchlist:
            watchlist_data = self.fetcher.fetch_watchlist(watchlist)
        
        # 合并所有数据用于摘要
        all_data = a_share_indices + global_indices + watchlist_data
        
        # 生成报告内容
        report_content = f"""# 📊 全天市场总结 ({date_str})

## 🕐 报告时间
{now.strftime("%Y-%m-%d %H:%M")}

## 🇨🇳 A股主要指数 (收盘)

"""
        
        for idx in a_share_indices:
            report_content += f"- **{idx['name']}**: {idx['price']:.2f} ({self._format_change(idx.get('change_pct', 0))})\n"
        
        report_content += f"\n## 🌍 全球主要指数\n\n"
        
        for idx in global_indices:
            report_content += f"- **{idx['name']}**: {idx['price']:.2f} ({self._format_change(idx.get('change_pct', 0))})\n"
        
        report_content += f"\n## 📋 市场摘要\n{self._generate_summary(all_data)}\n"
        
        if watchlist_data:
            report_content += f"\n## ⭐ 关注标的\n\n"
            for item in watchlist_data:
                report_content += f"- **{item['name']}** ({item['symbol']}): {item['price']:.2f} ({self._format_change(item.get('change_pct', 0))})\n"
        
        report_content += f"""
---
📝 **免责声明**: 本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。
"""
        
        return {
            "title": f"全天市场总结 - {date_str}",
            "report_type": "close",
            "report_date": now.strftime("%Y-%m-%d"),
            "content": report_content,
            "summary": self._generate_summary(all_data),
            "data_snapshot": json.dumps({
                "a_share_indices": a_share_indices,
                "global_indices": global_indices,
                "watchlist": watchlist_data,
            }, ensure_ascii=False),
        }
    
    def generate_custom_report(self, symbols: List[str], report_name: str = "自定义报告") -> Dict:
        """生成自定义报告"""
        now = datetime.now()
        date_str = now.strftime("%Y年%m月%d日")
        
        # 构建关注列表格式
        watchlist = []
        for symbol in symbols:
            # 根据代码判断市场
            if symbol.startswith('^'):
                market = 'global'
            elif symbol.isdigit():
                if len(symbol) == 5:  # 港股
                    market = 'hk'
                else:  # A股
                    market = 'a_share'
            else:
                market = 'us'
            watchlist.append({"symbol": symbol, "market": market})
        
        data = self.fetcher.fetch_watchlist(watchlist)
        
        report_content = f"""# 📋 {report_name} ({date_str})

## 🕐 报告时间
{now.strftime("%Y-%m-%d %H:%M")}

## 📈 标的行情

"""
        
        for item in data:
            report_content += f"- **{item['name']}** ({item['symbol']}): {item['price']:.2f} ({self._format_change(item.get('change_pct', 0))})\n"
        
        report_content += f"\n## 📊 摘要\n{self._generate_summary(data)}\n"
        
        return {
            "title": f"{report_name} - {date_str}",
            "report_type": "custom",
            "report_date": now.strftime("%Y-%m-%d"),
            "content": report_content,
            "summary": self._generate_summary(data),
            "data_snapshot": json.dumps({"data": data}, ensure_ascii=False),
        }


# 便捷函数
def generator():
    """获取报告生成器实例"""
    return ReportGenerator()


if __name__ == "__main__":
    # 测试报告生成
    gen = ReportGenerator()
    
    print("=== 生成午间报告 ===")
    noon_report = gen.generate_noon_report()
    print(noon_report['content'])
    
    print("\n\n=== 生成收盘报告 ===")
    close_report = gen.generate_close_report()
    print(close_report['content'])