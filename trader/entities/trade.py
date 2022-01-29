import json
from kiteconnect import KiteConnect


class Trade:
    LIMIT_ORDER = KiteConnect.ORDER_TYPE_LIMIT
    MARKET_ORDER = KiteConnect.ORDER_TYPE_MARKET

    EXCHANGE_NSE = KiteConnect.EXCHANGE_NSE
    EXCHANGE_NFO = KiteConnect.EXCHANGE_NFO

    BUY = KiteConnect.TRANSACTION_TYPE_BUY
    SELL = KiteConnect.TRANSACTION_TYPE_SELL

    def __init__(
        self,
        trading_symbol: str,
        exchange: str,
        order_type: str,
        transaction_type: str,
        quantity: int,
        entry_price: int = None,
        price: int = None,
    ):
        self.trading_symbol: str = trading_symbol
        self.exchange: str = exchange
        self.quantity: int = quantity
        self.entry_price: int = entry_price
        self.price: int = price
        self.order_type = order_type
        self.transaction_type = transaction_type

    def place_order(self, kite: KiteConnect):
        if self.order_type == self.LIMIT_ORDER and self.price == None:
            raise Exception("provide a price to execute limit order")

        order = kite.place_order(
            KiteConnect.VARIETY_REGULAR,
            self.exchange,
            self.trading_symbol,
            self.transaction_type,
            self.quantity,
            KiteConnect.PRODUCT_NRML,
            self.order_type,
            price=self.price if self.order_type == self.LIMIT_ORDER else None,
        )

        return order

    def json(self):
        return json.dumps(
            {
                "trading_symbol": self.trading_symbol,
                "exchange": self.exchange,
                "quantity": self.quantity,
                "entry_price": self.entry_price,
                "price": self.price,
            },
            indent=1,
        )
