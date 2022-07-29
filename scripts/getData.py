from scripts.requestRefrences import *
url = urlInfo.URI
qs = urlInfo.qs
content = ""
if urlInfo.qs_found:

    #Get History
    try:
        val = qs["getHistory"]
        if val == "true":
            s = ""
            for j in bot_brain.history:
                s += j + "\n"
            content = s
            
            pass
        pass
    except:
        pass

    try:
        val = qs["getBalance"]
        if val == "true":
            content = ",".join([str(bot_brain.ltc) , str(bot_brain.usd)])
    except Exception as e:
        pass

    try:
        val = qs["getBotInfo"]
        if val == "true":
            content = ",".join([str(bot_brain.enabled) , str(bot_brain.lastBuy)  , str(bot_brain.lastSell) , str(bot_brain.buyMargin)  , str(bot_brain.sellMargin)])
    except:
        pass 


    #Ticker Data
    try:
        val = qs["getTicker"]
        if val == 'true':
            
            content = str(ticker.tickerData.ask.price)
    except:
        pass