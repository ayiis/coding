#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
    https://stackoverflow.com/questions/22882667/socks-proxy-in-tornado-asynchttpclient
"""
import tornado.httpclient
tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
async_http_client = tornado.httpclient.AsyncHTTPClient(max_clients=1000)


# def prepare_curl_socks5(curl):
#     """
#         指定代理的类型，默认 HTTP
#         PROXYTYPE_HTTP / PROXYTYPE_SOCKS4 / PROXYTYPE_SOCKS5 / PROXYTYPE_SOCKS5_HOSTNAME
#     """
#     import pycurl
#     curl.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5)
#     # curl.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_HTTP)  # 默认


def http_request(req_data):
    return async_http_client.fetch(tornado.httpclient.HTTPRequest(
        url=req_data["url"],
        method=req_data["method"],
        headers=req_data["headers"],
        body=req_data.get("body"),
        decompress_response=True,
        # prepare_curl_callback=prepare_curl_socks5,
        proxy_host=req_data.get("proxy_host"),
        proxy_port=req_data.get("proxy_port"),
        request_timeout=req_data.get("request_timeout") or 30,
        connect_timeout=req_data.get("request_timeout") or 30
    ), raise_error=False)
