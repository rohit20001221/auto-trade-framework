from typing import Dict, Iterator
from entities.trade import Trade
from enum import Enum


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


class OrderExecutor:
    def __init__(
        self,
        mode: OrderExecutorType = OrderExecutorType.MULTIPLE,
    ):
        self.entries: Dict[str, Order] = dict()
        self.mode: OrderExecutorType = mode

    def enter_order(self, trade: Trade):
        if trade.trading_symbol not in self.entries:
            self.entries[trade.trading_symbol] = Order(
                trade.trading_symbol,
                trade.exchange,
                trade.quantity,
                trade.entry_price,
            )
        else:
            if self.mode == OrderExecutorType.MULTIPLE:
                self.entries[trade.trading_symbol].add_trade(trade)

    def clean_order(self, trading_symbol: str):
        del self.entries[trading_symbol]

    def get_orders(self) -> Iterator[Order]:
        for trading_symbol in self.entries:
            yield self.entries[trading_symbol]

    def enter_trade(self, trade: Trade):
        self.enter_order(trade)

        # publish the trade to the publisher
        # class to execute the trade

    def exit_trade(self, trade: Trade):
        self.clean_order(trade.trading_symbol)

        # execute the trade here
        # class to execute the trade
