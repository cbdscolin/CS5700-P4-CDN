#!/usr/bin/env python
import argparse
import http.server
from utils.util import Utils
import os
import urllib2
from collections import OrderedDict

import dnslib


class CustomHTTPRequestHandler(http.server.BaseHTTPRequestHandler, object):

    def __init__(self, request, client_address, server):
        global replica_server
        self.cached_replica_server = replica_server
        super(CustomHTTPRequestHandler, self).__init__(request, client_address, server)

    def do_GET(self):
        html_code, html_header, html_page_body = self.cached_replica_server.run(self.path)
        self.send_response(html_code)
        self.send_header("Content-type", "text/html")
        if html_header:
            for header in html_header:
                self.send_header(header, html_header[header])
        self.end_headers()
        self.wfile.write(html_page_body)
        self.wfile.close()
        return


class ReplicaServer:
    CACHE_FOLDER = "./replica_cache/"
    ORIGIN_PORT = "8080"
    ORIGIN_PROTOCOL = "http://"

    GRADING_BEACON_PATH = "/grading/beacon"

    MAX_CACHE_SIZE = 3

    def __init__(self, port, origin):
        self.cachedFiles = OrderedDict()
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

    def mark_file_in_cache(self, file_name, contents):
        Utils.save_file(self.CACHE_FOLDER + file_name, contents)
        self.cachedFiles[file_name] = True

        if len(self.cachedFiles) > self.MAX_CACHE_SIZE:
            file_to_delete, _ = self.cachedFiles.popitem(last=False)
            Utils.delete_file(self.CACHE_FOLDER + file_to_delete)

    def get_cached_file(self, file_name):
        self.cachedFiles.pop(file_name)
        self.cachedFiles[file_name] = True
        return Utils.get_file_contents(self.CACHE_FOLDER + file_name)

    def run(self, path):
        if self.GRADING_BEACON_PATH in path:
            return 204, None, ""

        local_file_path = path.replace("/", "")

        if local_file_path in self.cachedFiles:
            print ("Return cached file")
            return 200, None, self.get_cached_file(local_file_path)
        try:
            request = urllib2.Request(self.origin_url + path)
            request.add_header("Accept-Encoding", "utf-8")
            response = urllib2.urlopen(request)
        except Exception as ex:
            print (path)
            print (ex)
            return 404, None, ""

        response_body = response.read()
        self.mark_file_in_cache(local_file_path, response_body)
        return 200, None, response_body


if __name__ == "__main__":
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("-p", type=int)
    args_parser.add_argument("-n", type=str)
    args_parser.parse_args()

    args = args_parser.parse_args()

    # replica_server.run("/Catherine_Howard")
    replica_server = ReplicaServer(args.p, args.n)

    replica_server.start_http_server()
