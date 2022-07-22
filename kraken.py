import urllib.parse
import hashlib
import hmac
import base64

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
