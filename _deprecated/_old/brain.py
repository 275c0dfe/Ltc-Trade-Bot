import network
import kraken
import time
import math


class brain:
    def __init__(self, client: network.Client) -> None:
        self.history = []
        self.data = []
        self.ticks = 0
        self.kClient = client

        self.lastBuy = 0
        self.BuyActivation = 0
        self.waitBuy = True
        self.lastSell = 0
        self.sellActivation = 0
        self.waitSell = False

        self.waitForOrder = False

        self.usd = 100
        self.ltc = 0
        self.enabled = True
        self.loop = True

        self.openorders = 0
        self.currentOrder = (0, 0, "")

        self.buyMargin = 0.01
        self.sellMargin = 0.015

    def update(self, ticker: kraken.TickerData):
        action = False
        if self.ticks < 20:
            ab = (ticker.ask.price, ticker.bid.price)
            self.data.append(ab)
            self.lastBuy = ab[1]
            self.BuyActivation = (ab[1]) - (ab[1] * self.buyMargin)
            self.lastSell = ab[0]
            self.history.append(f"Initilizing {100 * (self.ticks/20)}%")
            action = True
        else:
            ab = (ticker.ask.price, ticker.bid.price)

            if self.waitSell:
                if self.sellActivation > (self.lastBuy + 0.20):
                    if self.sellActivation > ticker.bid.price:
                        if not self.waitForOrder:
                            self.waitBuy = True
                            self.waitSell = False
                            sp = ticker.ask.price + (ticker.ask.price * self.sellMargin)

                            oltc = self.ltc
                            usd = self.ltc * sp

                            self.lastSell = sp
                            self.currentOrder = (oltc, sp, "Sell")
                            self.waitForOrder = True

                            ltcs = str(oltc).split(".")
                            if len(ltcs[1]) > 2:
                                ltcs[1] = ltcs[1][:1]
                            ltcs = float(".".join(ltcs))

                            sps = str(sp).split(".")
                            if len(sps[1]) > 2:
                                sps[1] = sps[1][:1]
                            sps = float(".".join(sps))

                            res = self.kClient.createOrder(
                                "sell", oltc, "XLTCZUSD", sps
                            )

                            self.BuyActivation = (
                                (ab[1]) - (ab[1] * self.buyMargin)
                            ) - 0.20
                            self.history.append(
                                "Sell Order Added "
                                + str(oltc)
                                + " LTC/USD For $"
                                + str(sp)
                                + ". Total USD: "
                                + str(usd)
                            )
                            action = True
                            time.sleep(1.2)

            if self.waitBuy:
                if ticker.ask.price < self.BuyActivation:
                    if self.BuyActivation < self.lastSell:
                        if not self.waitForOrder:
                            self.waitBuy = False
                            self.waitSell = True
                            bp = ticker.bid.price - (ticker.bid.price * self.buyMargin)

                            ousd = self.usd

                            ltc = self.usd / bp

                            self.lastBuy = bp

                            self.currentOrder = (ltc, bp, "Buy")
                            self.waitForOrder = True

                            ltcs = str(ltc).split(".")
                            if len(ltcs[1]) > 2:
                                ltcs[1] = ltcs[1][:1]
                            ltcs = float(".".join(ltcs))

                            bps = str(bp).split(".")
                            if len(bps[1]) > 2:
                                bps[1] = bps[1][:2]
                            bps = float(".".join(bps))

                            res = self.kClient.createOrder("buy", ltc, "XLTCZUSD", bps)

                            self.sellActivation = (ab[0]) + (ab[0] * self.sellMargin)
                            self.history.append(
                                "Buy Order Added "
                                + str(ltc)
                                + " LTC/USD For $"
                                + str(bp)
                                + ". Total USD: "
                                + str(ousd)
                            )
                            action = True
                            time.sleep(1.2)

            if self.waitForOrder:

                od = self.currentOrder
                amt = od[0]
                price = od[1]
                typ = od[2]
                try:
                    open_orders = len(
                        self.kClient.getClientOpenOrders().json()["result"]["open"]
                    )
                except:
                    open_orders = 1
                    self.history.append("Error Reading Open Orders")
                    pass

                if open_orders < 1:

                    if typ == "Buy":
                        res = self.kClient.getClientBalance().json()["result"]
                        self.usd = float(res["ZUSD"])
                        self.ltc = float(res["XLTC"])

                        self.history.append(
                            "Buy Order Filled "
                            + str(amt)
                            + " LTC/USD For $"
                            + str(price)
                            + ". Total USD: "
                            + str(amt * ab[0])
                        )
                        f = open("TradeHistory.txt", "a")
                        f.write(
                            f"Buy Order Filled {str(amt)} LTC/USD For ${ab[1]}. Total Usd: ${amt*price}\n"
                        )
                        f.close()
                        self.waitForOrder = False
                        action = True

                    if typ == "Sell":

                        res = self.kClient.getClientBalance().json()["result"]
                        self.usd = float(res["ZUSD"])
                        self.ltc = float(res["XLTC"])

                        self.history.append(
                            "Sell Order Filled "
                            + str(amt)
                            + " LTC/USD For $"
                            + str(price)
                            + ". Total USD: "
                            + str(amt * price)
                        )
                        f = open("TradeHistory.txt", "a")
                        f.write(
                            f"Sell Order Filled {str(amt)} LTC/USD For ${ab[0]}. Total Usd: {amt * ab[0]}\n"
                        )
                        f.close()
                        self.waitForOrder = False
                        action = True

        # if len(self.history) > 128:
        #   self.history = self.history[len(self.history) - 17 :]
        #  self.history.append("Cleared Log")

        self.ticks += 1
