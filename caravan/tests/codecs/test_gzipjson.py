# encoding: utf-8
import unittest

from caravan.codecs import gzipjson

from nose_parameterized import parameterized


class Test(unittest.TestCase):

    @parameterized.expand([
        ('None', None, 'null'),
        ('String', 'Yo', '"Yo"'),
        ('Dict', {'k': 'v'}, '{"k": "v"}'),
        ('VeryLong', 'x' * 32001,
         b'eJztwSEBAAAAAqAvrnS+yRdACgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHA'
         b'ZPkWcIw=='),
        ('Unicode', u'😿😱∑', '"\\ud83d\\ude3f\\ud83d\\ude31\\u2211"'),
        ('VeryLongUnicode', u'😿' * 8001,
         b'eJztxjERACAIAMAuVGAxDCPawP5SwAa//H3U7ZU97jzu7u7u7u7u7u7u7u7u7u7u7u7'
         b'u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u'
         b'7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7'
         b'u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u'
         b'7u7u7u7u7u7u7u7u7u7u7u6/xwMOT8Lp'),
        ])
    def test_dumps(self, name, data, encoded):
        self.assertEqual(gzipjson.dumps(data), encoded)

        self.assertEqual(gzipjson.loads(encoded), data,
                         msg='Failed to decode data')

        self.assertEqual(gzipjson.loads(gzipjson.dumps(data)), data,
                         msg='Failed to encode/decode data')
