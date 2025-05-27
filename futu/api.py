from flask import Flask, jsonify, request
from futu import *
from config import *
from helper import *
from type import *
from util import *

app = Flask(__name__)

# POST place_order
@app.route('/futu/place-order', methods=['POST'])
def place_order():
    req = request.get_json(force=True)
    if req.get('action') is None or req.get('price') is None or req.get('type') is None:
        return jsonify({ "success": False }), 400
    
    code = req.get('code')
    price = float(req.get('price'))
    action = req.get('action')
    currency = req.get('currency')
    trade_type = req.get('type')

    if currency is None:
        currency = DEFAULT_TRADING_CURRENCY

    if code is None or currency is None:
        return jsonify({ "success": False, "message": "Code not provided" })
    print(f"code {code}")
    print(f"price {price}")
    print(f"currency {currency}")
    print(f"action {action}")
    print(f"trade_type {trade_type}")

    if trade_type == TradeType.Shares.value:
        return place_shares_order(code, price, currency, action)
    elif trade_type == TradeType.Option.value:
        direction = req.get('direction')
        if direction is None:
            return jsonify({"success": False, "message": "Direction not provided"})
        return place_option_order(code, price, currency, action, direction)
    else:
        return jsonify({ "success": False, "message": "Invalid type" }), 400

@app.route('/futu/close-position', methods=['POST'])
def close_position():
    req = request.get_json(force=True)
    code = req.get('code')
    direction = req.get('direction')
    currency = req.get('currency')
    trade_type = req.get('type')

    if currency is None:
        currency = DEFAULT_TRADING_CURRENCY

    if code is None:
        return jsonify({ "success": False, "message": "Invalid Body" })

    if trade_type == TradeType.Shares.value:
        return close_shares_position(code, currency)
    elif trade_type == TradeType.Option.value:
        if direction is None:
            return jsonify({"success": False, "message": "Direction not provided"})
        return close_option_position(code, currency, direction=direction)
    else:
        return jsonify({ "success": False, "message": "Invalid type" }), 400

    market_code = get_market_code(currency)
    code = f"{market_code}{code}"
    trd_market = get_trd_market(currency)
    security_firm = get_security_firm(currency)

    # Trading context
    trd_ctx = OpenSecTradeContext(filter_trdmarket=trd_market, host=FUTU_OPEN_D_HOST, port=FUTU_OPEN_D_PORT,
                                  security_firm=security_firm)
    ret, data = trd_ctx.position_list_query(trd_env=FUTU_ENV, acc_id=14806997)
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
            # price=500.0,
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