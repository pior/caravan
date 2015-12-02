# encoding: utf-8
import random
import unittest
import json
import zlib

from postalx.workflows.util import swf_encode_data, swf_decode_data


def make_random_string():
    return ''.join(['%x' % random.getrandbits(4000) for x in range(100)])


class Test(unittest.TestCase):

    test_payload = {'key': 'value'}
    large_payload = 'O' * 33000
    unicode_payload = {'key': u'ਉਊਏਐਓਔ'}
    too_large_payload = make_random_string()

    def test_encode_data(self):
        response = swf_encode_data(self.test_payload)
        self.assertEqual(response, b'{"key": "value"}')

    def test_encode_data_large(self):
        response = swf_encode_data(self.large_payload)
        expected = zlib.compress(json.dumps(self.large_payload))
        self.assertEqual(response, expected)

    def test_encode_data_too_large(self):
        response = swf_encode_data(self.large_payload)
        expected = zlib.compress(json.dumps(self.large_payload))
        self.assertEqual(response, expected)

    def test_decode_data(self):
        response = swf_decode_data(b'{"key": "value"}')
        self.assertEqual(response, self.test_payload)

    def test_decode_data_compressed(self):
        compressed_payload = zlib.compress(json.dumps(self.test_payload))
        response = swf_decode_data(compressed_payload)
        self.assertEqual(response, {'key': 'value'})

    def test_encode_decode(self):
        response = swf_decode_data(swf_encode_data(self.test_payload))
        self.assertEqual(response, self.test_payload)

    def test_encode_decode_large(self):
        response = swf_decode_data(swf_encode_data(self.large_payload))
        self.assertEqual(response, self.large_payload)

    def test_encode_decode_unicode(self):
        response = swf_decode_data(swf_encode_data(self.unicode_payload))
        self.assertEqual(response, self.unicode_payload)
