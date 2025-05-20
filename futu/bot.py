from futu import *
from config import *
import time

code = 'US.TSLA'
#
# quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)  # 创建行情对象
# print(quote_ctx.get_market_snapshot('HK.00700'))  # 获取港股 HK.00700 的快照数据
# quote_ctx.close() # 关闭对象，防止连接条数用尽

print(FUTU_OPEN_D_HOST)
print(FUTU_OPEN_D_PORT)

# Place Order
# trd_ctx = OpenSecTradeContext(host=FUTU_OPEN_D_HOST, port=FUTU_OPEN_D_PORT) # 创建交易对象
# print(trd_ctx.place_order(price=500.0, qty=100, code="HK.00700", order_type=OrderType.MARKET, trd_side=TrdSide.BUY, trd_env=TrdEnv.SIMULATE))  # 模拟交易，下单（如果是真实环境交易，在此之前需要先解锁交易密码）

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
# trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.US, host='127.0.0.1', port=11111,
#                               security_firm=SecurityFirm.FUTUSECURITIES)
# ret, data = trd_ctx.position_list_query(trd_env=FUTU_ENV, code=code)
# if ret == RET_OK:
#     orders = data.to_dict('records')
#     print(orders)
#     if len(orders) == 0:  # 如果持仓列表不为空
#         print('No order exists')
#
#     # Find the target order to close
#     target_order = None
#     for order in orders:
#         if order['code'] == code:
#             target_order = order
#             break
#
#     if target_order is None:
#         print('No order found')
#
#     print(f"Target close qty: {target_order['qty']}")
#
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
option_type = OptionType.CALL # ALL, CALL, PUT
option_code_index = 1 # Which option code to choose

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
ret_sub, err_message = quote_ctx.subscribe([code], [SubType.QUOTE], subscribe_push=False)
ret, data = quote_ctx.get_stock_quote([code])
if ret == RET_OK:
    print(data)
else:
    print('error:', data)

ret1, data1 = quote_ctx.get_option_expiration_date(code=code)

filter1 = OptionDataFilter()
filter1.delta_min = 0
# filter1.delta_max = +0.4
# filter1.gamma_min = 0.01
# filter1.open_interest_min = 100

if ret1 == RET_OK:
    date = data1['strike_time'].values.tolist()[0] # Get the first strike date
    print(date)
    ret2, data2 = quote_ctx.get_option_chain(code=code, start=date, end=date, data_filter=filter1)
    if ret2 == RET_OK:
        print(data2)
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
