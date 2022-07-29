from scripts.requestRefrences import *
url = urlInfo.URI
qs = urlInfo.qs
content = ""
if urlInfo.qs_found:

    try:
        val = qs["bot_enable"]
        if val == "true":
            bot_brain.enabled = True
            content = "OK"
        if val == "false":
            bot_brain.enabled = False
            
        
    except:
        pass