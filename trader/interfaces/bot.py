from entities.orders import Order, OrderExecutor, OrderExecutorType
from kiteconnect.connect import KiteConnect
from entities.zerodha import ZerodhaKite
from entities.trade import Trade
import threading
import time
import os


class TradeBot(OrderExecutor):
    class logger:
        @staticmethod
        def success(message):
            print("\033[1m" + "\033[92m" + message + "\033[92m" + "\033[1m")

        @staticmethod
        def error(message):
            print("\033[1m" + "\033[91m" + message + "\033[91m" + "\033[1m")

    def __init__(
        self,
        name: str,
        mode: OrderExecutorType = OrderExecutorType.MULTIPLE,
    ):
        super().__init__(mode=mode)
        self.name = name

        self.kite = KiteConnect(
            api_key=os.environ["API_KEY"], access_token=os.environ["ACCESS_TOKEN"]
        )
        self.zerodha = ZerodhaKite(self.kite)

    def enter_trade(self, trade: Trade):
        try:
            quote = self.zerodha.live_data(trade.trading_symbol)
        except Exception:
            raise Exception("failed to fetch live quote for ticker")

        super().enter_trade(trade, self.kite, quote)

    def exit_trade(self, trade: Trade):
        try:
            quote = self.zerodha.live_data(trade.trading_symbol)
        except Exception:
            raise Exception("failed to fetch live quote for ticker")

        super().exit_trade(trade, self.kite, quote)

    def entry_strategy(self):
        raise NotImplementedError

    def exit_strategy(self, order: Order):
        raise NotImplementedError

    def _exit_strategy(self, interval=10):
        while True:
            for order in self.get_orders():
                self.exit_strategy(order)

            time.sleep(interval)

    def start(self):
        entry_thread = threading.Thread(target=self.entry_strategy)
        exit_thread = threading.Thread(target=self._exit_strategy)

        entry_thread.start()
        exit_thread.start()
