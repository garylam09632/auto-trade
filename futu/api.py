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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)