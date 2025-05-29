from flask import Flask, jsonify, request, copy_current_request_context
from futu import *
from config import *
from helper import *
from type import *
from util import *
import queue
import threading
from time import sleep
from functools import wraps

app = Flask(__name__)

# Create a request queue and worker control
request_queue = queue.Queue()
worker_running = True
queue_lock = threading.Lock()

# Worker thread function
def worker():
    print("Worker thread started")  # Debug
    while worker_running:
        try:
            with queue_lock:
                if not request_queue.empty():
                    task = request_queue.get_nowait()
                    print(f"Worker processing task: {task}")  # Debug

                    func = task['func']
                    args = task['args']
                    kwargs = task['kwargs']
                    callback = task['callback']

                    try:
                        result = func(*args, **kwargs)
                        if callback:
                            callback(result)
                    except Exception as e:
                        print(f"Error processing task: {e}")
                    finally:
                        request_queue.task_done()
                else:
                    time.sleep(0.1)  # Small sleep to prevent busy waiting
        except Exception as e:
            print(f"Worker error: {e}")
            time.sleep(1)


# Start worker thread
worker_thread = threading.Thread(target=worker)
worker_thread.daemon = True
worker_thread.start()

# Decorator to ensure app context
def with_app_context(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        with app.app_context():
            return f(*args, **kwargs)

    return wrapper

def shutdown_worker():
    global worker_running
    worker_running = False
    worker_thread.join()

@with_app_context
def process_place_order(req):
    code = req.get('code')
    price = float(req.get('price'))
    action = req.get('action')
    currency = req.get('currency')
    trade_type = req.get('type')

    if currency is None:
        currency = DEFAULT_TRADING_CURRENCY

    if code is None or currency is None:
        return jsonify({"success": False, "message": "Code not provided"}), 400

    if trade_type == TradeType.Shares.value:
        return place_shares_order(code, price, currency, action)
    elif trade_type == TradeType.Option.value:
        direction = req.get('direction')
        if direction is None:
            return jsonify({"success": False, "message": "Direction not provided"}), 400
        return place_option_order(code, price, currency, action, direction)
    else:
        return jsonify({"success": False, "message": "Invalid type"}), 400


@with_app_context
def process_close_position(req):
    code = req.get('code')
    direction = req.get('direction')
    currency = req.get('currency')
    trade_type = req.get('type')

    if currency is None:
        currency = DEFAULT_TRADING_CURRENCY

    if code is None:
        return jsonify({"success": False, "message": "Invalid Body"}), 400

    if trade_type == TradeType.Shares.value:
        return close_shares_position(code, currency)
    elif trade_type == TradeType.Option.value:
        if direction is None:
            return jsonify({"success": False, "message": "Direction not provided"}), 400
        return close_option_position(code, currency, direction=direction)
    else:
        return jsonify({"success": False, "message": "Invalid type"}), 400


@app.route('/futu/place-order', methods=['POST'])
def place_order():
    req = request.get_json(force=True)
    if req.get('action') is None or req.get('price') is None or req.get('type') is None:
        return jsonify({"success": False}), 400

    response_holder = {'response': None}

    def callback(result):
        response_holder['response'] = result

    task = {
        'func': process_place_order,
        'args': [req],
        'kwargs': {},
        'callback': callback
    }

    request_queue.put(task)

    timeout = 30  # seconds
    for _ in range(timeout * 10):
        if response_holder['response'] is not None:
            return response_holder['response']
        sleep(0.1)

    return jsonify({"success": False, "message": "Request timeout"}), 504


@app.route('/futu/close-position', methods=['POST'])
def close_position():
    req = request.get_json(force=True)

    response_holder = {'response': None}

    def callback(result):
        response_holder['response'] = result

    task = {
        'func': process_close_position,
        'args': [req],
        'kwargs': {},
        'callback': callback
    }

    request_queue.put(task)

    timeout = 30  # seconds
    for _ in range(timeout * 10):
        if response_holder['response'] is not None:
            return response_holder['response']
        sleep(0.1)

    return jsonify({"success": False, "message": "Request timeout"}), 504

@app.route('/futu/test', methods=['POST'])
def test_api():
    req = request.get_json(force=True)
    print("Received test request")  # Debug

    response_holder = {'response': None}
    callback_event = threading.Event()

    def callback(result):
        response_holder['response'] = result
        callback_event.set()
        print("Callback executed")  # Debug

    task = {
        'func': test_func,
        'args': [req],
        'kwargs': {},
        'callback': callback
    }

    print("Adding task to queue")  # Debug
    with queue_lock:
        request_queue.put(task)
    print(f"Queue size: {request_queue.qsize()}")  # Debug

    # Wait for callback with timeout
    if not callback_event.wait(timeout=30):
        print("Timeout waiting for callback")  # Debug
        return jsonify({"success": False, "message": "Request timeout"}), 504

    print("Returning response")  # Debug
    return response_holder['response']


@with_app_context
def test_func(req):
    print("Processing test function")  # Debug
    code = req.get('code')
    print(f"Processing code: {code}")  # Debug
    time.sleep(5)  # Artificial delay to demonstrate queue working
    return jsonify({"success": True, "message": "Success", "code": code}), 200

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_worker()
    return jsonify({"success": True, "message": "Worker shutting down"})


if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    finally:
        shutdown_worker()