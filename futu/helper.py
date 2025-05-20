from futu.common.pb.Trd_Common_pb2 import TrdMarket
from type import MarketCode

def get_market_code(currency):
    if currency.upper() == 'USD':
        return MarketCode.US
    return MarketCode.HK

def get_trd_market(currency):
    if currency.upper() == 'USD':
        return TrdMarket.US
    return TrdMarket.HK