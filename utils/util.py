import os

import zlib
from math import sin, cos, sqrt, atan2, radians


class Utils:

    @staticmethod
    def print_logs(*log_lines):
        res = ""
        for log in log_lines:
            res += str(log)
        print(res)

    @staticmethod
    def save_file(filename, contents):
        f = open(filename, "wb")
        f.write(contents)
        f.close()

    @staticmethod
    def save_file_after_compression(filename, contents_bytes):
        before_len = len(contents_bytes)
        f = open(filename, "wb")
        compressed_contents_bytes = Utils.compress(contents_bytes)
        after_len = len(compressed_contents_bytes)
        f.write(compressed_contents_bytes)
        f.close()

    @staticmethod
    def get_file_contents(filename):
        f = open(filename, "rb")
        contents = f.read()
        f.close()
        return contents

    @staticmethod
    def get_file_contents_after_decompression(filename):
        f = open(filename, "rb")
        compressed_contents_bytes = f.read()
        f.close()
        decompressed_contents = Utils.decompress(compressed_contents_bytes)
        return decompressed_contents

    @staticmethod
    def delete_file(filename):
        os.remove(filename)

    @staticmethod
    def compress(original_contents_bytes):
        compressed_contents_bytes = zlib.compress(original_contents_bytes, zlib.Z_BEST_COMPRESSION)
        return compressed_contents_bytes

    @staticmethod
    def decompress(compressed_contents_bytes):
        decompressed_contents_bytes = zlib.decompress(compressed_contents_bytes)
        return decompressed_contents_bytes

    '''
    Reference: https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude
    '''
    @staticmethod
    def get_distance_between_coordinates(ord1, ord2):
        lat1 = radians(ord1[0])
        lon1 = radians(ord1[1])
        lat2 = radians(ord2[0])
        lon2 = radians(ord2[1])

        if lat1 is None or lat2 is None or lon1 is None or lon2 is None:
            raise Exception("Invalid locations used to calculate distance")

        long_diff = lon2 - lon1
        latt_diff = lat2 - lat1

        a = (sin(latt_diff / 2) ** 2) + cos(lat1) * cos(lat2) * sin(long_diff / 2)**2
        distance = 2 * atan2(sqrt(a), sqrt(1 - a)) * 6373.0

        return abs(distance)
