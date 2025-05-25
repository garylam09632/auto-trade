from flask import Flask, jsonify, request
from futu import *
from config import *
from helper import *
from type import *

app = Flask(__name__)

def place_shares_order(symbol, price, currency, action):

    market_code = get_market_code(currency)
    code = f"{market_code}{symbol}"
    trd_market = get_trd_market(currency)
    security_firm = get_security_firm(currency)

    # Get account total assets
    total_assets = 0
    available_assets = 0
    trd_ctx = OpenSecTradeContext(filter_trdmarket=trd_market, host=FUTU_OPEN_D_HOST, port=FUTU_OPEN_D_PORT, security_firm=security_firm)
    ret, data = trd_ctx.accinfo_query(trd_env=FUTU_ENV)
    if ret == RET_OK:
        total_assets = data['total_assets'][0]
        available_assets = data['total_assets'][0]
        print(f"total_assets {total_assets}")
    else:
        print('accinfo_query error: ', data)

    if available_assets < 0:
        return jsonify({ "success": False, "message": "Account total assets is 0" })

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
    shares_qty = allow_assets / price # Shares qty available for long and short (estimate qty only since the price is from request body instead of real-time quote)
    print(f"shares_qty {shares_qty}")         

    # # Set MAX_BUY
    # ret, data = trd_ctx.acctradinginfo_query(order_type=OrderType.NORMAL, code=code, price=price, trd_env=TrdEnv.SIMULATE)
    # if ret == RET_OK:
    #     print(data)
    #     max_buy = data['max_cash_buy'][0]  # 最大融资可买数量
    #     max_sell = data['max_sell_starget_order_qty = target_order['qty']hort'][0]
    #     print(max_buy * STOCK_ORDER_LIMIT)
    #     # ret, data = trd_ctx.place_order(
    #     #     price=400,
    #     #     qty=1,
    #     #     code=code,
    #     #     order_type=OrderType.MARKET,
    #     #     trd_side=action,
    #     #     trd_env=FUTU_ENV,
    #     #     session=Session.RTH
    #     # ) # 模拟交易，下单（如果是真实环境交易，在此之前需要先解锁交易密码）
    #     # if ret == RET_OK:
    #     #     print(data)
    #     #     return jsonify({ "success": True }), 201
    #     # else:
    #     #     print(data)
    #     #     return jsonify({ "success": False, "message": data })
    # else:
        # print('acc_trading_info_query error: ', data)
    
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
        return jsonify({ "success": True }), 200
    else:
        print(data2)
        return jsonify({ "success": False, "message": data })

# POST place_order
@app.route('/futu/place-order', methods=['POST'])
def place_order():
    req = request.get_json(force=True)
    if req.get('action') is None or req.get('price') is None:
        return jsonify({ "success": False }), 400
    
    code = req.get('code')
    price = float(req.get('price'))
    action = req.get('action')
    currency = req.get('currency')

    if currency is None:
        currency = DEFAULT_TRADING_CURRENCY

    if code is None or currency is None:
        return jsonify({ "success": False, "message": "Code not provided" })
    print(f"code {code}")
    print(f"price {price}")
    print(f"currency {currency}")
    print(f"action {action}")
    return place_shares_order(code, price, currency, action)

@app.route('/futu/close-position', methods=['POST'])
def close_position():
    req = request.get_json(force=True)
    code = req.get('code')
    direction = req.get('direction')
    currency = req.get('currency')

    if currency is None:
        currency = DEFAULT_TRADING_CURRENCY

    if code is None  or direction is None:
        return jsonify({ "success": False, "message": "Invalid Body" })

    market_code = get_market_code(currency)
    code = f"{market_code}{code}"
    trd_market = get_trd_market(currency)
    security_firm = get_security_firm(currency)

    # Trading context
    trd_ctx = OpenSecTradeContext(filter_trdmarket=trd_market, host=FUTU_OPEN_D_HOST, port=FUTU_OPEN_D_PORT,
                                  security_firm=security_firm)
    ret, data = trd_ctx.position_list_query(trd_env=FUTU_ENV)
    if ret == RET_OK:
        print(data)
        orders = data.to_dict('records')
        print(orders)
        if len(orders) == 0:  # 如果持仓列表不为空
            return jsonify({ "success": False, "message": "No order exists" })
        # Find the target order to close
        target_order = None
        for order in orders:
            if order['code'] == code:
                target_order = order
                break

        if target_order is None:
            print('No order found')
            return jsonify({ "success": False, "message": f"Order with {code} was not found" })

        action = None # Action is determined by the direction
        if direction == Direction.Call.value:
            print(f"Close call = {Action.Sell.value}")
            action = Action.Sell.value
        elif direction == Direction.Put.value:
            print(f"Close put = {Action.Buy.value}")
            action = Action.Buy.value
        else:
            return jsonify({ "success": False, "message": "Exception:Invalid direction" })

        print(f"Close position: {code}")
        print({
            "qty": target_order['qty'],
            "code": code,
            "order_type": OrderType.MARKET,
            "trd_side": action,
            "trd_env": FUTU_ENV,
            "session": Session.RTH
        })
        ret, data = trd_ctx.place_order(
            price=500.0,
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
        return jsonify({"success": False, "message": data })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)