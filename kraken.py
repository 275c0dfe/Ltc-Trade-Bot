import base64 , urllib , hmac , hashlib
import requests
import time

def get_kraken_signature(urlpath, data, secret):

    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()

    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()

def get_pair_qs(pair):
    qs = "?pair="
    qs+=pair
    return  qs

class AskData:
    def __init__(self) -> None:
        self.price = 0
        self.wholeLotVolume = 0
        self.lotVolume = 0

class BidData:
    def __init__(self) -> None:
        self.price = 0
        self.wholeLotVolume = 0
        self.lotVolume = 0

class LastTradeClose:
    def __init__(self) -> None:
        self.price = 0
        self.lotVolume = 0

class Volume:
    def __init__(self) -> None:
        self.today = 0
        self.DaytoHour = 0

class PriceData:
    def __init__(self) -> None:
        self.today = 0
        self.DaytoHour = 0

class TickerData:
    def __init__(self) -> None:
        self.ask = AskData()
        self.bid = BidData()
        self.lastTradeClose = LastTradeClose()
        self.volume = Volume()
        self.VWAPrice = Volume()
        self.tradeCount = Volume()
        self.high = PriceData()
        self.low = PriceData()
        self.open = 0

def loadTicker(data):
    ticker = TickerData()
    
    ask = ticker.ask
    ask.price = float(data["a"][0])
    ask.wholeLotVolume = float(data["a"][1])
    ask.lotVolume = float(data["a"][2])
    ticker.ask = ask

    bid = ticker.bid
    bid.price = float(data["b"][0])
    bid.wholeLotVolume = float(data["b"][1])
    bid.lotVolume = float(data["b"][2])
    ticker.bid = bid

    ltc = ticker.lastTradeClose
    ltc.price = float(data["c"][0])
    ltc.lotVolume = float(data["c"][1])
    ticker.lastTradeClose = ltc

    vol = ticker.volume
    vol.today = float(data["v"][0])
    vol.DaytoHour = float(data["v"][1])
    ticker.volume = vol

    wvol = ticker.VWAPrice
    wvol.today = float(data["p"][0])
    wvol.DaytoHour = float(data["p"][1])
    ticker.VWAPrice = wvol

    tc = ticker.tradeCount
    tc.today = float(data["t"][0])
    tc.DaytoHour = float(data["t"][1])
    ticker.tradeCount = tc

    low = ticker.low
    low.today = float(data["l"][0])
    low.DaytoHour = float(data["l"][1])
    ticker.low = low

    high = ticker.high
    high.today = float(data["h"][0])
    high.DaytoHour = float(data["h"][1])
    ticker.high = high
    ticker.open = float(data["o"])
    return ticker

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
        signiture = get_kraken_signature(uri , data , self._api_secret)
        headers = {}
        headers["API-Key"] = self._api_key
        headers["API-Sign"] = signiture
        res = requests.post(self._api_url + uri , headers=headers , data=data)
        return res

    def getClientOpenOrders(self):
        uri = "/0/private/OpenOrders"
        data = {"nonce":str(int(1000*time.time())) , "trades":True}
        signiture = get_kraken_signature(uri , data , self._api_secret)
        headers = {}
        headers["API-Key"] = self._api_key
        headers["API-Sign"] = signiture
        res = requests.post(self._api_url + uri , headers=headers , data=data)
        return res

    def createOrder(self , order_type , volume , pair , price):

        uri = "/0/private/AddOrder"
        data = {"nonce":str(int(1000*time.time())) , "ordertype":"limit" , "type":order_type , "volume":volume , "pair":pair , "price":price}
        signiture = get_kraken_signature(uri , data , self._api_secret)
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
        self.tickerData = TickerData()

    def update(self):
        try:
            uri = "https://api.kraken.com/0/public/Ticker" + get_pair_qs(self.pair)
            resp = requests.get(uri)
            
            self.tickerData = loadTicker(resp.json()["result"][self.pair])
            ask = self.tickerData.ask.price
            bid = self.tickerData.bid.price
            spread = ask - bid
            self.spread = spread
            self.lastUpdate = time.time()
        except Exception as e:
            print("Ticker Exception Thrown: " , e)
            pass
