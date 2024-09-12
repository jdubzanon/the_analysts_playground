from theanalystsplayground.Search.models import StockSearch


def inject_crypto_map():
    return {
        "X:BTCUSD": {
            "ticker": "BTC",
            "obj": StockSearch.objects.get(public_ticker="BTC", market_type="crypto"),
            "data": None,
        },
        "X:ETHUSD": {
            "ticker": "ETH",
            "obj": StockSearch.objects.get(public_ticker="ETH", market_type="crypto"),
            "data": None,
        },
        "X:SOLUSD": {
            "ticker": "SOL",
            "obj": StockSearch.objects.get(public_ticker="SOL", market_type="crypto"),
            "data": None,
        },
        "X:ADAUSD": {
            "ticker": "ADA",
            "obj": StockSearch.objects.get(public_ticker="ADA", market_type="crypto"),
            "data": None,
        },
        "X:XRPUSD": {
            "ticker": "XRP",
            "obj": StockSearch.objects.get(public_ticker="XRP", market_type="crypto"),
            "data": None,
        },
    }


def inject_forex_map():
    return {
        "C:EURUSD": {
            "ticker": "EURUSD",
            "obj": StockSearch.objects.get(public_ticker="EURUSD", market_type="fx"),
            "data": None,
        },
        "C:USDJPY": {
            "ticker": "USDJPY",
            "obj": StockSearch.objects.get(public_ticker="USDJPY", market_type="fx"),
            "data": None,
        },
        "C:GBPUSD": {
            "ticker": "GBPUSD",
            "obj": StockSearch.objects.get(public_ticker="GBPUSD", market_type="fx"),
            "data": None,
        },
        "C:USDCNY": {
            "ticker": "USDCNY",
            "obj": StockSearch.objects.get(public_ticker="USDCNY", market_type="fx"),
            "data": None,
        },
        "C:AUDUSD": {
            "ticker": "AUDUSD",
            "obj": StockSearch.objects.get(public_ticker="AUDUSD", market_type="fx"),
            "data": None,
        },
    }


def inject_name_map(data):
    if data is None:
        return data
    name_map = {}
    for item in data:
        if "error" in item:
            continue
        name_map[item.get("ticker")] = item.get("name")
    return name_map
