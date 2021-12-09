import os
import urllib.request
from collections import OrderedDict
import http.server

from utils.util import Utils


# Custom class to handle http request.
class CustomHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    cached_replica_server = None

    # Constructor for the class.
    def __init__(self, request, client_address, server):
        # Cache the instance of replica server to reuse
        global replica_server
        super().__init__(request, client_address, server)

    @staticmethod
    def save_replica_server_instance(replica_instance):
        CustomHTTPRequestHandler.cached_replica_server = replica_instance


    # Override the do_GET method of base class to handle get requests in a custom way.
    def do_GET(self):
        # Fetch http response code, headers and body for the path specified in the request.
        html_code, html_header, html_page_body = self.cached_replica_server.run(self.path)
        # Send  response code.
        self.send_response(html_code)
        # Send headers.
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(html_page_body)))

        if html_header:
            for header in html_header:
                self.send_header(header, html_header[header])
        self.end_headers()
        # Send html body
        if html_page_body:
            self.wfile.write(html_page_body)
        self.wfile.flush()
        return


# Instance of this class handles caching and responding to requests with the wikipedia data and other requests such
# as grading/beacon
class ReplicaServer:
    CACHE_FOLDER = "replica_cache/"
    ORIGIN_PORT = "8080"
    ORIGIN_PROTOCOL = "http://"

    GRADING_BEACON_PATH = "/grading/beacon"

    # Max number of pages cached in the disk.
    MAX_CACHE_SIZE = 180

    def __init__(self, port, origin):
        # Used to handle caching of web pages by using least recently used algorithm.
        self.cachedFiles = OrderedDict()
        # Store port and origin.
        self.port = port
        self.origin = origin
        # Construct the entire request URL.
        self.origin_url = self.ORIGIN_PROTOCOL + origin + ":" + self.ORIGIN_PORT
        # Create a dictionary to quickly identified cached pages.
        for ff in os.listdir(self.CACHE_FOLDER):
            if os.path.isfile(self.CACHE_FOLDER + ff):
                self.cachedFiles[ff] = True

    # Start HTTP server.
    def start_http_server(self, server_class=http.server.HTTPServer, handler_class=CustomHTTPRequestHandler):
        CustomHTTPRequestHandler.save_replica_server_instance(self)
        server_address = ('', self.port)
        httpd = server_class(server_address, handler_class)
        httpd.serve_forever()

    # Save the web page in cache by updating the dictionary and also save the contents to a file in the unicode format.
    def mark_file_in_cache(self, file_name, contents):
        Utils.save_file_after_compression(self.CACHE_FOLDER + file_name, contents)
        self.cachedFiles[file_name] = True

        # If the size of the cache is greater than capacity remove the least recently used page from the disk.
        if len(self.cachedFiles) > self.MAX_CACHE_SIZE:
            file_to_delete, _ = self.cachedFiles.popitem(last=False)
            Utils.delete_file(self.CACHE_FOLDER + file_to_delete)

    # Fetch the cached web page data in bytes from the disk and push it to the end of the dictionary to indicate it was accessed.
    def get_cached_file(self, file_name):
        self.cachedFiles.pop(file_name)
        self.cachedFiles[file_name] = True
        return Utils.get_file_contents_after_decompression(self.CACHE_FOLDER + file_name)

    # Function returns cached web page if exists or fetches the page from origin and returns the html headers, body
    # and response code.
    def run(self, path):
        # Handle /grading beacon request.
        if self.GRADING_BEACON_PATH in path:
            return 204, None, ""

        local_file_path = path.replace("/", "")

        # Return cached file.
        if local_file_path in self.cachedFiles:
            return 200, None, self.get_cached_file(local_file_path)
        try:
            # Get the page from origin as it is not yet cached
            request = urllib.request.Request(self.origin_url + path)
            request.add_header("Accept-Encoding", "utf-8")
            response = urllib.request.urlopen(request)
        except Exception as ex:
            print(path)
            print(ex)
            return 404, None, ""

        # Get response in bytes
        response_body = response.read()
        response.close()

        # Cache this web page.
        self.mark_file_in_cache(local_file_path, response_body)
        return 200, None, response_body
