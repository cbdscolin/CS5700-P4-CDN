import os
import unittest
from utils.util import Utils
from geo_ip_locator import GeoIPLocator


class MyTestCase(unittest.TestCase):
    ORIGIN_URL = "http://127.0.0.1:20442/"

    def test_compression(self):
        original = "<html><head>Header Field</head><body>Body Field</body></html>"
        compressed = Utils.compress(original.encode())
        decompressed = Utils.decompress(compressed)
        self.assertEqual(original, decompressed.decode())

    @unittest.skip("Skipped")
    def test_download_all(self):
        all_pages_list = Utils.get_file_contents("pageviews.csv").decode().split("\r\n")
        prg = os.popen("python3 httpserver -p 20442 -o cs5700cdnorigin.ccs.neu.edu")

        for line in all_pages_list:
            print(line)
            if len(line.split(",")) == 2:
                page_name, _ = line.split(",")
                os.system("wget -qO- " + self.ORIGIN_URL + page_name + " &> /dev/null")

        prg.close()

    def test_get_IP(self):
        locator = GeoIPLocator()
        self.assertEqual(locator.get_closest_ip("99.79.40.102"), "45.33.99.146")
        self.assertEqual(locator.get_closest_ip("18.231.60.86"), "45.33.99.146")

    def test_distance_calc(self):
        dis = Utils.get_distance_between_coordinates((52.2296756, 21.0122287), (52.406374, 16.9251681))
        self.assertEqual(278, int(dis))

if __name__ == '__main__':
    unittest.main()
