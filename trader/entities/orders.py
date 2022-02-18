from entities.zerodha import LiveTicker
from kiteconnect import KiteConnect
from typing import Dict, Iterator
from entities.trade import Trade
from enum import Enum
from pymongo import MongoClient
from pymongo.database import Database, Collection


class OrderExecutorType(Enum):
    SINGLE = "single"
    MULTIPLE = "multiple"


class Order:
    def __init__(self, trading_symbol, exchange, total_quantity, average_entry_price):
        self.trading_symbol = trading_symbol
        self.exchange = exchange
        self.total_quantity = total_quantity
        self.average_entry_price = average_entry_price

    def add_trade(self, trade: Trade):
        self.total_quantity += trade.quantity
        self.average_entry_price += trade.entry_price

        self.average_entry_price /= 2


class OrderDatabase(MongoClient):
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name

        self.db: Database = self["autotrade"]
        self.collection: Collection = self.db[name]

    def create_order(self, order: Order) -> None:
        _filter = {"trading_symbol": order.trading_symbol}

        _update = {
            "$set": {
                "trading_symbol": order.trading_symbol,
                "average_entry_price": order.average_entry_price,
                "exchange": order.exchange,
                "total_quantity": order.total_quantity,
            }
        }

        self.collection.update_one(_filter, _update, upsert=True)

    def get_order(self, trading_symbol) -> Order:
        order = self.collection.find_one({"trading_symbol": trading_symbol})

        return Order(
            order["trade"],
            order["exchange"],
            order["total_quantity"],
            order["average_entry_price"],
        )

    def delete_order(self, trading_symbol) -> None:
        self.collection.delete_one({"trading_symbol": trading_symbol})

    def orders(self) -> Iterator[Order]:
        if self.collection.count_documents({}) > 0:
            for order in self.collection.find():
                if order:
                    yield Order(
                        order["trading_symbol"],
                        order["exchange"],
                        order["total_quantity"],
                        order["average_entry_price"],
                    )
        else:
            return []


class OrderExecutor:
    def __init__(
        self,
        mode: OrderExecutorType = OrderExecutorType.MULTIPLE,
    ):
        self.entries: Dict[str, Order] = dict()
        self.__db = OrderDatabase(name=self.name, host="mongodb://db")

        self.mode: OrderExecutorType = mode

    def enter_order(self, trade: Trade):
        if trade.trading_symbol not in self.entries:
            order = Order(
                trade.trading_symbol,
                trade.exchange,
                trade.quantity,
                trade.entry_price,
            )
            self.__db.create_order(order)
        else:
            if self.mode == OrderExecutorType.MULTIPLE:
                order = self.__db.get_order(trade.trading_symbol).add_trade(trade)
                self.__db.create_order(order)

    def clean_order(self, trading_symbol: str):
        self.__db.delete_order(trading_symbol)

    def get_orders(self) -> Iterator[Order]:
        return self.__db.orders()

    def enter_trade(self, trade: Trade, kite: KiteConnect, quote: LiveTicker):
        try:
            trade.entry_price = quote.last_price
            trade.place_order(kite)
        except Exception as e:
            raise Exception(f"failed to place order {e}")
        else:
            self.enter_order(trade)

    def exit_trade(self, trade: Trade, kite: KiteConnect, quote: LiveTicker):
        try:
            trade.entry_price = quote.last_price
            trade.place_order(kite)
        except Exception as e:
            raise Exception(f"failed to place order {e}")
        else:
            self.clean_order(trade.trading_symbol)
