from interfaces.bot import TradeBot
from entities.orders import Order
import time


class Example(TradeBot):
    tickers = ["ACC", "TCS", "INFY"]

    def entry_strategy(self):
        while True:
            for ticker in self.tickers:
                print(self.zerodha.live_data(ticker))

            time.sleep(300)

    def exit_strategy(self, order: Order):
        return
