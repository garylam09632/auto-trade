import time
from futu import *
from util import *

direction = Direction.Put.value

option_positions = [
  {"code": "US.TSLA250530P360000", "stock_name": "TSLA"},
  {"code": "US.TSLA250530P355000", "stock_name": "TSLA"},
  {"code": "US.TSLA250530P352500", "stock_name": "TSLA"},
  {"code": "US.TSLA250530C370000", "stock_name": "TSLA"},
  {"code": "US.TSLA250530C367500", "stock_name": "TSLA"},
  {"code": "US.TSLA250530C365000", "stock_name": "TSLA"},
  {"code": "US.TSLA", "stock_name": "TSLA"},
  {"code": "US.NVDA250530C138000", "stock_name": "NVDA"},
  {"code": "US.CRWV250530P120000", "stock_name": "CRWV"},
  {"code": "US.CRWV250530P118000", "stock_name": "CRWV"},
  {"code": "US.CRWV250530P116000", "stock_name": "CRWV"},
  {"code": "US.CRWV250530P115000", "stock_name": "CRWV"},
  {"code": "US.CRWV250530C120000", "stock_name": "CRWV"},
  {"code": "US.CRWV250530C118000", "stock_name": "CRWV"},
  {"code": "US.CRWV250530C117000", "stock_name": "CRWV"}
]

option_positions = distinguish_shares_and_options(option_positions, 'US.TSLA')['options']
if len(option_positions) == 0:
    print({"success": False, "message": "No option positions"})

# Separate with calls and puts
option_positions = separate_calls_puts(option_positions)

# If the closing direction is call, only close call positions, else close put positions
if direction == Direction.Call.value:
    option_positions = option_positions['calls']
else:
    option_positions = option_positions['puts']

for position in option_positions:
    print(position)