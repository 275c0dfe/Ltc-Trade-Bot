from scripts.requestRefrences import *
wServer.is_serving = False
bot_brain.loop = False
import requests
requests.get("http://localhost" , timeout=1)
content = ""