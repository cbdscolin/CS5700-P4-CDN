import unittest
import zlib
from utils.util import Utils

class MyTestCase(unittest.TestCase):

    def test_compression(self):
        original = "<html><head>Header Field</head><body>Body Field</body></html>"
        compressed = Utils.compress(original.encode())
        decompressed = Utils.decompress(compressed)
        self.assertEqual(original, decompressed.decode())


if __name__ == '__main__':
    unittest.main()
