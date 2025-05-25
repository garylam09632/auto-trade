from futu import *
from config import *
from helper import *
from type import *
import time

code = 'US.TSLA'
#
# quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)  # 创建行情对象
# print(quote_ctx.get_market_snapshot('HK.00700'))  # 获取港股 HK.00700 的快照数据
# quote_ctx.close() # 关闭对象，防止连接条数用尽

# print(FUTU_OPEN_D_HOST)
# print(FUTU_OPEN_D_PORT)
# print(FUTU_ENV)
# print(Action.Buy.value)

# Place Order
# trd_ctx = OpenSecTradeContext(host=FUTU_OPEN_D_HOST, port=FUTU_OPEN_D_PORT) # 创建交易对象
# ret, data = trd_ctx.place_order(price=500.0, qty=1000, code="HK.01860", order_type=OrderType.MARKET, trd_side=TrdSide.BUY, trd_env=TrdEnv.SIMULATE)  # 模拟交易，下单（如果是真实环境交易，在此之前需要先解锁交易密码）
# if ret == RET_OK:
#     print(data)
#     order = data.to_dict('records')
#     print(order)
# else:
#     print(data)
# trd_ctx.close()

## Get Order History
# trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
# ret, data = trd_ctx.history_order_list_query(trd_env=TrdEnv.SIMULATE)
# if ret == RET_OK:
#     orders_list = data.to_dict('records')
#     print("All orders as list of dicts:")
#     print(orders_list)
#     if data.shape[0] > 0:  # 如果订单列表不为空
#         print(data['order_id'][0])  # 获取持仓第一个订单号
#         print(data['order_id'].values.tolist())  # 转为 list
# else:
#     print('history_order_list_query error: ', data)
#
# trd_ctx.close()

## Get Market State
# quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
#
# ret, data = quote_ctx.get_market_state(['US.TSLA'])
# if ret == RET_OK:
#     print(data)
# else:
#     print('error:', data)
# quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽

# Get account list
# trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.HK, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
# ret, data = trd_ctx.get_acc_list()
# if ret == RET_OK:
#     print(data)
#     print(data['acc_id'][0])  # 取第一个账号
#     print(data['acc_id'].values.tolist())  # 转为 list
# else:
#     print('get_acc_list error: ', data)
# trd_ctx.close()

# Get position list
# trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.US, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUINC)
# ret, data = trd_ctx.position_list_query(trd_env=FUTU_ENV)
# if ret == RET_OK:
#     orders = data.to_dict('records')
#     print(orders)
#     if len(orders) == 0:  # 如果持仓列表不为空
#         print('No order exists')

#     # Find the target order to close
#     target_order = None
#     for order in orders:
#         if order['code'] == code:
#             target_order = order
#             break

#     if target_order is None:
#         print('No order found')
#     else:
#         print(f"Target close qty: {target_order['qty']}")

#     # ret, data = trd_ctx.place_order(
#     #     price=500.0,
#     #     qty=1,
#     #     code=code,
#     #     order_type=OrderType.MARKET,
#     #     trd_side=TrdSide.SELL,
#     #     trd_env=FUTU_ENV,
#     #     session=Session.ETH
#     # )  # 模拟交易，下单（如果是真实环境交易，在此之前需要先解锁交易密码）
#     # if ret == RET_OK:
#     #     print(data)
#     #     return jsonify({"success": True}), 201
#     # else:
#     #     print('place_order fail')
#     #     print(data)
#     #     return jsonify({"success": False, "message": "PlaceOrder failed"})
# else:
#     print('position_list_query error: ', data)
# trd_ctx.close()

# Get option code of the nearest strike date

# Variables
# option_type = OptionType.CALL # ALL, CALL, PUT
# option_code_index = 1 # Which option code to choose
#
quote_ctx = OpenQuoteContext(host=FUTU_OPEN_D_HOST, port=FUTU_OPEN_D_PORT)

# # # Subscribe the stock to get the real-time price
# ret_sub, err_message = quote_ctx.subscribe([code], [SubType.QUOTE, SubType.TICKER], subscribe_push=False, session=Session.ALL)
# if ret_sub == RET_OK:
#     ret, data = quote_ctx.get_stock_quote([code])
#     if ret == RET_OK:
#         print(data)
#     else:
#         print('error:', data)
# else:
#     print('subscription failed', err_message)
# quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽

ret1, data1 = quote_ctx.get_option_expiration_date(code=code)

filter1 = OptionDataFilter()
filter1.delta_min = 0

target_price = 338
filter1.delta_max = +0.4
filter1.gamma_min = 0.01
filter1.open_interest_min = 100

if ret1 == RET_OK:
    date = data1['strike_time'].values.tolist()[0] # Get the first strike date
    print('Strike date:' + date)
    ret2, data2 = quote_ctx.get_option_chain(code=code, start=date, end=date)
    if ret2 == RET_OK:
        print(data2.to_dict('records'))
        arr = data2['name'].values.tolist()

        price_tolerance = 5.0  # How far from target price to consider
        max_options_per_type = 6  # Max options to show per call/put

        # Initialize collections
        calls = []
        puts = []

        for code in arr:
            parts = code.split(' ')
            option_type = parts[2][-1]  # 'C' or 'P'
            price = float(parts[2][:-1])  # Convert price to float

            # Check if price is within tolerance (including target price)
            if abs(price - target_price) <= price_tolerance:
                if option_type == 'C':
                    calls.append((abs(price - target_price), code))  # (distance, code)
                else:
                    puts.append((abs(price - target_price), code))

        # Sort by proximity to target price and limit results
        calls = sorted(calls, key=lambda x: x[0])[:max_options_per_type]
        puts = sorted(puts, key=lambda x: x[0])[:max_options_per_type]

        # Combine and extract just the codes
        results = [item[1] for item in calls + puts]

        print("Options near target price:")
        for option in results:
            print(convert_option_format(option))

        # print(data2['code'][0])  # 取第一条的股票代码
        # print(data2['code'].values.tolist())  # 转为 list
    else:
        print('error:', data2)
    # for date in expiration_date_list:
    #     ret2, data2 = quote_ctx.get_option_chain(code=code, start=date, end=date, data_filter=filter1)
    #     if ret2 == RET_OK:
    #         print(data2)
    #         print(data2['code'][0])  # 取第一条的股票代码
    #         print(data2['code'].values.tolist())  # 转为 list
    #     else:
    #         print('error:', data2)
    #     time.sleep(10)
else:
    print('error:', data1)
quote_ctx.close()  # 结束后记得关闭当条连接，防止连接条数用尽

trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.US, host=FUTU_OPEN_D_HOST, port=FUTU_OPEN_D_PORT, security_firm=SecurityFirm.FUTUINC)

ret, data = trd_ctx.get_acc_list()
if ret == RET_OK:
    print(data)
    print(data['acc_id'][0])  # 取第一个账号
    print(data['acc_id'].values.tolist())  # 转为 list
else:
    print('get_acc_list error: ', data)

ret2, data2 = trd_ctx.place_order(
    price=0.97,   
    acc_id=14806998,
    qty=3,
    code="US.TSLA250530C342500",
    order_type=OrderType.MARKET,
    trd_side=TrdSide.BUY,
    trd_env=FUTU_ENV,
    session=Session.RTH
)
if ret2 == RET_OK:
    print(data2.to_dict('records'))
    # print(data2.values.tolist())
else:
    print('error:', data2)
trd_ctx.close()