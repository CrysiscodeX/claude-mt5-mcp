import numpy as np

def get_account_info(**kwargs):
    try:
        import MetaTrader5 as mt5
        if not mt5.initialize():
            raise Exception("MT5 initialization failed. Is the terminal running and logged in?")
        
        info = mt5.account_info()
        if info is not None:
            return info._asdict()
        return None
    except Exception as e:
        return {"error": True, "message": str(e)}

def get_symbol_tick(symbol: str, **kwargs):
    try:
        import MetaTrader5 as mt5
        if not mt5.initialize():
            raise Exception("MT5 initialization failed. Is the terminal running and logged in?")
            
        tick = mt5.symbol_info_tick(symbol)
        if tick is not None:
            return tick._asdict()
        return None
    except Exception as e:
        return {"error": True, "message": str(e)}

def get_historical_data(symbol: str, timeframe: str, count: int, **kwargs):
    try:
        import MetaTrader5 as mt5
        if not mt5.initialize():
            raise Exception("MT5 initialization failed. Is the terminal running and logged in?")
            
        mt5_timeframe = getattr(mt5, timeframe)
        rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, count)
        
        if rates is None:
            return {"data": []}
            
        # Convert numpy array to a list of dictionaries
        rates_list = []
        for rate in rates:
            rates_list.append({
                "time": int(rate['time']),
                "open": float(rate['open']),
                "high": float(rate['high']),
                "low": float(rate['low']),
                "close": float(rate['close'])
            })
        return {"data": rates_list}
    except Exception as e:
        return {"error": True, "message": str(e)}

def get_indicator_value(symbol: str, timeframe: str, indicator: str, period: int, **kwargs):
    try:
        import MetaTrader5 as mt5
        if not mt5.initialize():
            raise Exception("MT5 initialization failed. Is the terminal running and logged in?")
            
        mt5_timeframe = getattr(mt5, timeframe)
        
        latest_value = None
        
        if indicator == "SMA":
            handle = mt5.iMA(symbol, mt5_timeframe, period, 0, mt5.MODE_SMA, mt5.PRICE_CLOSE)
            if handle != -1:
                buffer_data = mt5.copy_buffer(handle, 0, 0, 1)
                if buffer_data is not None and len(buffer_data) > 0:
                    latest_value = np.real(buffer_data[0])
        elif indicator == "RSI":
            handle = mt5.iRSI(symbol, mt5_timeframe, period, mt5.PRICE_CLOSE)
            if handle != -1:
                buffer_data = mt5.copy_buffer(handle, 0, 0, 1)
                if buffer_data is not None and len(buffer_data) > 0:
                    latest_value = np.real(buffer_data[0])

        if latest_value is not None and not np.isnan(latest_value):
            return {'value': float(latest_value)}
        else:
            return {'value': None}
    except Exception as e:
        return {"error": True, "message": str(e)}