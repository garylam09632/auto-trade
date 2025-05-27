from futu import *


def get_market_code(currency):
    if currency.upper() == 'USD':
        return "US."
    return "HK."

def get_trd_market(currency):
    if currency.upper() == 'USD':
        return TrdMarket.US
    return TrdMarket.HK

def get_security_firm(currency):
    # if currency.upper() == 'USD':
    #     return SecurityFirm.FUTUIN
    return SecurityFirm.FUTUSECURITIES

def convert_option_format(option_code):
    """Convert from 'TSLA 250523 262.50P' to 'US.TSLA250523C570000'"""
    parts = option_code.split()
    ticker = parts[0]  # TSLA
    expiry = parts[1]  # 250523 (DDMMYY format)
    strike_type = parts[2]  # e.g., 262.50P

    # Extract strike price and option type (C/P)
    strike_price = float(strike_type[:-1])  # 262.50
    option_type = strike_type[-1].upper()  # P or C

    # Convert strike price to 6-digit number (e.g., 262.50 → 570000)
    strike_in_thousands = int(strike_price * 1000)  # 262.50 → 262500
    strike_padded = f"{strike_in_thousands:06d}"  # Pad to 6 digits

    # Construct the new format
    converted_code = f"{ticker}{expiry}{option_type}{strike_padded}"
    return converted_code
