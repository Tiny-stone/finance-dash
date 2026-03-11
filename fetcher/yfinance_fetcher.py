"""
美股/全球指数数据抓取 - 使用 yfinance
优化：添加缓存机制 + 批量获取
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 缓存
_cache_time = {}
_cache_data = {}
CACHE_TTL = 300  # 5 分钟缓存（美股闭市时可延长）


def _is_cache_valid(key: str) -> bool:
    """检查缓存是否有效"""
    if key not in _cache_time:
        return False
    # 美股交易时段外（北京时间 22:30-次日 5:00），缓存延长到 30 分钟
    hour = datetime.now().hour
    is_us_closed = hour < 5 or hour >= 22
    ttl = 1800 if is_us_closed else CACHE_TTL
    return (datetime.now() - _cache_time[key]).total_seconds() < ttl


# 常见美股/全球指数代码映射
SYMBOL_MAP = {
    # 美股指数
    'US.SPX': '^GSPC',      # 标普 500
    'US.DJI': '^DJI',       # 道琼斯
    'US.IXIC': '^IXIC',     # 纳斯达克
    'US.RUT': '^RUT',       # 罗素 2000
    'US.VIX': '^VIX',       # 恐慌指数

    # 全球指数
    'HK.HSI': '^HSI',       # 恒生指数
    'HK.HSCEI': '^HSCEI',   # 恒生国企
    'JP.N225': '^N225',     # 日经 225
    'UK.FTSE': '^FTSE',     # 富时 100
    'DE.GDAXI': '^GDAXI',   # 德国 DAX
    'FR.FCHI': '^FCHI',     # 法国 CAC40

    # 汇率
    'FX.USDCNY': 'USDCNY=X',
    'FX.EURUSD': 'EURUSD=X',

    # 大宗商品
    'CMD.GOLD': 'GC=F',     # 黄金
    'CMD.SILVER': 'SI=F',   # 白银
    'CMD.OIL': 'CL=F',      # 原油 WTI
    'CMD.BRENT': 'BZ=F',    # 布伦特原油
    'CMD.COPPER': 'HG=F',   # 铜

    # 加密货币
    'CRYPTO.BTC': 'BTC-USD',
    'CRYPTO.ETH': 'ETH-USD',
}


def get_symbol_ticker(symbol: str) -> str:
    """获取 yfinance 代码"""
    return SYMBOL_MAP.get(symbol, symbol)


def get_us_indices_batch() -> dict:
    """
    批量获取所有美股指数（带缓存）
    优化：美股闭市时直接返回缓存，避免重复请求
    """
    cache_key = 'us_indices_batch'

    # 美股交易时段检查：北京时间 22:30-次日 5:00 为交易时间
    hour = datetime.now().hour
    is_us_trading = 22 <= hour or hour < 5

    # 非交易时段缓存 30 分钟，交易时段缓存 5 分钟
    if cache_key in _cache_time:
        ttl = 300 if is_us_trading else 1800
        if (datetime.now() - _cache_time[cache_key]).total_seconds() < ttl:
            return _cache_data.get(cache_key, {})

    # 如果已有旧缓存且非交易时段，直接返回（避免 yfinance 超时）
    if not is_us_trading and cache_key in _cache_data and _cache_data[cache_key]:
        return _cache_data[cache_key]

    results = {}
    us_symbols = [k for k in SYMBOL_MAP.keys() if k.startswith('US.')]

    try:
        # 使用 yfinance 批量下载
        tickers = yf.Tickers(' '.join([SYMBOL_MAP.get(s, s) for s in us_symbols]))

        for symbol in us_symbols:
            ticker_code = SYMBOL_MAP.get(symbol, symbol)
            try:
                ticker = tickers.tickers[ticker_code]
                hist = ticker.history(period='1d', timeout=5)
                if not hist.empty:
                    current = hist.iloc[-1]
                    info = ticker.info
                    prev_close = info.get('previousClose', current['Open'])

                    results[symbol] = {
                        'symbol': symbol,
                        'name': info.get('shortName', info.get('longName', symbol)),
                        'price': float(current['Close']),
                        'change': float(current['Close'] - prev_close),
                        'change_pct': float((current['Close'] - prev_close) / prev_close * 100),
                    }
            except Exception as e:
                print(f"Error fetching {symbol}: {e}")
                continue

        # 保存缓存（只有成功获取数据时才更新）
        if results:
            _cache_time[cache_key] = datetime.now()
            _cache_data[cache_key] = results

    except Exception as e:
        print(f"Error fetching US indices batch: {e}")
        # 返回旧缓存（如果有）
        return _cache_data.get(cache_key, {})

    return results


def get_stock_spot(symbol: str) -> dict:
    """
    获取美股/全球指数实时行情（从批量数据或缓存获取）
    """
    # 如果是美股指数，优先从批量数据获取
    if symbol.startswith('US.'):
        batch_data = get_us_indices_batch()
        if symbol in batch_data:
            return batch_data[symbol]

    # 单个获取（带缓存）
    cache_key = f'us_{symbol}'
    if _is_cache_valid(cache_key):
        return _cache_data.get(cache_key)

    try:
        ticker_code = get_symbol_ticker(symbol)
        ticker = yf.Ticker(ticker_code)

        info = ticker.info
        hist = ticker.history(period='1d')

        if hist.empty:
            return None

        current = hist.iloc[-1]
        prev_close = info.get('previousClose', current['Open'])

        result = {
            'symbol': symbol,
            'name': info.get('shortName', info.get('longName', symbol)),
            'price': float(current['Close']),
            'change': float(current['Close'] - prev_close),
            'change_pct': float((current['Close'] - prev_close) / prev_close * 100),
            'open': float(current['Open']),
            'high': float(current['High']),
            'low': float(current['Low']),
            'volume': float(current['Volume']),
            'prev_close': float(prev_close),
        }

        # 保存缓存
        _cache_time[cache_key] = datetime.now()
        _cache_data[cache_key] = result

        return result
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None


def get_stock_history(symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    获取历史行情
    """
    try:
        ticker_code = get_symbol_ticker(symbol)
        ticker = yf.Ticker(ticker_code)

        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=365)

        df = ticker.history(start=start_date, end=end_date)
        return df
    except Exception as e:
        print(f"Error fetching history for {symbol}: {e}")
        return pd.DataFrame()


def get_market_status() -> dict:
    """
    获取全球市场开盘状态
    """
    # 简化版：根据当前时间判断
    now = datetime.now()
    hour_utc = now.hour

    status = {
        'A 股': 'closed',      # 9:30-15:00 CST
        '港股': 'closed',      # 9:30-16:00 HKT
        '美股': 'closed',      # 9:30-16:00 EST
        '欧洲': 'closed',      # 8:00-16:30 CET
        '日本': 'closed',      # 9:00-15:00 JST
    }

    # 简化判断（实际应使用时区和交易日历）
    if 1 <= hour_utc <= 7:
        status['美股'] = 'open'
    elif 8 <= hour_utc <= 10:
        status['欧洲'] = 'open'
        status['A 股'] = 'open'
        status['港股'] = 'open'
    elif 13 <= hour_utc <= 15:
        status['欧洲'] = 'open'
        status['A 股'] = 'open'
        status['港股'] = 'open'
    elif 14 <= hour_utc <= 20:
        status['美股'] = 'open'

    return status
