import base64, re
from scrapy.dupefilter import RFPDupeFilter

proxyServer = "http://proxy.abuyun.com:9010"
proxyUser = "HAK012H884KTB99P"
proxyPass = "DC43E53E984C8382"
proxyAuth = "Basic " + (base64.b64encode((proxyUser + ":" + proxyPass).encode())).decode()

class ProxyMiddleware(object):
    def process_request(self, request, spider):
        request.meta["proxy"] = proxyServer
        request.headers["Proxy-Authorization"] = proxyAuth

class IDDupeFilter(RFPDupeFilter):
    def request_fingerprint(self, request):
        if 'thread' in request.url:
            tid = re.search('(thread-\d+-\d+)', request.url)
            tid = tid.groups()[0]
            return tid
        else:
            return super(IDDupeFilter, self).request_fingerprint(request)