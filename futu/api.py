from flask import Flask, jsonify, request
from futu import *
from config import *
from helper import *

app = Flask(__name__)

# POST place_order
@app.route('/futu/place-order', methods=['POST'])
def place_order():
    req = request.get_json(force=True)
    code = req.get('code')
    currency = DEFAULT_TRADING_CURRENCY
    if req.get('currency') is not None:
        currency = req.get('currency')

    print(f"currency = {currency}")
    action = TrdSide.BUY if req.get("action") == "Buy" else TrdSide.SELL
    if code is None or currency is None:
        return jsonify({ "success": False, "message": "Code not provided" })
    market_code = get_market_code(currency)
    code = f"{market_code}{code}"
    trd_market = get_trd_market(currency)
    print("trd_market:", trd_market)
    trd_ctx = OpenSecTradeContext(filter_trdmarket=trd_market, host=FUTU_OPEN_D_HOST, port=FUTU_OPEN_D_PORT, security_firm=SecurityFirm.FUTUINC)
    ret, data = trd_ctx.acctradinginfo_query(order_type=OrderType.NORMAL, code=code, price=400, trd_env=TrdEnv.SIMULATE)
    if ret == RET_OK:
        print(data)
        max_buy = data['max_cash_buy'][0]  # 最大融资可买数量
        max_sell = data['max_sell_short'][0]
        print(max_buy * STOCK_ORDER_LIMIT)
        ret, data = trd_ctx.place_order(
            price=400,
            qty=1,
            code=code,
            order_type=OrderType.MARKET,
            trd_side=action,
            trd_env=FUTU_ENV,
            session=Session.RTH
        ) # 模拟交易，下单（如果是真实环境交易，在此之前需要先解锁交易密码）
        if ret == RET_OK:
            print(data)
            return jsonify({ "success": True }), 201
        else:
            print(data)
            return jsonify({ "success": False, "message": data })
    else:
        print('acc_trading_info_query error: ', data)
        return jsonify({ "success": False }), 400

@app.route('/futu/close_position', methods=['POST'])
def close_position():
    req = request.get_json(force=True)
    code = req.get('code')
    currency = req.get('currency')
    if code is None or currency is None:
        return jsonify({ "success": False, "message": "Code not provided" })
    market_code = get_market_code(currency)
    code = f"{market_code}.{code}"
    trd_market = get_trd_market(currency)

    # Trading context
    trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.US, host=FUTU_OPEN_D_HOST, port=FUTU_OPEN_D_PORT,
                                  security_firm=SecurityFirm.FUTUSECURITIES)
    ret, data = trd_ctx.position_list_query(trd_env=FUTU_ENV, code=code)
    if ret == RET_OK:
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

        ret, data = trd_ctx.place_order(
            price=500.0,
            qty=1,
            code=code,
            order_type=OrderType.MARKET,
            trd_side=TrdSide.SELL,
            trd_env=FUTU_ENV,
            session=Session.ETH
        )  # 模拟交易，下单（如果是真实环境交易，在此之前需要先解锁交易密码）
        return jsonify({"success": True}), 201
        # if ret == RET_OK:
        #     print(data)
        #     return jsonify({"success": True}), 201
        # else:
        #     print('place_order fail')
        #     print(data)
        #     return jsonify({"success": False, "message": "PlaceOrder failed"})
    else:
        print('position_list_query error: ', data)
        return jsonify({"success": False, "message": data })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)