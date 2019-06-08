# coding=utf8

import unittest

from half_json.core import JSONFixer


class TestJSCase(unittest.TestCase):

    def test_bare_key(self):
        line = '{a:1, b:{c:3}}'
        ok, newline, _ = JSONFixer(js_style=True).fix(line)
        self.assertTrue(ok)
        self.assertEqual('{"a":1, "b":{"c":3}}', newline)
