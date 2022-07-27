from requestRefrences import *
url = urlInfo.URI
qs = urlInfo.qs
if urlInfo.qs_found:
    ticker.update()
    try:
        val = qs["getTicker"]
        if val == 'true':
            content = str(ticker.tickerData.ask.price)
    except:
        pass