"""
数据抓取模块 - A股/港股使用AKShare，美股/全球指数使用yfinance
"""
import akshare as ak
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

class DataFetcher:
    """数据抓取器"""
    
    # A股指数映射
    A_SHARE_INDICES = {
        "000001": "上证指数",
        "000300": "沪深300",
        "000016": "上证50",
        "000905": "中证500",
        "399001": "深证成指",
        "399006": "创业板指",
        "399673": "创业板50",
        "000688": "科创50",
    }
    
    # 港股指数
    HK_INDICES = {
        "^HSI": "恒生指数",
        "^HSCE": "恒生国企指数",
        "^HSTECH": "恒生科技指数",
    }
    
    # 美股/全球指数 (yfinance格式)
    GLOBAL_INDICES = {
        "^GSPC": "标普500",
        "^DJI": "道琼斯",
        "^IXIC": "纳斯达克",
        "^NDX": "纳斯达克100",
        "^RUT": "罗素2000",
        "^VIX": "VIX恐慌指数",
        "^FTSE": "英国富时100",
        "^GDAXI": "德国DAX",
        "^FCHI": "法国CAC40",
        "^N225": "日经225",
        "^KS11": "韩国KOSPI",
    }
    
    def __init__(self):
        self.today = datetime.now().strftime("%Y%m%d")
    
    def get_a_share_index(self, symbol: str) -> Optional[Dict]:
        """获取A股指数数据"""
        try:
            # 使用AKShare获取指数行情
            df = ak.index_zh_a_spot_em()
            
            # 查找对应指数
            row = df[df['代码'] == symbol]
            if row.empty:
                return None
            
            row = row.iloc[0]
            return {
                "symbol": symbol,
                "name": row.get('名称', self.A_SHARE_INDICES.get(symbol, 'Unknown')),
                "market": "a_share",
                "price": float(row.get('最新价', 0) or 0),
                "change": float(row.get('涨跌额', 0) or 0),
                "change_pct": float(row.get('涨跌幅', 0) or 0),
                "volume": float(row.get('成交量', 0) or 0),
                "high": float(row.get('最高', 0) or 0),
                "low": float(row.get('最低', 0) or 0),
                "open": float(row.get('今开', 0) or 0),
                "prev_close": float(row.get('昨收', 0) or 0),
            }
        except Exception as e:
            print(f"Error fetching A-share index {symbol}: {e}")
            return None
    
    def get_a_share_stock(self, symbol: str) -> Optional[Dict]:
        """获取A股个股数据"""
        try:
            # 使用AKShare获取个股行情
            df = ak.stock_zh_a_spot_em()
            
            # 查找对应股票
            row = df[df['代码'] == symbol]
            if row.empty:
                return None
            
            row = row.iloc[0]
            return {
                "symbol": symbol,
                "name": row.get('名称', 'Unknown'),
                "market": "a_share",
                "price": float(row.get('最新价', 0) or 0),
                "change": float(row.get('涨跌额', 0) or 0),
                "change_pct": float(row.get('涨跌幅', 0) or 0),
                "volume": float(row.get('成交量', 0) or 0),
                "high": float(row.get('最高', 0) or 0),
                "low": float(row.get('最低', 0) or 0),
                "open": float(row.get('今开', 0) or 0),
                "prev_close": float(row.get('昨收', 0) or 0),
            }
        except Exception as e:
            print(f"Error fetching A-share stock {symbol}: {e}")
            return None
    
    def get_hk_stock(self, symbol: str) -> Optional[Dict]:
        """获取港股数据"""
        try:
            # 使用AKShare获取港股行情
            df = ak.stock_hk_spot_em()
            
            # 查找对应股票
            row = df[df['代码'] == symbol]
            if row.empty:
                return None
            
            row = row.iloc[0]
            return {
                "symbol": symbol,
                "name": row.get('名称', 'Unknown'),
                "market": "hk",
                "price": float(row.get('最新价', 0) or 0),
                "change": float(row.get('涨跌额', 0) or 0),
                "change_pct": float(row.get('涨跌幅', 0) or 0),
                "volume": float(row.get('成交量', 0) or 0),
                "high": float(row.get('最高', 0) or 0),
                "low": float(row.get('最低', 0) or 0),
                "open": float(row.get('今开', 0) or 0),
                "prev_close": float(row.get('昨收', 0) or 0),
            }
        except Exception as e:
            print(f"Error fetching HK stock {symbol}: {e}")
            return None
    
    def get_us_stock(self, symbol: str) -> Optional[Dict]:
        """获取美股数据 (使用yfinance)"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="2d")
            
            if hist.empty:
                return None
            
            today = hist.iloc[-1]
            prev = hist.iloc[-2] if len(hist) > 1 else today
            
            change = today['Close'] - prev['Close']
            change_pct = (change / prev['Close'] * 100) if prev['Close'] != 0 else 0
            
            return {
                "symbol": symbol,
                "name": info.get('shortName', info.get('longName', symbol)),
                "market": "us",
                "price": round(today['Close'], 2),
                "change": round(change, 2),
                "change_pct": round(change_pct, 2),
                "volume": int(today['Volume']),
                "high": round(today['High'], 2),
                "low": round(today['Low'], 2),
                "open": round(today['Open'], 2),
                "prev_close": round(prev['Close'], 2),
            }
        except Exception as e:
            print(f"Error fetching US stock {symbol}: {e}")
            return None
    
    def get_global_index(self, symbol: str) -> Optional[Dict]:
        """获取全球指数 (使用yfinance)"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="2d")
            
            if hist.empty:
                return None
            
            today = hist.iloc[-1]
            prev = hist.iloc[-2] if len(hist) > 1 else today
            
            change = today['Close'] - prev['Close']
            change_pct = (change / prev['Close'] * 100) if prev['Close'] != 0 else 0
            
            return {
                "symbol": symbol,
                "name": self.GLOBAL_INDICES.get(symbol, info.get('shortName', symbol)),
                "market": "global",
                "price": round(today['Close'], 2),
                "change": round(change, 2),
                "change_pct": round(change_pct, 2),
                "volume": int(today['Volume']) if 'Volume' in today else 0,
                "high": round(today['High'], 2),
                "low": round(today['Low'], 2),
                "open": round(today['Open'], 2),
                "prev_close": round(prev['Close'], 2),
            }
        except Exception as e:
            print(f"Error fetching global index {symbol}: {e}")
            return None
    
    def fetch_watchlist(self, watchlist: List[Dict]) -> List[Dict]:
        """批量获取关注列表数据"""
        results = []
        
        for item in watchlist:
            symbol = item['symbol']
            market = item['market']
            
            data = None
            if market == 'a_share':
                if symbol in self.A_SHARE_INDICES:
                    data = self.get_a_share_index(symbol)
                else:
                    data = self.get_a_share_stock(symbol)
            elif market == 'hk':
                data = self.get_hk_stock(symbol)
            elif market == 'us':
                data = self.get_us_stock(symbol)
            elif market == 'global':
                data = self.get_global_index(symbol)
            
            if data:
                results.append(data)
        
        return results
    
    def get_all_a_share_indices(self) -> List[Dict]:
        """获取所有A股主要指数"""
        results = []
        for symbol in self.A_SHARE_INDICES.keys():
            data = self.get_a_share_index(symbol)
            if data:
                results.append(data)
        return results
    
    def get_all_global_indices(self) -> List[Dict]:
        """获取所有全球主要指数"""
        results = []
        for symbol in self.GLOBAL_INDICES.keys():
            data = self.get_global_index(symbol)
            if data:
                results.append(data)
        return results


# 便捷函数
def fetcher():
    """获取数据抓取器实例"""
    return DataFetcher()


if __name__ == "__main__":
    # 测试数据抓取
    f = DataFetcher()
    
    print("=== 测试A股指数 ===")
    index_data = f.get_a_share_index("000001")
    print(json.dumps(index_data, ensure_ascii=False, indent=2))
    
    print("\n=== 测试美股 ===")
    us_data = f.get_us_stock("AAPL")
    print(json.dumps(us_data, ensure_ascii=False, indent=2))
    
    print("\n=== 测试全球指数 ===")
    global_data = f.get_global_index("^GSPC")
    print(json.dumps(global_data, ensure_ascii=False, indent=2))