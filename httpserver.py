#!/usr/bin/env python
import urllib

import http.client
from utils.util import Utils
import os


class ReplicaServer:

    CACHE_FOLDER = "./replica_cache/"

    def __init__(self):
        self.cachedFiles = {}
        for ff in os.listdir(self.CACHE_FOLDER):
            if os.path.isfile(self.CACHE_FOLDER + ff):
                self.cachedFiles[ff] = True

    def run(self, path):
        local_file_path = path.replace("/", "")
        if local_file_path in self.cachedFiles:
            print ("Return cached file")
            return Utils.get_file_contents(self.CACHE_FOLDER + local_file_path)
        conn = http.client.HTTPConnection("cs5700cdnorigin.ccs.neu.edu:8080")
        conn.request("GET", path)
        response = conn.getresponse()
        print(response.status, response.reason)

        response_body = response.read()
        Utils.save_file(self.CACHE_FOLDER + path, response_body)


if __name__ == "__main__":
    ReplicaServer().run("/Catherine_Howard")
