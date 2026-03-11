"""
Finance Dash 抓取服务
提供 A 股、港股、美股数据抓取和报告生成功能
"""

from .akshare_fetcher import (
    get_stock_spot,
    get_index_spot,
    get_market_summary,
    get_news_flash,
    get_all_a_stocks,
    get_all_hk_stocks,
    get_all_a_stock_indices,
    get_all_hk_indices,
)

from .yfinance_fetcher import (
    get_stock_spot as get_us_stock_spot,
    get_us_indices_batch,
    get_market_status,
)

from .report_generator import ReportGenerator
from .push_client import D1PushClient

__all__ = [
    'get_stock_spot',
    'get_index_spot',
    'get_market_summary',
    'get_news_flash',
    'get_all_a_stocks',
    'get_all_hk_stocks',
    'get_all_a_stock_indices',
    'get_all_hk_indices',
    'get_us_stock_spot',
    'get_us_indices_batch',
    'get_market_status',
    'ReportGenerator',
    'D1PushClient',
]
