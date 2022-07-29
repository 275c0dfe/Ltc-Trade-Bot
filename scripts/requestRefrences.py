import socket
import network
import brain
import server
class qs_i:
    def __init__(self) -> None:
        self.qs = {}
        self.qs_found = False
        self.URI = ""
    pass

content = ""
urlInfo = empty()
urlInfo.qs = {}
urlInfo.qs_found = False
urlInfo.URI = ""
cookie = {}
client = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
ticker = network.Ticker()
bot_brain = brain.brain(network.Client("" , "" , ""))
wServer = server.HttpServer(("" , 80) , "" , ticker , bot_brain)
Data = {}