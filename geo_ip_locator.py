import math

import requests
from utils.util import Utils

class GeoIPLocator:

    API_URL = "https://api.freegeoip.app/json/"

    API_KEYS = ["cbfc9480-57a2-11ec-8ad8-833775a8b221"]

    def __init__(self):
        self.replica_IPs = []
        self.IP_locations = []
        self.api_key_index = 0
        for ip in Utils.get_file_contents("/course/cs5700f21/http-repls.txt").decode().split("\n"):
            ip = ip.strip()
            if ip:
                self.replica_IPs.append(ip)

        for ip in self.replica_IPs:
            ip_details = self.get_IP_details(ip)
            self.IP_locations.append((ip_details['latitude'], ip_details['longitude']))

    def get_IP_details(self, ip_address):
        output = requests.get(self.API_URL + ip_address + "?apikey=" + self.API_KEYS[self.api_key_index])
        return output.json()

    def get_closest_ip(self, source_ip):
        source_ip_details = self.get_IP_details(source_ip)
        source_ip_location = (source_ip_details['latitude'], source_ip_details['longitude'])
        lowest_dist = math.inf
        closest_ip = 0
        for ii, dest_ip_loc in enumerate(self.IP_locations):
            cur_dis = Utils.get_distance_between_coordinates(source_ip_location, dest_ip_loc)
            if lowest_dist > cur_dis:
                lowest_dist = cur_dis
                closest_ip = ii

        return self.replica_IPs[closest_ip]


