'''Function Binds All Files For Application To Server'''
def bindFilestoServer(httpServer):
    httpServer.addFile("scripts/route.py" , cacheable=False)
    httpServer.addFile("web/index.html" , cacheable=False)
    httpServer.addFile("web/api.js" , cacheable=False)
    httpServer.addFile("web/style.css" , cacheable=False)
    httpServer.addFile("web/login.html" , cacheable=False)
    httpServer.addFile("scripts/getData.py" , cacheable=False)
    httpServer.addFile("scripts/shutdown.py" , cacheable=False)
    httpServer.addFile("scripts/login.py" , cacheable=False)
    httpServer.addFile("scripts/setkey.py" , cacheable=False)
    httpServer.addFile("scripts/setData.py" , cacheable=False)
    httpServer.addFile("TradeHistory.txt")
    httpServer.tokens["$JqueryRefrence"] = "<script src=\"https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js\"></script> "
    httpServer.tokens["$ApiRefrence"] = "<script src='/web/api.js' ></script>"
    httpServer.tokens["$StyleRefrence"] = "<link rel=\"stylesheet\" href=\"/web/style.css\">"
    httpServer.tokens["from scripts.requestRefrences import *"] = ""
    httpServer.tokens["$FontLink"] = "<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\"><link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin><link href=\"https://fonts.googleapis.com/css2?family=Ubuntu&display=swap\" rel=\"stylesheet\">"
    httpServer.Data["Access_Key"] = "devKey001"
