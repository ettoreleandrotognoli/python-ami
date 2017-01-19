# -*- encoding: utf-8 -*-

import unittest
from asterisk import ami


class AMIClientEncodingTest(unittest.TestCase):
    def test_decode_utf8(self):
        client = ami.AMIClient(encoding='utf-8')
        encoded = b'\xc3\x82\xc3\xa8\xc3\xb2\xc3\xa0\xc3\xab\xc3\xa8\xc3\xa9 \xc3\x8a\xc3\xa0\xc3\xab\xc3\xa8\xc3\xad\xc3\xa8\xc3\xad'
        expected = u'Âèòàëèé Êàëèíèí'
        decoded = client._decode_pack(encoded)
        self.assertEqual(expected, decoded)

    def test_decode_latin1(self):
        client = ami.AMIClient(encoding='latin-1')
        encoded = b'\xc2\xe8\xf2\xe0\xeb\xe8\xe9 \xca\xe0\xeb\xe8\xed\xe8\xed'
        expected = u'Âèòàëèé Êàëèíèí'
        decoded = client._decode_pack(encoded)
        self.assertEqual(expected, decoded)
