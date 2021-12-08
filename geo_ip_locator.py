import math
import urllib.request

from utils.util import Utils


class GeoIPLocator:
    API_URL = "https://api.freegeoip.app/json/"

    API_KEYS = ["cbfc9480-57a2-11ec-8ad8-833775a8b221"]

    # Constructor for the class
    def __init__(self):
        self.replica_IPs = []
        self.IP_locations = []
        self.api_key_index = 0
        # Read all the replica IP addresses from the file on the server.
        for ip in Utils.get_file_contents("./http-repls.txt").decode().split("\n"):
            ip = ip.strip()
            if ip:
                self.replica_IPs.append(ip)

        # Cache the location of replica IP addresses. We will use them later to find the closest replica to the client.
        # In case of rate limit or other errors switch to round robin method to redirect clients.
        # try:
        #     for ip in self.replica_IPs:
        #         ip_details = self.get_IP_details(ip)
        #         self.IP_locations.append((ip_details['latitude'], ip_details['longitude']))
        # except:
        #     self.IP_locations = None

        self.IP_locations = [(33.844, -84.4784), (37.5625, -122.0004), (50.1188, 8.6843), (35.6887, 139.745), (-33.8672, 151.1997), (19.0748, 72.8856)]

    # Get geological location of the IP address passed.
    def get_IP_details(self, ip_address):

        request = urllib.request.Request(self.API_URL + ip_address + "?apikey=" + self.API_KEYS[self.api_key_index])
        output = urllib.request.urlopen(request)

        # In case the API fails to get the location data then throw an exception.
        if output.status != 200:
            raise Exception("Failed to get location details for " + ip_address)
        res = {}

        for line in output.read().decode().split(","):
            if "latitude" in line:
                res["latitude"] = float(line.split(":")[1])
                pass
            if "longitude" in line:
                res["longitude"] = float(line.split(":")[1])
                pass
        output.close()

        return res

    # Get the closest replica to the IP address passed in the parameter.
    def get_closest_ip(self, source_ip):
        closest_ip_index = -1
        source_ip_details = self.get_IP_details(source_ip)
        # Get location of the source IP address
        source_ip_location = (source_ip_details['latitude'], source_ip_details['longitude'])
        lowest_dist = math.inf
        for ii, dest_ip_loc in enumerate(self.IP_locations):
            # Calculate the distance between source & destination.
            cur_dis = Utils.get_distance_between_coordinates(source_ip_location, dest_ip_loc)
            # If the distance is lower than the previous lowest distance then the current IP is closest to the source
            if lowest_dist > cur_dis:
                lowest_dist = cur_dis
                closest_ip_index = ii

        # Return the closest replica's IP address.
        return self.replica_IPs[closest_ip_index]
