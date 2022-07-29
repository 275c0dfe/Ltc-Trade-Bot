
import network
import kraken
import time
import os
import brain
import server
import threading


mongo_key = "rOv9c0GrlZpq8MXs"

api_sec = "GIz/HrbyV3T9OjtVVtoBxoCX0HicUtCKXiLhwX8mO1IyDbAGprEkweQ4YWp9b5gmLozhufyxFqXhka4DQuaFEg=="
api_key = "mUN/wXLMwEof0jmutBJdEJbhf8jHft/PbILRTeWCyhd8/UA+A7IGHsxU"
client = network.Client(api_key , api_sec , "0123")

pair = "LTCUSD"
coinName = "XLTCZUSD"
ltc_Ticker = network.Ticker()
ltc_Ticker.pair = pair
ltc_Ticker.name = coinName

rateLimit = 3
tradingBrain = brain.brain(client)
res = client.getClientBalance().json()["result"]
tradingBrain.usd = float(res["ZUSD"])
tradingBrain.ltc = float(res["XLTC"])

config = {"Enable_Brain_Trading":True}


httpServer = server.HttpServer(("" , 80) , "Trading_Server" , ltc_Ticker , tradingBrain)

tradingBrain.history.append("Web Server Initializing")
httpServer.addFile("scripts/route.py" , cacheable=False)
httpServer.addFile("web/index.html" , cacheable=False)
httpServer.addFile("web/api.js" , cacheable=False)
httpServer.addFile("web/style.css" , cacheable=False)
httpServer.addFile("web/login.html" , cacheable=False)
httpServer.addFile("scripts/getData.py" , cacheable=False)
httpServer.addFile("scripts/shutdown.py" , cacheable=False)
httpServer.addFile("scripts/login.py" , cacheable=False)
httpServer.addFile("scripts/setkey.py" , cacheable=False)
httpServer.addFile("scripts/setData.py" , cacheable=False)
httpServer.addFile("TradeHistory.txt")

httpServer.tokens["$JqueryRefrence"] = "<script src=\"https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js\"></script> "
httpServer.tokens["$ApiRefrence"] = "<script src='/web/api.js' ></script>"
httpServer.tokens["$StyleRefrence"] = "<link rel=\"stylesheet\" href=\"/web/style.css\">"
httpServer.tokens["from scripts.requestRefrences import *"] = ""
httpServer.tokens["$FontLink"] = "<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\"><link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin><link href=\"https://fonts.googleapis.com/css2?family=Ubuntu&display=swap\" rel=\"stylesheet\">"

httpServer.Data["Access_Key"] = "devKey001"


httpServer.bind()
httpServer.listen(10)

tradingBrain.history.append("Web Server Initialized")
tradingBrain.history.append("Kraken Client Started")
Server_Thread = threading.Thread(target=httpServer.accept_loop)
Server_Thread.start()
print("Server Started")
time.sleep(0.5)


def bot_loop():
    while tradingBrain.loop:
        try:
            ud = ltc_Ticker.lastUpdate
            if time.time() - ud > rateLimit:
                ltc_Ticker.update()
                if tradingBrain.enabled:
                    tradingBrain.update(ltc_Ticker.tickerData)
            time.sleep(0.25)
        except KeyboardInterrupt:
            break

bot_thread = threading.Thread(target=bot_loop)
print("Starting bot")
bot_thread.start()
