from enum import Enum
from dataclasses import dataclass
from typing import Optional

class TradeType(Enum):
    Shares = "SHARES"
    Option = "OPTION"

class Action(Enum):
    Buy = "BUY"
    Sell = "SELL"

class Direction(Enum):
    Call = "CALL" # Long
    Put = "PUT" # Short

class Currency(Enum):
    Usd = "USD"
    Hkd = "HKD"

@dataclass
class Alert:
    code: str
    type: TradeType
    action: Action
    direction: Optional[Direction] = None
    currency: Optional[Currency] = None