# coding=utf8

import unittest

from half_json.core import JSONFixer


class TestOtherCase(unittest.TestCase):

    def test_patch_left_object(self):
        line = '}'
        ok, newline, _ = JSONFixer().fix(line)
        self.assertTrue(ok)
        self.assertEqual('{}', newline)

    def test_patch_left_array(self):
        line = ']'
        ok, newline, _ = JSONFixer().fix(line)
        self.assertTrue(ok)
        self.assertEqual('[]', newline)

    def test_patch_half_array(self):
        line = '[]]'
        ok, newline, _ = JSONFixer().fix(line)
        self.assertTrue(ok)
        self.assertEqual('[[]]', newline)

    def test_patch_half_object(self):
        line = '{}}'
        ok, newline, _ = JSONFixer().fix(line)
        self.assertTrue(ok)
        self.assertEqual('{"":{}}', newline)

    def test_patch_half_object_array(self):
        line = '{}]'
        ok, newline, _ = JSONFixer().fix(line)
        self.assertTrue(ok)
        self.assertEqual('[{}]', newline)

    def test_patch_half_array_object(self):
        line = '[]}'
        ok, newline, _ = JSONFixer().fix(line)
        self.assertTrue(ok)
        self.assertEqual('{"":[]}', newline)

    def test_patch_half_array_with_coma(self):
        line = '1, [""], -1]'
        ok, newline, _ = JSONFixer().fix(line)
        self.assertTrue(ok)
        self.assertEqual('[1, [""], -1]', newline)

    def test_patch_half_array_with_coma_v2(self):
        line = '1, 2'
        ok, newline, _ = JSONFixer().fix(line)
        self.assertTrue(ok)
        self.assertEqual('[1, 2]', newline)

    def test_patch_half_object_with_colon(self):
        line = '"a":'
        ok, newline, _ = JSONFixer().fix(line)
        self.assertTrue(ok)
        self.assertEqual('{"a":null}', newline)

    def test_patch_many_half_object(self):
        line = '{}[]{}}]'
        ok, newline, _ = JSONFixer().fix(line)
        self.assertTrue(ok)
        self.assertEqual('[{"":{},"":[],"":{}}]', newline)

    def test_patch_string(self):
        line = 'E"'
        ok, newline, _ = JSONFixer().fix(line)
        self.assertTrue(ok)
        self.assertEqual('"E"', newline)
