from enum import Enum
import json


class TradeType(Enum):
    INDEXOPT = "INDEXOPT"
    INDEXFUT = "INDEXFUT"
    STOCKOPT = "STOCKOPT"
    STOCK = "STOCK"
    STOCKFUT = "STOCKFUT"


class TradeTag(Enum):
    ENTRY = "ENTRY"
    EXIT = "EXIT"


class TradeEndpoint(Enum):
    MARKET_ORDER_BUY = "/place/market_order/buy"
    MARKET_ORDER_SELL = "/place/market_order/sell"
    LIMIT_ORDER_BUY = "/place/limit_order/buy"
    LIMIT_ORDER_SELL = "/place/limit_order/sell"


class Trade:
    def __init__(
        self,
        endpoint: TradeEndpoint,
        trading_symbol: str,
        exchange: str,
        quantity: int,
        tag: TradeTag,
        publisher: str,
        entry_price: int,
        price: int,
        ltp: int,
        type: TradeType,
        max_quantity: float = float("inf"),
    ):
        self.endpoint: TradeEndpoint = endpoint
        self.trading_symbol: str = trading_symbol
        self.exchange: str = exchange
        self.quantity: int = quantity
        self.tag: TradeTag = tag
        self.publisher: str = publisher
        self.entry_price: int = entry_price
        self.price: int = price
        self.ltp: int = ltp
        self.type: TradeType = type
        self.max_quantity = max_quantity

    def json(self):
        return json.dumps(
            {
                "endpoint": self.endpoint.value,
                "trading_symbol": self.trading_symbol,
                "exchange": self.exchange,
                "quantity": self.quantity,
                "tag": self.tag.value,
                "publisher": self.publisher,
                "entry_price": self.entry_price,
                "price": self.price,
                "ltp": self.ltp,
                "type": self.type.value,
                "max_quantity": self.max_quantity,
            },
            indent=1,
        )
