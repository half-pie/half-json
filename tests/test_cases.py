# coding=utf8

import unittest

from half_json.core import JSONFixer


class TestSimpleCase(unittest.TestCase):

    def test_half_object(self):
        line = '{'
        ok, newline, _ = JSONFixer().fix(line)
        self.assertTrue(ok)
        self.assertEqual('{}', newline)

    def test_half_array(self):
        line = '['
        ok, newline, _ = JSONFixer().fix(line)
        self.assertTrue(ok)
        self.assertEqual('[]', newline)

    def test_half_string(self):
        line = '"a'
        ok, newline, _ = JSONFixer().fix(line)
        self.assertTrue(ok)
        self.assertEqual('"a"', newline)

    def test_object_miss_key(self):
        line = '{:1}'
        ok, newline, _ = JSONFixer().fix(line)
        self.assertTrue(ok)
        self.assertEqual('{"":1}', newline)

    def test_half_array_with_element(self):
        line = '[1'
        ok, newline, _ = JSONFixer().fix(line)
        self.assertTrue(ok)
        self.assertEqual('[1]', newline)

    def test_array_miss_element(self):
        line = '[,'
        ok, newline, _ = JSONFixer().fix(line)
        self.assertTrue(ok)
        self.assertEqual('[]', newline)

    def test_simple_mix(self):
        line = '[{'
        ok, newline, _ = JSONFixer().fix(line)
        self.assertTrue(ok)
        self.assertEqual('[{}]', newline)

    def test_simple_mix_A(self):
        line = '[{,'
        ok, newline, _ = JSONFixer().fix(line)
        self.assertTrue(ok)
        self.assertEqual('[{}]', newline)

    def test_miss_quote(self):
        line = '{"a'
        ok, newline, _ = JSONFixer().fix(line)
        self.assertTrue(ok)
        self.assertEqual('{"a":null}', newline)

    def test_miss_colon(self):
        line = '{"a":1,"b"'
        ok, newline, _ = JSONFixer().fix(line)
        self.assertTrue(ok)
        self.assertEqual('{"a":1,"b":null}', newline)

    def test_many_from_adhocore(self):
        line = '{"a":1,'
        ok, newline, _ = JSONFixer().fix(line)
        self.assertTrue(ok)
        self.assertEqual('{"a":1}', newline)

    def test_case_from_stackoverflow(self):
        line = '{"title": "Center "ADVANCE"", "text": "Business.English."}'
        ok, newline, _ = JSONFixer().fix(line)
        self.assertTrue(ok)
        self.assertEqual('{"title": "Center ","ADVANCE":", ","text": "Business.English."}', newline)

    def test_case_miss_key(self):
        line = '{['
        ok, newline, _ = JSONFixer().fix(line)
        self.assertTrue(ok)
        self.assertEqual('{"":[]}', newline)

    def test_object_miss_value(self):
        line = '{"V":}'
        ok, newline, _ = JSONFixer().fix(line)
        self.assertTrue(ok)
        self.assertEqual('{"V":null}', newline)

    def test_array_miss_value(self):
        line = '[,]'
        ok, newline, _ = JSONFixer().fix(line)
        self.assertTrue(ok)
        self.assertEqual('[]', newline)

    def test_array_miss_value_2(self):
        line = '[null,]'
        ok, newline, _ = JSONFixer().fix(line)
        self.assertTrue(ok)
        self.assertEqual('[null]', newline)
