# coding=utf8

import unittest

from half_json.core import clear


class TestSimpleCase(unittest.TestCase):

    def test_half_object(self):
        line = '{'
        ok, newline = clear(line)
        self.assertTrue(ok)
        self.assertEqual('{}', newline)

    def test_half_array(self):
        line = '['
        ok, newline = clear(line)
        self.assertTrue(ok)
        self.assertEqual('[]', newline)

    def test_object_miss_key(self):
        line = '{:1}'
        ok, newline = clear(line)
        self.assertTrue(ok)
        self.assertEqual('{"":1}', newline)

    def test_array_miss_element(self):
        line = '[,'
        ok, newline = clear(line)
        self.assertTrue(ok)
        self.assertEqual('[null,null]', newline)
