"""End-to-end tests migrated from the original unittest suite."""

import random
import sys

import pytest

from half_json.core import JSONFixer

# --- test_cases.py equivalents ---


@pytest.mark.parametrize(
    "input_line, expected",
    [
        ("{", "{}"),
        ("[", "[]"),
        ('"a', '"a"'),
        ("{:1}", '{"":1}'),
        ("[1", "[1]"),
        ("[,", "[]"),
        ("[{", "[{}]"),
        ("[{,", "[{}]"),
        ('{"a', '{"a":null}'),
        ('{"a":1,"b"', '{"a":1,"b":null}'),
        pytest.param(
            '{"a":1,',
            '{"a":1}',
            marks=pytest.mark.skipif(
                sys.version_info >= (3, 13), reason="Python 3.13+ accepts trailing commas in JSON"
            ),
        ),
        ("{[", '{"":[]}'),
        ('{"V":}', '{"V":null}'),
        ("[,]", "[]"),
        pytest.param(
            "[null,]",
            "[null]",
            marks=pytest.mark.skipif(
                sys.version_info >= (3, 13), reason="Python 3.13+ accepts trailing commas in JSON"
            ),
        ),
    ],
)
def test_basic_fixes(input_line, expected):
    ok, line, _ = JSONFixer().fix(input_line)
    assert ok
    assert line == expected


def test_case_from_stackoverflow():
    line = '{"title": "Center "ADVANCE"", "text": "Business.English."}'
    ok, newline, _ = JSONFixer().fix(line)
    assert ok
    assert newline == '{"title": "Center ","ADVANCE":", ","text": "Business.English."}'


def test_unstrict_ok():
    line = '{"hello": "wor\nld"}'
    ok, _, _ = JSONFixer().fix(line)
    assert not ok
    ok, newline, _ = JSONFixer().fix(line, strict=False)
    assert ok
    assert newline == line


def test_unstrict_fix():
    line = '{"hello": "wor\nld"'
    ok, _, _ = JSONFixer().fix(line)
    assert not ok
    ok, newline, _ = JSONFixer().fix(line, strict=False)
    assert ok
    assert newline == '{"hello": "wor\nld"}'


# --- test_stop.py equivalents ---


@pytest.mark.parametrize(
    "input_line, expected",
    [
        ("}", "{}"),
        ("]", "[]"),
        ("[]]", "[[]]"),
        ("{}}", '{"":{}}'),
        ("{}]", "[{}]"),
        ("[]}", '{"":[]}'),
        ('1, [""], -1]', '[1, [""], -1]'),
        ("1, 2", "[1, 2]"),
        ('"a":', '{"a":null}'),
        ("{}[]{}}]", '[{"":{},"":[],"":{}}]'),
        ('E"', '"E"'),
    ],
)
def test_structural_fixes(input_line, expected):
    ok, line, _ = JSONFixer().fix(input_line)
    assert ok
    assert line == expected


# --- test_js.py equivalents ---


def test_js_bare_key():
    ok, line, _ = JSONFixer(js_style=True).fix("{a:1, b:{c:3}}")
    assert ok
    assert line == '{"a":1, "b":{"c":3}}'


def test_js_single_quoted_key():
    line = "{'a':1, 'b':{'c':[]}}"
    ok, newline, _ = JSONFixer(js_style=True).fix(line)
    assert ok
    assert newline == '{"a":1, "b":{"c":[]}}'


# --- test_miss.py equivalents ---

LARGE_JSON = '[{"_id":"5cf12ecfb7af6c84da64571b","index":0,"guid":"c2aedc2a-7303-42e2-b5a8-d58afca2149f","isActive":false,"balance":"$1,322.22","name":{"first":"Gardner","last":"Ford"},"company":"IMAGINART","tags":["irure","culpa"],"friends":[{"id":0,"name":"Malinda Estes"}]}]'


def test_random_tail_truncation():
    fixer = JSONFixer()
    random.seed(12345)
    for _ in range(200):
        idx = random.randint(1, len(LARGE_JSON))
        result = fixer.fix(LARGE_JSON[:idx])
        assert result.success


def test_random_head_truncation():
    fixer = JSONFixer(200)
    random.seed(12345)
    for _ in range(200):
        idx = random.randint(1, len(LARGE_JSON) - 1)
        result = fixer.fix(LARGE_JSON[idx:])
        assert result.success
