
import network
import kraken
import time
import os
import brain

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



while True:
    try:
        ud = ltc_Ticker.lastUpdate
        if time.time() - ud > rateLimit:
            ltc_Ticker.update()
            tradingBrain.update(ltc_Ticker.tickerData)
        
        os.system("cls")
        print(pair)
        print("Ask(Buy): " + str(ltc_Ticker.tickerData.ask.price))
        print("Bid(Sell): " + str(ltc_Ticker.tickerData.bid.price))
        print("Spread: " + str(ltc_Ticker.spread) + "\n")
        print("Time Since Update: " + str(time.time()- ud))
        ts = tradingBrain.ltc
        if ts < 0.0001:
            ts = "<0.0001"
        else:
            ts = str(ts)
        print("Balance:" + str(ts) + " LTC")
        print("Fait Balance: " + str(tradingBrain.usd) + " Usd\n")
        print("Brain Last Sell: " +str(tradingBrain.lastSell))
        print("Brain Sell Activation: " +str(tradingBrain.sellActivation) + "\n")
        print("Brain Last Buy: " +str(tradingBrain.lastBuy))
        print("Brain Buy Activation: " +str(tradingBrain.BuyActivation) + "\n")
        print("Current Order| Amount:" + str(tradingBrain.currentOrder[0]) + " | Price: " + str(tradingBrain.currentOrder[1]) + " | Type: " + tradingBrain.currentOrder[2])
        print("Order Closed: " + str(not tradingBrain.waitForOrder) + "\n")
        print("Brain Ticks: " + str(tradingBrain.ticks))
        print("Brain History: ")
        try:
            th = tradingBrain.history[len(tradingBrain.history)-15:]
            for a in th:
                print("     " + a)
        except:
            pass

        time.sleep(0.25)
    except KeyboardInterrupt:
        break
