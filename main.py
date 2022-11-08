import kraken
import os
import TradeAlgorithms
import litehttp
import ServerBindings
import threading
import time

api_sec = os.environ["kraken_Secret"]
api_key = os.environ["kraken_Key"]
print("Secret: " , api_sec)
print("Api Key: " , api_key)

Currency = ["LTCUSD" , "XLTCZUSD"]



client = kraken.Client(api_key , api_sec , "null")

ticker =  kraken.Ticker()
ticker.name = Currency[0]
ticker.pair =  Currency[1]

ticker.update()

rateLimit = 2

tradeAlgo = TradeAlgorithms.brain(client)
res = client.getClientBalance().json()


res = res["result"]

tradeAlgo.usd = float(res["ZUSD"])
tradeAlgo.ltc = float(res["XLTC"])

config = {"Enable_Trading_Brain":True}
httpServer = litehttp.HttpServer(("" , 80) , "" , ticker , tradeAlgo)
ServerBindings.bindFilestoServer(httpServer)
httpServer.bind()
httpServer.listen(10)
tradeAlgo.history.append("Kraken Client Started")

httpServerThread = threading.Thread(target=httpServer.accept_loop)
httpServerThread.start()

tradeAlgo.history.append("Http Server Active")


def bot_loop():
    while tradeAlgo.loop:
        try:
            ud = ticker.lastUpdate
            if time.time() - ud > rateLimit:
                
                ticker.update()
                if tradeAlgo.enabled:
                    tradeAlgo.update(ticker.tickerData)
            time.sleep(0.25)
        except KeyboardInterrupt:
            break

algoThread = threading.Thread(target= bot_loop)
algoThread.start()
print("LiteTrade Running")
