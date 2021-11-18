#!/usr/bin/env python
import argparse

import http.server
from utils.util import Utils
import os
import urllib2

import dnslib


class CustomHTTPRequestHandler(http.server.BaseHTTPRequestHandler, object):

    def __init__(self, request, client_address, server):
        global replica_server
        self.cached_replica_server = replica_server
        super(CustomHTTPRequestHandler, self).__init__(request, client_address, server)


    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        html_page_body = self.cached_replica_server.run(self.path)
        self.wfile.write(html_page_body)
        self.wfile.close()
        return


class ReplicaServer:
    CACHE_FOLDER = "./replica_cache/"
    ORIGIN_PORT = "8080"
    ORIGIN_PROTOCOL = "http://"

    def __init__(self, port, origin):
        self.cachedFiles = {}
        self.port = port
        self.origin = origin
        self.origin_url = self.ORIGIN_PROTOCOL + origin + ":" + self.ORIGIN_PORT
        for ff in os.listdir(self.CACHE_FOLDER):
            if os.path.isfile(self.CACHE_FOLDER + ff):
                self.cachedFiles[ff] = True

    def start_http_server(self, server_class=http.server.HTTPServer, handler_class=CustomHTTPRequestHandler):
        server_address = ('', self.port)
        httpd = server_class(server_address, handler_class)
        httpd.serve_forever()

    def run(self, path):
        local_file_path = path.replace("/", "")
        if local_file_path in self.cachedFiles:
            print ("Return cached file")
            return Utils.get_file_contents(self.CACHE_FOLDER + local_file_path)
        try:
            request = urllib2.Request(self.origin_url + path)
            request.add_header("Accept-Encoding", "utf-8")
            response = urllib2.urlopen(request)
        except Exception as ex:
            print (path)
            print (ex)
            return ""

        response_body = response.read()
        Utils.save_file(self.CACHE_FOLDER + path, response_body)
        return response_body


if __name__ == "__main__":
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("-p", type=int)
    args_parser.add_argument("-n", type=str)
    args_parser.parse_args()

    args = args_parser.parse_args()

    # replica_server.run("/Catherine_Howard")
    replica_server = ReplicaServer(args.p, args.n)

    replica_server.start_http_server()
