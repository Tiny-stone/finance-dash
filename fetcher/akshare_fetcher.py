"""
A 股/港股数据抓取 - 使用 AKShare
优化：批量获取 + 内存缓存（5 分钟有效期）
"""
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import time
from functools import lru_cache

# 缓存时间戳
_cache_time = {}
_cache_data = {}
CACHE_TTL = 300  # 5 分钟缓存


def _is_cache_valid(key: str) -> bool:
    """检查缓存是否有效"""
    if key not in _cache_time:
        return False
    return (datetime.now() - _cache_time[key]).total_seconds() < CACHE_TTL


def get_a_stocks_by_symbols(symbols: list) -> pd.DataFrame:
    """
    获取指定 A 股股票列表的行情（优化：只获取需要的股票）
    symbols: 股票代码列表
    """
    try:
        # 使用 akshare 的个股实时行情接口，批量获取
        # 对于少量股票，直接循环获取更快
        results = []
        for symbol in symbols:
            try:
                df = ak.stock_zh_a_spot_em()
                row = df[df['代码'] == symbol]
                if not row.empty:
                    results.append(row.iloc[0])
            except:
                continue
        return pd.DataFrame(results) if results else pd.DataFrame()
    except Exception as e:
        print(f"Error fetching A 股 stocks by symbols: {e}")
        return pd.DataFrame()


def get_all_a_stocks() -> pd.DataFrame:
    """
    批量获取所有 A 股行情（用于批量查询优化）
    优化：带缓存，首次获取后 5 分钟内直接返回缓存
    """
    cache_key = 'a_stocks'
    if _is_cache_valid(cache_key):
        cached = _cache_data.get(cache_key, pd.DataFrame())
        if not cached.empty:
            return cached

    try:
        print(f"[{datetime.now()}] 获取全量 A 股数据（首次加载，约需 2-3 分钟）...")
        df = ak.stock_zh_a_spot_em()
        _cache_time[cache_key] = datetime.now()
        _cache_data[cache_key] = df
        print(f"[{datetime.now()}] ✓ 获取完成，共 {len(df)} 只股票")
        return df
    except Exception as e:
        print(f"Error fetching A 股 stocks: {e}")
        return pd.DataFrame()


def get_all_hk_stocks() -> pd.DataFrame:
    """
    批量获取所有港股行情
    """
    cache_key = 'hk_stocks'
    if _is_cache_valid(cache_key):
        return _cache_data.get(cache_key, pd.DataFrame())

    try:
        df = ak.stock_hk_spot_em()
        _cache_time[cache_key] = datetime.now()
        _cache_data[cache_key] = df
        return df
    except Exception as e:
        print(f"Error fetching HK stocks: {e}")
        return pd.DataFrame()


def get_stocks_by_symbols(symbols: list, market: str = 'A 股') -> list:
    """
    批量获取指定股票列表的行情
    symbols: 股票代码列表
    market: 市场 (A 股/港股)
    """
    results = []

    if market == 'A 股':
        df = get_all_a_stocks()
        symbol_col, name_col = '代码', '名称'
    else:  # 港股
        df = get_all_hk_stocks()
        symbol_col, name_col = '代码', '名称'

    if df.empty:
        return results

    for symbol in symbols:
        row = df[df[symbol_col] == symbol]
        if not row.empty:
            r = row.iloc[0]
            results.append({
                'symbol': symbol,
                'name': r[name_col],
                'price': float(r['最新价']),
                'change': float(r['涨跌额']),
                'change_pct': float(r['涨跌幅']),
                'volume': float(r['成交量']),
                'amount': float(r['成交额']),
                'high': float(r['最高']),
                'low': float(r['最低']),
                'open': float(r['今开']),
                'prev_close': float(r['昨收']),
            })

    return results


def get_stock_spot(symbol: str) -> dict:
    """
    获取个股实时行情（从批量数据中获取）
    symbol: 股票代码 (如：000001, 00700)
    """
    try:
        # A 股
        if symbol.isdigit() and (symbol.startswith('0') or symbol.startswith('3') or symbol.startswith('6')):
            df = get_all_a_stocks()
            if not df.empty:
                row = df[df['代码'] == symbol]
                if not row.empty:
                    return {
                        'symbol': symbol,
                        'name': row['名称'].values[0],
                        'price': float(row['最新价'].values[0]),
                        'change': float(row['涨跌额'].values[0]),
                        'change_pct': float(row['涨跌幅'].values[0]),
                        'volume': float(row['成交量'].values[0]),
                        'amount': float(row['成交额'].values[0]),
                        'high': float(row['最高'].values[0]),
                        'low': float(row['最低'].values[0]),
                        'open': float(row['今开'].values[0]),
                        'prev_close': float(row['昨收'].values[0]),
                        'turnover_rate': float(row['换手率'].values[0]) if '换手率' in row.columns else 0,
                    }

        # 港股
        elif symbol.isdigit() and len(symbol) <= 5:
            df = get_all_hk_stocks()
            if not df.empty:
                row = df[df['代码'] == symbol]
                if not row.empty:
                    return {
                        'symbol': symbol,
                        'name': row['名称'].values[0],
                        'price': float(row['最新价'].values[0]),
                        'change': float(row['涨跌额'].values[0]),
                        'change_pct': float(row['涨跌幅'].values[0]),
                        'volume': float(row['成交量'].values[0]),
                        'amount': float(row['成交额'].values[0]),
                        'high': float(row['最高'].values[0]),
                        'low': float(row['最低'].values[0]),
                        'open': float(row['今开'].values[0]),
                        'prev_close': float(row['昨收'].values[0]),
                    }
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")

    return None


def get_all_a_stock_indices() -> pd.DataFrame:
    """
    批量获取所有 A 股指数行情（用于批量查询优化）
    """
    cache_key = 'a_stock_indices'
    if _is_cache_valid(cache_key):
        return _cache_data.get(cache_key, pd.DataFrame())

    try:
        df = ak.stock_zh_index_spot_em()
        _cache_time[cache_key] = datetime.now()
        _cache_data[cache_key] = df
        return df
    except Exception as e:
        print(f"Error fetching A 股 indices: {e}")
        return pd.DataFrame()


def get_all_hk_indices() -> pd.DataFrame:
    """
    批量获取所有港股指数行情
    """
    cache_key = 'hk_indices'
    if _is_cache_valid(cache_key):
        return _cache_data.get(cache_key, pd.DataFrame())

    try:
        df = ak.stock_hk_index_spot_em()
        _cache_time[cache_key] = datetime.now()
        _cache_data[cache_key] = df
        return df
    except Exception as e:
        print(f"Error fetching HK indices: {e}")
        return pd.DataFrame()


def get_index_spot(index_code: str) -> dict:
    """
    获取指数行情（从批量数据中获取）
    index_code: 指数代码 (如：sh000001, hk.HSI, US.SPX)
    """
    try:
        # A 股指数
        if index_code.startswith('sh') or index_code.startswith('sz'):
            df = get_all_a_stock_indices()
            if not df.empty:
                row = df[df['代码'] == index_code]
                if not row.empty:
                    return {
                        'symbol': index_code,
                        'name': row['名称'].values[0],
                        'price': float(row['最新价'].values[0]),
                        'change': float(row['涨跌额'].values[0]),
                        'change_pct': float(row['涨跌幅'].values[0]),
                        'volume': float(row['成交量'].values[0]),
                        'amount': float(row['成交额'].values[0]),
                    }

        # 港股指数
        elif index_code.startswith('hk.'):
            df = get_all_hk_indices()
            if not df.empty:
                symbol = index_code.replace('hk.', '')
                row = hk_indices_df[hk_indices_df['代码'] == symbol]
                if not row.empty:
                    return {
                        'symbol': index_code,
                        'name': row['名称'].values[0],
                        'price': float(row['最新价'].values[0]),
                        'change': float(row['涨跌额'].values[0]),
                        'change_pct': float(row['涨跌幅'].values[0]),
                    }
    except Exception as e:
        print(f"Error fetching index {index_code}: {e}")

    return None


def get_stock_history(symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    获取历史行情
    symbol: 股票代码
    start_date: 开始日期 YYYY-MM-DD
    end_date: 结束日期 YYYY-MM-DD
    """
    try:
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')

        # A 股历史行情
        if symbol.isdigit() and (symbol.startswith('0') or symbol.startswith('3') or symbol.startswith('6')):
            df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start_date, end_date=end_date)
            return df

        # 港股历史行情
        elif symbol.isdigit() and len(symbol) <= 5:
            df = ak.stock_hk_daily(symbol=symbol, period="daily", start_date=start_date, end_date=end_date)
            return df
    except Exception as e:
        print(f"Error fetching history for {symbol}: {e}")

    return pd.DataFrame()


def get_news_flash() -> list:
    """
    获取财经新闻快讯
    """
    try:
        # 东方财富快讯
        df = ak.stock_info_global_cls(symbol="全部")
        news_list = []
        for _, row in df.head(20).iterrows():
            news_list.append({
                'title': row.get('标题', ''),
                'content': row.get('内容', ''),
                'source': '东方财富',
                'publish_time': datetime.now(),
                'category': '宏观',
            })
        return news_list
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []


def get_market_summary() -> dict:
    """
    获取市场概览（带缓存）
    """
    cache_key = 'market_summary'

    # 检查缓存
    if _is_cache_valid(cache_key):
        return _cache_data.get(cache_key, {})

    try:
        # A 股涨跌家数
        df = ak.stock_zh_a_spot_em()
        total = len(df)
        up = len(df[df['涨跌幅'] > 0])
        down = len(df[df['涨跌幅'] < 0])
        flat = len(df[df['涨跌幅'] == 0])

        # 涨停跌停
        limit_up = len(df[df['涨跌幅'] >= 9.8])
        limit_down = len(df[df['涨跌幅'] <= -9.8])

        result = {
            'market': 'A 股',
            'total': total,
            'up': up,
            'down': down,
            'flat': flat,
            'limit_up': limit_up,
            'limit_down': limit_down,
            'up_ratio': round(up / total * 100, 2) if total > 0 else 0,
        }

        # 保存缓存
        _cache_time[cache_key] = datetime.now()
        _cache_data[cache_key] = result

        return result
    except Exception as e:
        print(f"Error fetching market summary: {e}")
        return {}
