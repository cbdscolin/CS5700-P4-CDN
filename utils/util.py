import os

import zlib


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
        Utils.print_logs("Compression: Before = ", before_len, " After = ", after_len)
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
