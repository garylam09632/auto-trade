from futu import *
from config import *
from helper import *
from type import *
from flask import Flask, jsonify, request

def place_shares_order(symbol, price, currency, action):
    market_code = get_market_code(currency)
    code = f"{market_code}{symbol}"
    trd_market = get_trd_market(currency)
    security_firm = get_security_firm(currency)

    # Get account total assets
    total_assets = 0
    available_assets = 0
    trd_ctx = OpenSecTradeContext(filter_trdmarket=trd_market, host=FUTU_OPEN_D_HOST, port=FUTU_OPEN_D_PORT,
                                  security_firm=security_firm)
    ret, data = trd_ctx.accinfo_query(trd_env=FUTU_ENV)
    if ret == RET_OK:
        total_assets = data['total_assets'][0]
        available_assets = data['total_assets'][0]
        print(f"total_assets {total_assets}")
    else:
        print('accinfo_query error: ', data)

    if available_assets < 0:
        return jsonify({"success": False, "message": "Account total assets is 0"})

    ret, data = trd_ctx.position_list_query(trd_env=FUTU_ENV, code=code)

    position_asset_sum = 0
    if ret == RET_OK:
        orders = data.to_dict('records')
        print(orders)
        if len(orders) == 0:  # 如果持仓列表不为空
            print('No order exists')

        # Find the target order to close
        target_order = None
        for order in orders:
            position_asset_sum += order['qty'] * order['cost_price']
        available_assets -= position_asset_sum

    allow_assets = total_assets * SHARES_ORDER_PERCENTAGE_PER_STOCK
    # If the assets amount after deducting the stock which in position is less than the allowed assets, use all of the available assets
    if allow_assets > available_assets:
        allow_assets = available_assets

    print(f"allow_assets {allow_assets}")
    print(f"price {price}")
    shares_qty = allow_assets / price  # Shares qty available for long and short (estimate qty only since the price is from request body instead of real-time quote)
    print(f"shares_qty {shares_qty}")

    print(f"Place order: {code}")
    print({
        "price": price,
        "qty": shares_qty,
        "code": code,
        "order_type": OrderType.MARKET,
        "trd_side": action,
        "trd_env": FUTU_ENV,
        "session": Session.RTH
    })
    if FUTU_ENV == TrdEnv.REAL:
        ret, data = trd_ctx.unlock_trade(FUTU_TRADE_PWD)
        if ret == RET_OK:
            print("Unlocked")
        else:
            print('unlock_trade error: ', data)
            return jsonify({"success": False, "message": "Unlock trade failed"})
    ret2, data2 = trd_ctx.place_order(
        price=price,
        qty=shares_qty,
        code=code,
        order_type=OrderType.MARKET,
        trd_side=action,
        trd_env=FUTU_ENV,
        session=Session.RTH
    )
    if ret2 == RET_OK:
        print(data2)
        return jsonify({"success": True}), 200
    else:
        print(data2)
        return jsonify({"success": False, "message": data})


def close_shares_position(symbol, currency):
    market_code = get_market_code(currency)
    code = f"{market_code}{symbol}"
    trd_market = get_trd_market(currency)
    security_firm = get_security_firm(currency)

    # Trading context
    trd_ctx = OpenSecTradeContext(filter_trdmarket=trd_market, host=FUTU_OPEN_D_HOST, port=FUTU_OPEN_D_PORT,
                                  security_firm=security_firm)
    ret, data = trd_ctx.position_list_query(trd_env=FUTU_ENV)
    if ret == RET_OK:
        orders = data.to_dict('records')
        if len(orders) == 0:  # 如果持仓列表不为空
            return jsonify({"success": False, "message": "No order exists"})
        # Find the target order to close
        target_order = None
        for order in orders:
            if order['code'] == code:
                target_order = order
                break

        if target_order is None:
            print('No order found')
            return jsonify({"success": False, "message": f"Order with {code} was not found"})

        action = Action.Sell.value if target_order['position_side'] == PositionSide.LONG else Action.Buy.value

        print(f"Close position: {code}")
        print({
            "qty": target_order['qty'],
            "code": code,
            "order_type": OrderType.MARKET,
            "trd_side": action,
            "trd_env": FUTU_ENV,
            "session": Session.RTH
        })
        if FUTU_ENV == TrdEnv.REAL:
            ret, data = trd_ctx.unlock_trade(FUTU_TRADE_PWD)
            if ret == RET_OK:
                print("Unlocked")
            else:
                print('unlock_trade error: ', data)
                return jsonify({"success": False, "message": "Unlock trade failed"})
        ret, data = trd_ctx.place_order(
            price=1,
            qty=target_order['qty'],
            code=code,
            order_type=OrderType.MARKET,
            trd_side=action,
            trd_env=FUTU_ENV,
            session=Session.RTH
        )  # 模拟交易，下单（如果是真实环境交易，在此之前需要先解锁交易密码）
        if ret == RET_OK:
            print(data)
            return jsonify({"success": True}), 201
        else:
            print('place_order fail')
            print(data)
            return jsonify({"success": False, "message": "Close position failed"})
    else:
        print('position_list_query error: ', data)
        return jsonify({"success": False, "message": data})


def place_option_order(symbol, price, currency, action, direction):
    market_code = get_market_code(currency)
    code = f"{market_code}{symbol}"
    trd_market = get_trd_market(currency)
    security_firm = get_security_firm(currency)
    print(f"code: {code}")
    options = get_target_option_code(code, price)
    if not options or "calls" not in options or "puts" not in options:
        return False  # Early exit if invalid structure

    # Ensure the indices are within bounds
    if OPTION_CALL_INDEX >= len(options["calls"]) or OPTION_PUT_INDEX >= len(options["puts"]):
        return False  # Avoid "IndexError: list index out of range"

    # Safely access the options
    target_call = options["calls"][OPTION_CALL_INDEX]
    target_put = options["puts"][OPTION_PUT_INDEX]

    # Assume direction value must be valid
    if direction == Direction.Call.value:
        print('CALL')
        code = target_call
    else:
        print('PUT')
        code = target_put

    # Get option account
    acc_id = 0
    get_acc_ctx = OpenSecTradeContext(filter_trdmarket=trd_market, host=FUTU_OPEN_D_HOST, port=FUTU_OPEN_D_PORT)
    get_acc_ret, get_acc_data = get_acc_ctx.get_acc_list()
    if get_acc_ret == RET_OK:
        acc_list = get_acc_data.to_dict('records')
        for acc in acc_list:
            if acc['sim_acc_type'] == 'OPTION' and acc['trd_env'] == TrdEnv.SIMULATE and FUTU_ENV == TrdEnv.SIMULATE:
                acc_id = acc['acc_id']
                break
            if acc['trd_env'] == TrdEnv.REAL and FUTU_ENV == TrdEnv.REAL:
                acc_id = acc['acc_id']
                break
    else:
        print('get_acc_list error: ', get_acc_data)

    # Get account total assets
    total_assets = 0
    available_assets = 0
    trd_ctx = OpenSecTradeContext(filter_trdmarket=trd_market, host=FUTU_OPEN_D_HOST, port=FUTU_OPEN_D_PORT,
                                  security_firm=security_firm)
    ret, data = trd_ctx.accinfo_query(trd_env=FUTU_ENV, acc_id=acc_id)
    if ret == RET_OK:
        total_assets = data['total_assets'][0]
        available_assets = data['total_assets'][0]
        print(f"total_assets {total_assets}")
    else:
        print('accinfo_query error: ', data)

    if available_assets < 0:
        return jsonify({"success": False, "message": "Account total assets is 0"})

    # Get positions
    ret, data = trd_ctx.position_list_query(trd_env=FUTU_ENV, acc_id=acc_id)
    if ret == RET_OK:
        print(data.to_dict('records'))
    else:
        print('accinfo_query error: ', data)
        return jsonify({"success": False, "message": "Query position error"})

    # allow_assets = total_assets * SHARES_ORDER_PERCENTAGE_PER_STOCK
    # # If the assets amount after deducting the stock which in position is less than the allowed assets, use all of the available assets
    # if allow_assets > available_assets:
    #     allow_assets = available_assets

    # print(f"allow_assets {allow_assets}")
    # print(f"price {price}")
    # shares_qty = allow_assets / price # Shares qty available for long and short (estimate qty only since the price is from request body instead of real-time quote)
    shares_qty = 1

    print({
        "price": price,
        "qty": shares_qty,
        "code": code,
        "order_type": OrderType.MARKET,
        "trd_side": action,
        "trd_env": FUTU_ENV,
        "session": Session.RTH
    })
    if FUTU_ENV == TrdEnv.REAL:
        ret, data = trd_ctx.unlock_trade(FUTU_TRADE_PWD)
        if ret == RET_OK:
            print("Unlocked")
        else:
            print('unlock_trade error: ', data)
            return jsonify({"success": False, "message": "Unlock trade failed"})
    ret2, data2 = trd_ctx.place_order(
        acc_id=acc_id,
        price=price,
        qty=shares_qty,
        code=code,
        order_type=OrderType.MARKET,
        trd_side=action,
        trd_env=FUTU_ENV,
        # session=Session.RTH
    )
    if ret2 == RET_OK:
        print(data2)
        return jsonify({"success": True}), 200
    else:
        print(f"ret2 {data2}")
        return jsonify({"success": False, "message": data2})


def close_option_position(symbol, currency, direction):
    market_code = get_market_code(currency)
    code = f"{market_code}{symbol}"
    trd_market = get_trd_market(currency)
    security_firm = get_security_firm(currency)

    # Get account speific for option trading
    acc_id = 0
    get_acc_ctx = OpenSecTradeContext(filter_trdmarket=trd_market, host=FUTU_OPEN_D_HOST, port=FUTU_OPEN_D_PORT)
    get_acc_ret, get_acc_data = get_acc_ctx.get_acc_list()
    if get_acc_ret == RET_OK:
        acc_list = get_acc_data.to_dict('records')
        for acc in acc_list:
            if acc['sim_acc_type'] == 'OPTION' and acc['trd_env'] == TrdEnv.SIMULATE and FUTU_ENV == TrdEnv.SIMULATE:
                acc_id = acc['acc_id']
                break
            if acc['trd_env'] == TrdEnv.REAL and FUTU_ENV == TrdEnv.REAL:
                acc_id = acc['acc_id']
                break
    else:
        print('get_acc_list error: ', get_acc_data)

    # Get all option positions
    option_positions = []
    trd_ctx = OpenSecTradeContext(filter_trdmarket=trd_market, host=FUTU_OPEN_D_HOST, port=FUTU_OPEN_D_PORT,
                                  security_firm=security_firm)
    ret, data = trd_ctx.position_list_query(trd_env=FUTU_ENV, acc_id=acc_id)
    if ret == RET_OK:
        option_positions = data.to_dict('records')
        print(option_positions)
    else:
        return jsonify({"success": False, "message": "Query position error"})

    # Separate with shares and options with the desire code/symbol
    option_positions = distinguish_shares_and_options(option_positions, code)['options']
    if len(option_positions) == 0:
        return jsonify({"success": False, "message": "No option positions"})

    # Separate with calls and puts
    option_positions = separate_calls_puts(option_positions)

    # If the closing direction is call, only close call positions, else close put positions
    if direction == Direction.Call.value:
        option_positions = option_positions['calls']
    else:
        option_positions = option_positions['puts']

    # Unlock trade authority
    if FUTU_ENV == TrdEnv.REAL:
        ret, data = trd_ctx.unlock_trade(FUTU_TRADE_PWD)
        if ret == RET_OK:
            print("Unlocked")
        else:
            print('unlock_trade error: ', data)
            return jsonify({"success": False, "message": "Unlock trade failed"})

    for position in option_positions:
        code = position['code']
        qty = position['qty']
        action = Action.Sell.value if position['position_side'] == PositionSide.LONG else Action.Buy.value
        print({
            "qty": qty,
            "code": code,
            "order_type": OrderType.MARKET,
            "trd_side": action,
            "trd_env": FUTU_ENV,
            "session": Session.RTH
        })
        ret, data = trd_ctx.place_order(
            acc_id=acc_id,
            price=1,
            qty=qty,
            code=code,
            order_type=OrderType.MARKET,
            trd_side=action,
            trd_env=FUTU_ENV,
            session=Session.RTH
        )  # 模拟交易，下单（如果是真实环境交易，在此之前需要先解锁交易密码）
        if ret == RET_OK:
            print(data)
        else:
            print('close option position fail')
            print(data)
            return jsonify({"success": False, "message": "Close position failed"})

    return jsonify({"success": True, "option_positions": option_positions})


def get_target_option_code(code, price):
    quote_ctx = OpenQuoteContext(host=FUTU_OPEN_D_HOST, port=FUTU_OPEN_D_PORT)
    ret1, data1 = quote_ctx.get_option_expiration_date(code=code)

    if ret1 == RET_OK:
        strike_dates = data1['strike_time'].values.tolist()
        today = datetime.now().strftime('%Y-%m-%d')

        # Find the first strike date that's not today
        selected_date = None
        for date in strike_dates:
            if date != today:
                selected_date = date
                break

        if not selected_date:
            print("No future strike dates available")
            quote_ctx.close()
            return None

        print('Selected strike date:', selected_date)

        ret2, data2 = quote_ctx.get_option_chain(code=code, start=selected_date, end=selected_date)
        if ret2 == RET_OK:
            arr = data2.to_dict('records')

            # Initialize collections
            calls = []
            puts = []

            for option in arr:
                # parts = code.split(' ')
                code = option['code']
                option_type = option['option_type']
                strike_price = float(option['strike_price'])  # Convert price to float

                # Check if strike price is within tolerance
                # if abs(strike_price - target_price) <= OPTION_PRICE_TOLERANCE:
                # For CALLS: Only include strikes ABOVE target_price
                if option_type == Direction.Call.value and strike_price > price:
                    # print(f"Call code:{code}")
                    # print(f"strike_price:{strike_price}")
                    calls.append(code)  # (strike_price, code)
                # For PUTS: Only include strikes BELOW target_price
                elif option_type == Direction.Put.value and strike_price < price:
                    # print(f"Put code:{code}")
                    # print(f"strike_price:{strike_price}")
                    puts.append(code)

            # Sort by proximity to target price and limit results
            calls = sorted(calls, key=lambda x: x[0])[:OPTION_MAX_PER_TYPE]
            puts.reverse()
            puts = sorted(puts, key=lambda x: x[0])[:OPTION_MAX_PER_TYPE]
            print(calls)
            print(puts)
            # print(data2['code'][0])  #  print(data2['code'].values.tolist())  # 转为 list取第一条的股票代码
            #             #
            quote_ctx.close()  # 结束后记得关闭当条连接，防止连接条数用尽
            return {"calls": calls, "puts": puts}
        else:
            print('error:', data2)
    else:
        print('error:', data1)
    quote_ctx.close()  # 结束后记得关闭当条连接，防止连接条数用尽
    return None

def distinguish_shares_and_options(positions, code=None):
    """
    Distinguish between shares and options in a list of positions, optionally filtering by underlying stock code.
    
    Args:
        positions (list): List of position dictionaries
        code (str, optional): Underlying stock code to filter options by (e.g., "US.TSLA"). 
                             If None, returns all options.
        
    Returns:
        dict: Dictionary with 'shares' and 'options' keys containing separated positions
    """
    shares = []
    options = []
    
    for position in positions:
        # Check if it's an option position
        is_option = ('C' in position['code'] or 'P' in position['code'] or 
                    'call' in position['stock_name'].lower() or 
                    'put' in position['stock_name'].lower())
        
        if is_option:
            # If a specific code is provided, check if the option belongs to that underlying
            if code is None or position['code'].startswith(code):
                options.append(position)
        else:
            shares.append(position)
    
    return {
        'shares': shares,
        'options': options
    }

def separate_calls_puts(options):
    """
    Separate options into calls and puts based on their codes and names.
    
    Args:
        options (list): List of option position dictionaries
        
    Returns:
        dict: Dictionary with 'calls' and 'puts' keys containing separated options
    """
    calls = []
    puts = []
    
    for option in options:
        # Check if it's a call (either 'C' in code or 'call' in name)
        is_call = ('C' in option['code'] or 
                 'call' in option['stock_name'].lower())
        
        # Check if it's a put (either 'P' in code or 'put' in name)
        is_put = ('P' in option['code'] or 
                'put' in option['stock_name'].lower())
        
        if is_call and not is_put:
            calls.append(option)
        elif is_put and not is_call:
            puts.append(option)
        else:
            # Handle ambiguous cases (shouldn't happen with standard option codes)
            # You might want to log these cases
            pass
    
    return {
        'calls': calls,
        'puts': puts
    }