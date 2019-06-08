# coding=utf8

import unittest

from half_json.core import JSONFixer


class TestJSCase(unittest.TestCase):

    def test_bare_key(self):
        line = '{a:1, b:{c:3}}'
        ok, newline, _ = JSONFixer(js_style=True).fix(line)
        self.assertTrue(ok)
        self.assertEqual('{"a":1, "b":{"c":3}}', newline)

    def test_litte_key(self):
        line = "{'a':1, 'b':{'c':[]}}"
        ok, newline, _ = JSONFixer(js_style=True).fix(line)
        self.assertTrue(ok)
        self.assertEqual('{"a":1, "b":{"c":[]}}', newline)

        for i in range(1, len(line)):
            ok, newline, _ = JSONFixer(js_style=True).fix(line[:i])
            self.assertTrue(ok)

    def test_litte_key_half(self):
        line = "{'a':}"
        ok, newline, _ = JSONFixer(js_style=True).fix(line)
        self.assertTrue(ok)
        self.assertEqual('{"a":null}', newline)
