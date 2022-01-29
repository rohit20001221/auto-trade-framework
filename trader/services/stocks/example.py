from interfaces.bot import TradeBot
from entities.orders import Order
from entities.trade import Trade
import time


class Example(TradeBot):
    tickers = ["ACC", "TCS", "INFY"]

    def entry_strategy(self):
        while True:
            for ticker in self.tickers:
                trade = Trade(
                    ticker, Trade.EXCHANGE_NSE, Trade.LIMIT_ORDER, Trade.BUY, 1, 0, 0
                )

                try:
                    self.enter_trade(trade)

                    self.logger.success(f"[**] completed placing trade for {ticker}")
                except Exception as e:
                    self.logger.error(f"[**] failed to place trade for {ticker} {e}")
                    continue

            time.sleep(300)

    def exit_strategy(self, order: Order):
        return
