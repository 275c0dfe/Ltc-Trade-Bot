import socket
import threading
import time

content_types = {}
content_types["txt"] = "text/html"
content_types["html"] = "text/html"
content_types["py"] = "text/html"


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

class qs_info:
    def __init__(self):
        self.qs = []
        self.qs_found = False
        self.URI = ""

def ParseQs(qss):
    qs = {}
    v = qss.split("&")
    for i in v:
        qs[i.split("=")[0].replace("+", " ")] = i.split("=")[1].replace("+", " ")
    return qs

class HttpServer:
    def __init__(self, host, name, ticker, tb):
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
        self.debug = False
        self.ticker = ticker
        self.trade_brain = tb
        self.Data = {}
        connection = {}
        connection["raw_socket"] = self.socket
        connection["bound"] = False
        connection["listening"] = False
        connection["transmitting"] = False
        connection["recieving"] = False
        
    def bind(self):
        self.socket.bind(self.host)
        
    def handle_client(self, client):
        ClientSocket = client["sock"]  # Get socket from client
        rawRequest = ClientSocket.recv(self.d_size)  # Recieve Request Data

        _request_start = time.time()

        if self.debug:
            print("new request: " + str(client["addr"]))

        try:  # Try to parse the request
            req = self.parser.parseClient(rawRequest.decode())
        except Exception as e:  # Handle Fail
            if self.debug:
                print("Unable to parse Request")
                print(e)
            return 0

        url = req["url"]  # Grab Url from Request Object
        cookie = {}
        passThroughCookieString = ""
        is_cookied = False
        try:
            rawCookie = req["headers"]["Cookie"]
            is_cookied = True
            passThroughCookieString = rawCookie
            items = rawCookie.split(";")
            for it in items:
                j = it.split("=")
                k = j[0]
                v = j[1]
                cookie[k] = v
        except Exception as e:
            if self.debug:
                print("Cookie Exeption: " + str(e))

        # QS Support
        _qs = qs_info()
        _qs.qs = url.split("?")
        _qs.qs_found = False

        if len(_qs.qs) > 1:
            _qs.URI = _qs.qs[0]
            _qs.qs = _qs.qs[1]
            if _qs.qs != "":
                _qs.qs = ParseQs(_qs.qs)
            else:
                _qs.qs = "empty"
            _qs.qs_found = True
            url = _qs.URI
        else:
            _qs.URI = url

        if _qs.qs_found:
            if self.debug:
                print("##QS##: " + str(_qs.qs))

        cache = self.cache
        locatedResource = False
        responseObject = {}  # Response Config Object
        cid = -1  # Resource Id in Cache
        resourceContent = ""  # Resource Data
        responseString = ""  # Response String
        resourceObject = {}

        if url == "/":  # Fix / 404
            url = "/" + self.files[0]["PATH"]

        for i in range(len(cache)):  # Check If Resource Cached
            ce = cache[i]
            if url == "/" + ce["path"]:
                locatedResource = True
                cid = i
                resourceContent = ce["content"]
                try:
                    ce["action"]()
                except:
                    pass
                break

        if locatedResource == False:  # Check File Index for Resource
            for fileObject in self.files:
                if url == "/" + fileObject["PATH"]:
                    resourceObject = fileObject
                    locatedResource = True
                    resourceHandle = open(fileObject["PATH"], "r")
                    resourceContent = resourceHandle.read()
                    resourceHandle.close()

                    # Cache System
                    try:
                        self.rrc[url] += 1
                    except:
                        self.rrc[url] = 1
                    if self.rrc[url] > 5:
                        if fileObject not in self.uncacheable:
                            try:
                                resourceObject["action"]
                                self.forceCache(
                                    fileObject["PATH"], action=fileObject["action"]
                                )
                            except:
                                if self.debug:
                                    print("caching: " + fileObject["PATH"])
                                self.forceCache(fileObject["PATH"])
                    break

        if locatedResource:  # Respond With Resource

            # detokenize page
            tokens = self.tokens.keys()
            for token in list(tokens):
                while token in resourceContent:
                    resourceContent = resourceContent.replace(token, self.tokens[token])

            # Check file type for special types
            ftype = url.split(".")[1]
            if ftype == "py":
                _dscript_start = time.time()
                execStr = resourceContent
                envir = {}
                envir["Data"] = self.Data
                envir["wServer"] = self
                envir["content"] = resourceContent
                envir["urlInfo"] = _qs
                envir["cookie"] = cookie
                envir["client"] = client
                envir["ticker"] = self.ticker
                envir["bot_brain"] = self.trade_brain
                try:
                    exec(execStr, envir)
                    resourceContent = envir["content"]
                except Exception as e:
                    print(e)
                _dscript_end = time.time()
                if (_dscript_end - _dscript_start) * 1000 > 200:
                    print(
                        f"Http Server Warning: Dynamic Script {url} took over 200ms. Time Took {1000*(_dscript_end - _dscript_start)}"
                    )

            responseObject["status_code"] = 200
            responseObject["content"] = resourceContent
            heads = {}
            try:
                heads["Content-Type"] = content_types[ftype]
            except:
                heads["Content-Type"] = "text/html"

            if is_cookied:
                heads["Cookie"] = passThroughCookieString
            heads["Server"] = "Python"
            heads["connection"] = "close"
            responseObject["headers"] = heads
            responseString = self.parser.createRes(responseObject)
            try:
                if resourceObject["action"] != None:
                    resourceObject["action"]()
            except KeyError:
                pass
        else:  # Resource Not Found, Respond With 404 Error

            responseObject["status_code"] = 404
            responseObject["content"] = "404 Not Found"
            heads = {}
            heads["Content-Type"] = "text/html"
            heads["Server"] = "Python"
            heads["connection"] = "close"
            responseObject["headers"] = heads
            responseString = self.parser.createRes(responseObject)

        ClientSocket.send(responseString.encode())
        _request_end = time.time()
        if (_request_end - _request_start) * 1000 > 300:
            print(
                f"Http Server: Performance Warning Request Took Over 300 ms. Time Taken: {1000*(_request_end-_request_start)}"
            )
        ClientSocket.close()
        if self.debug:
            print("request served: " + url)
            print("status: " + str(responseObject["status_code"]))
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
        self.is_serving = True

    def addFile(self, path, action=None, cacheable=True):
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
