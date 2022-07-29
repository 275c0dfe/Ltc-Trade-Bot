from scripts.requestRefrences import *
url = urlInfo.URI
qs = urlInfo.qs
content = ""
if urlInfo.qs_found:
    try:
        val = qs["enable_bot"]
        if val == "true":
            bot_brain.enabled = True
            content = "OK"
        if val == "false":
            bot_brain.enabled = False
            content = "OK"
    except:
        pass


    try:
        val = qs["buy_input"]
        val = val.replace("!Period" , ".")
        bot_brain.lastBuy = float(val)
        content = "OK"
    except:
        pass

    try:
        val = qs["sell_input"]
        val = val.replace("!Period" , ".")
        bot_brain.lastSell = float(val)
        content = "OK"
    except:
        pass

    try:
        val = qs["buy_margin"]
        val = val.replace("!Period" , ".")
        bot_brain.lastBuy = float(val)
        content = "OK"
    except:
        pass

    try:
        val = qs["sell_margin"]
        val = val.replace("!Period" , ".")
        bot_brain.lastSell = float(val)
        content = "OK"
    except:
        pass