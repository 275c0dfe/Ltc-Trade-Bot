import socket
import network
class empty:
    pass

content = ""
urlInfo = empty()
urlInfo.qs = {}
urlInfo.qs_found = False
urlInfo.URI = ""
cookie = {}
client = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
ticker = network.Ticker()