import requests
import kraken
import time


class Client:
    def __init__(self , api_key , api_secret , key) -> None:
        
        self._api_key = api_key
        self._api_secret = api_secret
        self._key = key
        self._api_url = "https://api.kraken.com"
        self._locked = False

    def publicRequest(self ,  url):
        uri =  self._api_url + "/0/public" + url
        resp = requests.get(uri)
        return resp.json()

    def getClientBalance(self):
        uri = "/0/private/Balance"
        data = {"nonce":str(int(1000*time.time()))}
        signiture = kraken.get_kraken_signature(uri , data , self._api_secret)
        headers = {}
        headers["API-Key"] = self._api_key
        headers["API-Sign"] = signiture
        res = requests.post(self._api_url + uri , headers=headers , data=data)
        return res

    def getClientOpenOrders(self):
        uri = "/0/private/OpenOrders"
        data = {"nonce":str(int(1000*time.time())) , "trades":True}
        signiture = kraken.get_kraken_signature(uri , data , self._api_secret)
        headers = {}
        headers["API-Key"] = self._api_key
        headers["API-Sign"] = signiture
        res = requests.post(self._api_url + uri , headers=headers , data=data)
        return res

    def createOrder(self , order_type , volume , pair , price):

        
        uri = "/0/private/AddOrder"
        data = {"nonce":str(int(1000*time.time())) , "ordertype":"limit" , "type":order_type , "volume":volume , "pair":pair , "price":price}
        signiture = kraken.get_kraken_signature(uri , data , self._api_secret)
        headers = {}
        headers["API-Key"] = self._api_key
        headers["API-Sign"] = signiture
        res = requests.post(self._api_url + uri , headers=headers , data=data)
        f = open("TradeHistory.txt" , "a")
        f.write(f"#Kraken API Trade. {order_type} {str(volume)}LTC At ${str(price)}\n")
        f.write(res.text + "\n")
        f.close()
        return res.json()

class Ticker:
    def __init__(self) -> None:
        self.pair = ""
        self.name = ""
        self.spread = 0
        self.lastUpdate = 0.0
        self.tickerData = kraken.TickerData()

    def update(self):
        try:
            uri = "https://api.kraken.com/0/public/Ticker" + kraken.get_pair_qs(self.pair)
            resp = requests.get(uri)
            self.tickerData = kraken.loadTicker(resp.json()["result"][self.name])
            ask = self.tickerData.ask.price
            bid = self.tickerData.bid.price
            spread = ask - bid
            self.spread = spread
            self.lastUpdate = time.time()
        except:
            pass
