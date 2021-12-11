import os
import threading
import time
import unittest
import urllib
import socket
from urllib.error import HTTPError, URLError

from dns.active_measure import LoadMeasurer
from dns.dns_server import DNSResolver
import dns.dns_server
from dns.geo_ip_locator import GeoIPLocator
from utils.util import Utils

'''
1. Run these tests after running deployCDN & runCDN commands on cs5700cdnproject.ccs.neu.edu server.
2. Run these tests from the tests/ folder of the repo. 
3. Skip CDNTests.test_download_all_pages test as it takes longer to complete.
4. Run tests using python3 -m tests.cdn_tests command
'''


class CDNTests(unittest.TestCase):
    ORIGIN_URL = "http://127.0.0.1:20442/"

    def setUp(self):
        self.all_replica_ips = []
        for ip in Utils.get_file_contents("./../http-repls.txt").decode().split("\n"):
            ip = ip.strip()
            if ip:
                self.all_replica_ips.append(ip)

    @staticmethod
    def create_dns_request(ip):
        class DNSReq:
            def __init__(self):
                self.objs = []

            def reply(self):
                objs = self.objs

                class RE:
                    def __init__(self):
                        pass

                    def add_answer(self, obj):
                        objs.append(obj)

                return RE()

        class DNSH:
            def __init__(self):
                self.client_address = [ip]

        dns_request = DNSReq()
        dns_handler = DNSH()
        return dns_request, dns_handler

    def test_dns_response(self):
        locator = GeoIPLocator("./../http-repls.txt")

        req, hand = self.create_dns_request("99.79.40.102")
        dns.dns_server.DNSResolver(locator, "example.com").resolve(req, hand)
        self.assertEqual(str(req.objs[0].rdata), "45.33.99.146")

        req, hand = self.create_dns_request("18.231.60.86")
        dns.dns_server.DNSResolver(locator, "example.com").resolve(req, hand)
        self.assertEqual(str(req.objs[0].rdata), "45.33.99.146")

        # European Client Server has German Replica Server closest to it
        req, hand = self.create_dns_request("34.116.137.247")
        dns.dns_server.DNSResolver(locator, "example.com").resolve(req, hand)
        self.assertEqual(str(req.objs[0].rdata), "139.162.142.68")

        # Indian Client Server has Indian Replica Server closest to it
        req, hand = self.create_dns_request("34.131.44.77")
        dns.dns_server.DNSResolver(locator, "example.com").resolve(req, hand)
        self.assertEqual(str(req.objs[0].rdata), "172.105.36.32")

    def test_dns_server_running(self):
        resp = os.popen("dig @173.255.237.185 -p 40002")
        out = resp.read()
        resp.close()
        self.assertTrue(";; ANSWER SECTION:" in out)
        self.assertTrue("QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 0" in out)
        resp.close()

    def test_distance_between_two_coordinates(self):
        dis = Utils.get_distance_between_coordinates((52.2296756, 21.0122287), (52.406374, 16.9251681))
        self.assertEqual(278, int(dis))

    def test_compression(self):
        original = "<html><head>Header Field</head><body>Body Field</body></html>"
        compressed = Utils.compress(original.encode())
        decompressed = Utils.decompress(compressed)
        self.assertEqual(original, decompressed.decode())

    def test_beacon_request(self):
        locator = GeoIPLocator("./../http-repls.txt")
        self.assertEqual(len(locator.IP_locations), 6)
        self.assertEqual(len(locator.replica_IPs), 6)
        self.assertEqual(len(self.all_replica_ips), 6)

        for replica_ip in self.all_replica_ips:
            request = urllib.request.Request("http://" + replica_ip + ":40002/grading/beacon")
            request.add_header("Accept-Encoding", "utf-8")
            response = None
            try:
                response = urllib.request.urlopen(request)
            except Exception as ex:
                print(ex)
                print("replica: " + replica_ip)
                raise ex

            self.assertIsNotNone(response)
            self.assertEqual(response.code, 204)

    def test_page_fetch_works(self):
        expected_content = Utils.get_file_contents("./test_resources/Chief_Justice_of_the_United_States")
        for replica_ip in self.all_replica_ips:
            request = urllib.request.Request("http://" + replica_ip + ":40002/Chief_Justice_of_the_United_States")
            request.add_header("Accept-Encoding", "utf-8")
            response = None
            try:
                response = urllib.request.urlopen(request)
            except Exception as ex:
                print(ex)
                print("replica: " + replica_ip)
                raise ex

            actual_content = response.read()
            self.assertIsNotNone(response)
            self.assertEqual(response.code, 200)
            self.assertEqual(actual_content, expected_content)
            response.close()

    def test_invalid_page_fetch(self):
        for replica_ip in self.all_replica_ips:
            request = urllib.request.Request("http://" + replica_ip + ":40002/Invalid_Page")
            request.add_header("Accept-Encoding", "utf-8")
            try:
                response = urllib.request.urlopen(request)
                self.fail("Request should fail with 404 error")
            except HTTPError as ex:
                self.assertEqual(ex.code, 404)

    @unittest.skip("Skipping test that downloads all pages")  # Uncomment this to run this test case.
    def test_download_all_pages(self):
        all_pages_list = Utils.get_file_contents("./test_resources/pageviews.csv").decode().split("\r\n")
        for page_no, line in enumerate(all_pages_list):
            print(page_no)
            if len(line.split(",")) == 2:
                page_name, _ = line.split(",")
                for replica_ip in self.all_replica_ips:
                    request = urllib.request.Request("http://" + replica_ip + ":40002/" + page_name)
                    request.add_header("Accept-Encoding", "utf-8")
                    response = urllib.request.urlopen(request)
                    actual_content = response.read().decode()

                    self.assertIsNotNone(response)
                    self.assertEqual(response.code, 200)
                    self.assertTrue(len(actual_content) > 0)
                    self.assertTrue(actual_content.startswith("<!DOCTYPE html>"))
                    self.assertTrue(actual_content.endswith("</html>"))
                    response.close()
            else:
                print("Invalid line: ", page_no, line)

    @unittest.skip("Skipping test that expects dns and repica servers to be stopped")
    def test_dns_and_replicas_stopped(self):
        resp = os.popen("dig @173.255.237.185 -p 40002")
        out = resp.read()
        resp.close()
        self.assertTrue("connection timed out; no servers could be reached" in out)

        for replica_ip in self.all_replica_ips:
            request = urllib.request.Request("http://" + replica_ip + ":40002/Chief_Justice_of_the_United_States")
            request.add_header("Accept-Encoding", "utf-8")
            try:
                urllib.request.urlopen(request)
                self.fail("Connection should fail for the replica " + replica_ip)
            except URLError as ex:
                self.assertTrue(ex.reason.strerror, "Connection refused")

    @staticmethod
    def load_server_ip(tId, replica_ip):
        print("Running thread", tId, replica_ip)
        for i in range(990000000):
            request = urllib.request.Request("http://" + replica_ip + ":40002/")
            request.add_header("Accept-Encoding", "utf-8")

            try:
                urllib.request.urlopen(request)
            except:
                pass
        print("thread ", tId, " completed")

    def test_response_time(self):
        replica_ip = self.all_replica_ips[0]

        thread_count = 2000
        for i in range(thread_count):
            thread = threading.Thread(target=CDNTests.load_server_ip, args=(i, replica_ip))
            thread.start()
        time.sleep(6)

        # request = urllib.request.Request("http://" + replica_ip + ":40002/")
        # request.add_header("Accept-Encoding", "utf-8")
        start = time.time()
        # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # s.connect((replica_ip, 40002))
        # s.sendall('Hello, world'.encode())
        # s.close()
        try:
            urllib.request.urlopen(request)
            fail("Failed")
        except:
            pass
        end = time.time()

        print("Time taken: ", (end - start))
        time.sleep(10000)

    def test_should_check_load(self):
        locator = GeoIPLocator("./../http-repls.txt")
        load_measurer = LoadMeasurer(locator, 4)
        self.assertFalse(load_measurer.should_check_load())
        time.sleep(2)
        self.assertFalse(load_measurer.should_check_load())
        time.sleep(3)
        self.assertTrue(load_measurer.should_check_load())

    def test_dns_with_bad_replicas(self):
        locator = GeoIPLocator("./../http-repls.txt")

        req, hand = self.create_dns_request("99.79.40.102")
        dns.dns_server.DNSResolver(locator, "example.com").resolve(req, hand)
        self.assertEqual(str(req.objs[0].rdata), "45.33.99.146")

        locator.load_measurer.bad_replicas = [0, 1]

        req, hand = self.create_dns_request("99.79.40.102")
        dns.dns_server.DNSResolver(locator, "example.com").resolve(req, hand)
        self.assertEqual(str(req.objs[0].rdata), "139.162.142.68")

        locator.load_measurer.bad_replicas = [0, 1, 2, 3]

        req, hand = self.create_dns_request("99.79.40.102")
        dns.dns_server.DNSResolver(locator, "example.com").resolve(req, hand)
        self.assertEqual(str(req.objs[0].rdata), "172.105.36.32")

        locator.load_measurer.bad_replicas = [0, 1, 2, 3, 4, 5]

        req, hand = self.create_dns_request("99.79.40.102")
        dns.dns_server.DNSResolver(locator, "example.com").resolve(req, hand)
        self.assertEqual(str(req.objs[0].rdata), "45.33.99.146")

    def test_scamper(self):
        # cmd = os.popen('scamper -c "trace -d 40002 -P TCP" -i 172.105.36.32 -i 45.33.99.146')
        # out = cmd.read()

        out = Utils.get_file_contents("./../scamper_out.txt").decode()

        ip_logs = out.split("traceroute")

        z
        replica_ip_ratings_pairs = {}
        for single_ip_log in ip_logs:
            single_ip_log = single_ip_log.strip()
            if single_ip_log == "":
                continue
            ip_log_lines = single_ip_log.split("\n")
            replica_ip = ip_log_lines[0].split("to")[1].strip()
            ratings = 0
            if len(ip_log_lines) > 0:
                # last hop has star
                if "*" in ip_log_lines[len(ip_log_lines) - 1]:
                    ratings = -2
                else:
                    for single_ip_log_line in ip_log_lines:
                        if "*" in single_ip_log_line:
                            ratings = -1
                            break

            print (replica_ip, ratings)
            replica_ip_ratings_pairs[replica_ip] = ratings






        print(replica_ip_ratings_pairs)

if __name__ == '__main__':
    unittest.main()
