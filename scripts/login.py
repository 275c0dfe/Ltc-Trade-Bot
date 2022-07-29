from scripts.requestRefrences import *
import generation
url = urlInfo.URI
qs = urlInfo.qs
content = ""
if urlInfo.qs_found:
    k = qs["Key"]
    if k == Data["Access_Key"]:
        Data["Current_Login_Id"]= generation.randStr(16)
        
        content = Data["Current_Login_Id"]
