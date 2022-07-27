import socket
import threading
import time



class HttpParser:
    def __init__(self):
        self.ver = "1.0"
        self.log = []
        self.max_log = 16

    def parseClient(self, sreq):
        sr = sreq.split("\r\n")
        l = sr[0].split(" ")
        method = l[0]
        url = l[1]
        http_ver = l[2]
        req = {}
        req["method"] = method
        req["url"] = url
        req["http_ver"] = http_ver
        sr = sr[1:]
        headers = {}
        for l in sr:
            if l != "":
                b = l.split(": ")
                headers[b[0]] = b[1]
        req["headers"] = headers
        if len(self.log) > self.max_log:
            self.log.pop()
            self.log.append(req)
        else:
            self.log.append(req)
        return req

    def createRes(self, reso):
        codes = {}
        codes["404"] = "Not Found"
        codes["200"] = "OK"
        res = "HTTP/1.1 "
        res += str(reso["status_code"]) + " "
        res += codes[str(reso["status_code"])] + "\r\n"
        header = ""
        for k in reso["headers"].keys():
            header += k + ": " + reso["headers"][k] + "\r\n"
        header += "\r\n"
        res += header
        res += reso["content"]
        res += ""
        return res


class CObject:
    pass


def noop():
    pass


def ParseQs(qss):
    qs = {}
    v = qss.split("&")
    for i in v:
        qs[i.split("=")[0].replace("+", " ")] = i.split("=")[1].replace("+", " ")
    return qs


class HttpServer:
    def __init__(self, host, name , ticker):
        self.host = host
        self.name = name
        self.files = []
        self.uncacheable = []
        self.cache = []
        self.max_cache = 8
        self.rrc = {}
        self.active_clients = []
        self.threads = []
        self.parser = HttpParser()
        self.d_size = (1024 * 1024) * 512  # 512 KB
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tokens = {}
        self.is_serving = False
        self.is_debug = False
        self.ticker = ticker
        connection = {}
        connection["raw_socket"] = self.socket
        connection["bound"] = False
        connection["listening"] = False
        connection["transmitting"] = False
        connection["recieving"] = False
        self.connection = connection

    def bind(self):
        self.socket.bind(self.host)
        self.connection["bound"] = True

    def handle_client(self, client):
        csock = client["sock"]  # Get socket from client
        upr = csock.recv(self.d_size)  # Recieve Request Data
        if self.is_debug:
            print("new request: " + str(client["addr"]))

        try:  # Try to parse the request
            req = self.parser.parseClient(upr.decode())
        except Exception as e:  # Handle Fail
            if self.is_debug:
                print("Unable to parse Request")
                print(e)
            return 0

        url = req["url"]  # Grab Url from Request Object
        cookie = {}
        passCook = ""
        is_cookied = False
        try:
            cook = req["headers"]["Cookie"]
            is_cookied = True
            passCook = cook
            items = cook.split(";")
            for it in items:
                j = it.split("=")
                k = j[0]
                v = j[1]
                cookie[k] = v
            
        except Exception as e:
            if self.is_debug:
                print("Cookie Exeption: " + str(e))
        
        # QS Support
        urlo = CObject()
        urlo.qs = url.split("?")
        urlo.qs_found = False
        
        if len(urlo.qs) > 1:
            urlo.URI = urlo.qs[0]
            urlo.qs = urlo.qs[1]
            if urlo.qs != "":
                urlo.qs = ParseQs(urlo.qs)
            else:
                urlo.qs = "empty"
            urlo.qs_found = True
            url = urlo.URI
        else:
            urlo.URI = url

        if urlo.qs_found:
            if self.is_debug:
                print("##QS##: " + str(urlo.qs))

        #
        cache = self.cache  # Get Cache locally
        located = False  # Kinda Self Explanitory
        res = {}  # Response Config Object
        cid = -1  # Resource Id in Cache
        rcont = ""  # Resource Data
        sres = ""  # Response String
        hobjec = {}

        if url == "/":  # Fix / 404
            url = "/" + self.files[0]["PATH"]
        
        for i in range(len(cache)):  # Check If Resource Cached
            ce = cache[i]
            if url == "/" + ce["path"]:
                located = True
                cid = i
                rcont = ce["content"]
                try:
                    ce["action"]()
                except:
                    pass
                break
        if located == False:  # Check File Index for Resource
            for p in self.files:
                if url == "/" + p["PATH"]:
                    hobjec = p
                    located = True
                    f = open(p["PATH"], "r")
                    rcont = f.read()
                    f.close()
                    try:
                        self.rrc[url] += 1
                    except:
                        self.rrc[url] = 1
                    if self.rrc[url] > 5:
                        if p not in self.uncacheable:
                            try:
                                hobjec["action"]
                                self.forceCache(p["PATH"], action=p["action"])
                            except:
                                if self.is_debug:
                                    print("caching: " + p["PATH"])
                                self.forceCache(p["PATH"])

                    break

        if located:  # Respond With Resource

            #detokenize page
            tokens = self.tokens.keys()
            for token in list(tokens):
                while token in rcont:
                    rcont = rcont.replace(token , self.tokens[token])


            types = {}
            types["txt"] = "text/html"
            types["html"] = "text/html"
            types["py"] = "text/html"
            ftype = url.split(".")[1]

            if ftype == "py":
                execStr = rcont
                envir = {}
                envir["content"] = rcont
                envir["urlInfo"] = urlo
                envir["cookie"] = cookie
                envir["client"] = client
                envir["ticker"] = self.ticker
                try:
                    exec(execStr , envir)
                    rcont = envir["content"]
                except Exception as e:
                    print(e)



            res["status_code"] = 200
            res["content"] = rcont
            heads = {}
            try:
                heads["Content-Type"] = types[ftype]
            except:
                heads["Content-Type"] = "text/html"
            
            if is_cookied:
                heads["Cookie"] = passCook
            heads["Server"] = "Python"
            heads["connection"] = "close"
            res["headers"] = heads
            sres = self.parser.createRes(res)
            try:
                if hobjec["action"] != None:
                    hobjec["action"]()
            except KeyError:
                pass
        else:  # Resource Not Found, Respond With 404 Error

            res["status_code"] = 404
            res["content"] = "404 Not Found"
            heads = {}
            heads["Content-Type"] = "text/html"
            heads["Server"] = "Python"
            heads["connection"] = "close"
            res["headers"] = heads
            sres = self.parser.createRes(res)

        csock.send(sres.encode())  # Send Response string
        csock.close()  # Close Socket
        if self.is_debug:
            print("request served: " + url)
            print("status: " + str(res["status_code"]))
            print("cached: " + str(cid != -1))
            if cid != -1:
                print("Cache Id: " + str(cid))

    def accept_loop(self):
        while self.is_serving:
            cli, addr = self.socket.accept()
            client = {}
            client["sock"] = cli
            client["addr"] = addr
            thr = threading.Thread(target=self.handle_client, args=[client])
            thr.start()
            self.threads.append(thr)

    def listen(self, backlog):
        self.socket.listen(backlog)
        self.connection["listening"] = True
        self.is_serving = True

    def addFile(self, path, action=None , cacheable = True):
        if not cacheable:
            self.uncacheable.append({"PATH": path, "action": action})
            
        self.files.append({"PATH": path, "action": action})
            

    def forceCache(self, path, action=None):
        f = open(path, "r")
        txt = f.read()
        f.close()
        ce = {}
        ce["path"] = path
        ce["content"] = txt
        ce["action"] = action
        self.cache.append(ce)
