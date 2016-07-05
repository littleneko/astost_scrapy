# -*- coding: utf-8 -*-


# Start your middleware class
class ProxyMiddleware(object):

    # overwrite process request
    def process_request(self, request, spider):
        # Set the location of the proxy
        request.meta['proxy'] = "http://127.0.0.1:8118"

