"""
D1 推送客户端 - 将抓取的数据推送到 Cloudflare Workers API
"""
import requests
import json
import os
from datetime import datetime


class D1PushClient:
    """推送数据到 D1 数据库的客户端"""
    
    def __init__(self, api_base=None, secret=None):
        self.api_base = api_base or os.getenv('D1_API_BASE', 'https://finance-dash.your-account.workers.dev')
        self.secret = secret or os.getenv('D1_FETCHER_SECRET', 'your-secret-key')
        
    def _headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.secret}'
        }
    
    def push_report(self, report_date, report_type, content, summary=None, metadata=None):
        """
        推送日报到 D1
        
        Args:
            report_date: 报告日期 (YYYY-MM-DD)
            report_type: 报告类型 ('noon' 或 'daily')
            content: 报告内容
            summary: 摘要（可选）
            metadata: 额外元数据（可选，字典格式）
        """
        url = f"{self.api_base}/api/internal/push-report"
        
        payload = {
            'report_date': report_date,
            'report_type': report_type,
            'content': content,
            'summary': summary,
            'metadata': metadata
        }
        
        try:
            response = requests.post(url, headers=self._headers(), json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            print(f"✓ 报告推送成功: {report_date} {report_type} - {result.get('action')}")
            return result
        except requests.exceptions.RequestException as e:
            print(f"✗ 报告推送失败: {e}")
            raise
    
    def push_market_summary(self, date, market, up_count, down_count, flat_count=0, 
                           limit_up=0, limit_down=0, indices=None, metadata=None):
        """
        推送市场概览数据到 D1
        
        Args:
            date: 日期 (YYYY-MM-DD)
            market: 市场 ('A股', '港股', '美股')
            up_count: 上涨家数
            down_count: 下跌家数
            flat_count: 平盘家数
            limit_up: 涨停家数
            limit_down: 跌停家数
            indices: 指数数据（可选，字典格式）
            metadata: 额外元数据（可选）
        """
        url = f"{self.api_base}/api/internal/push-market-data"
        
        payload = {
            'date': date,
            'market': market,
            'up_count': up_count,
            'down_count': down_count,
            'flat_count': flat_count,
            'limit_up': limit_up,
            'limit_down': limit_down,
            'indices': indices,
            'metadata': metadata
        }
        
        try:
            response = requests.post(url, headers=self._headers(), json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            print(f"✓ 市场数据推送成功: {date} {market} - {result.get('action')}")
            return result
        except requests.exceptions.RequestException as e:
            print(f"✗ 市场数据推送失败: {e}")
            raise
    
    def check_health(self):
        """检查 API 健康状态"""
        url = f"{self.api_base}/api/health"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"✗ API 健康检查失败: {e}")
            return None


if __name__ == '__main__':
    # 测试推送
    client = D1PushClient()
    
    # 检查 API 状态
    health = client.check_health()
    if health:
        print(f"API 状态: {health}")
    
    # 测试推送报告
    # client.push_report(
    #     report_date=datetime.now().strftime('%Y-%m-%d'),
    #     report_type='noon',
    #     content='测试报告内容',
    #     summary='测试摘要'
    # )
