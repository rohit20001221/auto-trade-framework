from typing import DefaultDict, Dict, List, Union
import datetime
from enum import Enum
from kiteconnect.connect import KiteConnect
import redis
import requests
import time
import json


class OHLC:
    def __init__(self, ohlc: dict):
        self.open = ohlc.get("open")
        self.high = ohlc.get("high")
        self.low = ohlc.get("low")
        self.close = ohlc.get("close")


class Depth:
    class DepthInfo:
        def __init__(self, depth: dict):
            self.price = depth["price"]
            self.orders = depth["orders"]
            self.quantity = depth["quantity"]

    def __init__(self, depth: dict):
        self.buy: List[Depth.DepthInfo] = []
        self.sell: List[Depth.DepthInfo] = []

        for depth_info in depth.get("buy", []):
            self.buy.append(Depth.DepthInfo(depth_info))

        for depth_info in depth.get("sell", []):
            self.sell.append(Depth.DepthInfo(depth_info))


class LiveTicker:
    MODE_FULL = "full"
    MODE_QUOTE = "quote"
    MODE_LTP = "ltp"

    def __init__(self, live_ticker: dict):
        self.instrument_token: int = live_ticker.get("instrument_token")
        self.mode: Union[
            LiveTicker.MODE_FULL, LiveTicker.MODE_QUOTE, LiveTicker.MODE_LTP
        ] = live_ticker.get("mode")
        self.volume: int = live_ticker.get("volume")
        self.last_price: float = live_ticker.get("last_price")
        self.average_price: float = live_ticker.get("average_price")
        self.last_quantity: int = live_ticker.get("last_quantity")
        self.total_buy_quantity: int = live_ticker.get("total_buy_quantity")
        self.total_sell_quantity: int = live_ticker.get("total_sell_quantity")
        self.change: float = live_ticker.get("change")
        self.last_trade_time: datetime.datetime = live_ticker.get("last_trade_time")
        self.timestamp: datetime.datetime = live_ticker.get("timestamp")
        self.oi: int = live_ticker.get("oi")
        self.oi_day_low: int = live_ticker.get("oi_day_low")
        self.ohlc = OHLC(live_ticker.get("ohlc", {}))
        self.tradable: bool = live_ticker.get("tradable", False)
        self.depth: Depth = Depth(live_ticker.get("depth", {}))


class HistoricalDataInterval(Enum):
    INTERVAL_1_MINUTE = "1minuite"
    INTERVAL_3_MINUTE = "3minute"
    INTERVAL_5_MINUTE = "5minute"
    INTERVAL_10_MINUTE = "10minute"
    INTERVAL_15_MINUTE = "15minute"
    INTERVAL_1_DAY = "1day"


class HistoricalOHLC(OHLC):
    def __init__(self, ohlc: dict):
        super().__init__(ohlc)
        self.time: datetime.datetime = ohlc.get("time")


class IndexHistorical:
    def __init__(self, nifty: List[HistoricalOHLC], bank_nifty: List[HistoricalOHLC]):
        self.nifty = nifty
        self.bank_nifty = bank_nifty


from collections import defaultdict


class ZerodhaKite:
    def __init__(self, kite: KiteConnect):
        self.kite = kite
        self.instruments = self.kite.instruments()

        self.token_map = {}
        for instrument in self.instruments:
            self.token_map[instrument["tradingsymbol"]] = instrument

        self.redis = redis.StrictRedis(host="redis_server")

        self.historical_data_cache: DefaultDict[
            str, List[HistoricalOHLC]
        ] = defaultdict(list)

    def _get_live(self, endpoint):
        return requests.get("http://live_data/" + endpoint)

    def historical_data(
        self,
        tradingsymbol: str,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        interval: HistoricalDataInterval,
    ) -> List[HistoricalOHLC]:
        # check for the data in cache
        if self.redis.get(f"historical:{tradingsymbol}"):
            # if there is a cache hit get the historical data from cache
            _data = json.loads(
                self.redis.get(f"historical:{interval.value}:{tradingsymbol}")
            )
        else:
            _data = self.kite.historical_data(
                self.token_map[tradingsymbol]["instrument_token"],
                start_time,
                end_time,
                interval.value,
            )

            # add the historical data to cache
            self.redis.set(
                f"historical:{interval.value}:{tradingsymbol}",
                json.dumps(_data, default=str),
                self.get_expiry(interval.value),
            )

        data: List[HistoricalOHLC] = []
        for ohlc in _data:
            data.append(HistoricalOHLC(ohlc))

        return data

    def historical_data_today(
        self, tradingsymbol, interval: HistoricalDataInterval
    ) -> List[HistoricalOHLC]:
        data = self.historical_data(
            tradingsymbol, datetime.date.today(), datetime.date.today(), interval
        )

        return data

    def live_data(self, tradingsymbol) -> LiveTicker:
        data = self.redis.get(tradingsymbol)

        if data == None:
            self._get_live(
                "subscribe"
                + "/"
                + str(self.token_map[tradingsymbol]["instrument_token"])
            )
            time.sleep(2)

            data = self.redis.get(tradingsymbol)

        return LiveTicker(json.loads(data))
