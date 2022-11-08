from scripts.requestRefrences import *



import random
import math
def randInt(min , mx):
    r= random.random() - min
    a = r * mx
    return math.floor(a) + min

content = ""


try:
    ses_id = Data["Current_Login_Id"]
except:
    Data["Current_Login_Id"] = "_Undef(" + str(randInt(2 , 512)) + ")"

try:
    cs_id = cookie["Session_Id"]
    if cs_id == ses_id:
        content = "<html><script>function redir(){window.location.replace('/web/index.html');} redir();</script></html>"
    else:
        content = "<html><script>function redir(){window.location.replace('/web/login.html');} redir();</script></html>"

except:
    content = "<html><script>function redir(){window.location.replace('/web/login.html');} redir();</script></html>"