from entities.orders import Order, OrderExecutor, OrderExecutorType
from kiteconnect.connect import KiteConnect
from entities.zerodha import ZerodhaKite
import threading
import time
import os


class TradeBot(OrderExecutor):
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

    def entry_strategy(self):
        raise NotImplementedError

    def exit_strategy(self, order: Order):
        raise NotImplementedError

    def _exit_strategy(self, interval=10):
        while True:
            tickers = set(self.entries.keys()).copy()

            for ticker in tickers:
                if ticker in self.entries:
                    self.exit_strategy(self.entries[ticker])

            time.sleep(interval)

    def start(self):
        entry_thread = threading.Thread(target=self.entry_strategy)
        exit_thread = threading.Thread(target=self._exit_strategy)

        entry_thread.start()
        exit_thread.start()
