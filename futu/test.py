from futu import *
import datetime
import numpy as np


def get_nearest_options(quote_ctx, stock_code, option_type=OptionType.ALL, direction=OptionDirection.ALL):
    """
    Get options with nearest expiry and strike price closest to current market price

    Parameters:
        quote_ctx: OpenQuoteContext instance
        stock_code: Underlying stock code (e.g., 'HK.00700')
        option_type: OptionType.CALL, OptionType.PUT, or OptionType.ALL
        direction: OptionDirection.ALL, etc.

    Returns:
        Dictionary with nearest call and put options
    """
    # Get option chain
    ret, data = quote_ctx.get_option_chain(stock_code, option_type, direction)
    if ret != RET_OK:
        print(f"Error getting option chain: {data}")
        return None

    # Get current market price of underlying
    ret, market_data = quote_ctx.get_market_snapshot([stock_code])
    if ret != RET_OK:
        print(f"Error getting market snapshot: {market_data}")
        return None

    current_price = market_data.iloc[0]['last_price']

    # Convert expiry date strings to datetime objects for comparison
    data['expiry_date_dt'] = pd.to_datetime(data['strike_time'])

    # Find the nearest expiry date
    nearest_expiry = data['expiry_date_dt'].min()
    nearest_options = data[data['expiry_date_dt'] == nearest_expiry]

    # Find options with strike price closest to current price
    nearest_options['strike_diff'] = abs(nearest_options['strike_price'] - current_price)

    # Get the closest call and put options
    result = {
        'underlying': stock_code,
        'current_price': current_price,
        'nearest_expiry': nearest_expiry.strftime('%Y-%m-%d')
    }

    if OptionType.CALL in nearest_options['option_type'].values:
        closest_call = nearest_options[nearest_options['option_type'] == OptionType.CALL].nsmallest(1, 'strike_diff')
        result['call'] = closest_call.iloc[0].to_dict()

    if OptionType.PUT in nearest_options['option_type'].values:
        closest_put = nearest_options[nearest_options['option_type'] == OptionType.PUT].nsmallest(1, 'strike_diff')
        result['put'] = closest_put.iloc[0].to_dict()

    return result


# Example usage
if __name__ == "__main__":
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

    try:
        # Example for Tencent stock
        stock_code = 'HK.00700'
        result = get_nearest_options(quote_ctx, stock_code)

        print(f"Underlying: {result['underlying']}")
        print(f"Current Price: {result['current_price']}")
        print(f"Nearest Expiry: {result['nearest_expiry']}")

        if 'call' in result:
            print("\nNearest Call Option:")
            print(f"Code: {result['call']['code']}")
            print(f"Strike: {result['call']['strike_price']}")
            print(f"Premium: {result['call']['price']}")

        if 'put' in result:
            print("\nNearest Put Option:")
            print(f"Code: {result['put']['code']}")
            print(f"Strike: {result['put']['strike_price']}")
            print(f"Premium: {result['put']['price']}")

    finally:
        quote_ctx.close()  # Close the connection