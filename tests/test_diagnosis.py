import pytest

from half_json.diagnosis import ErrorType, diagnose


@pytest.mark.parametrize("text, expected_type", [
    ('{"a"', ErrorType.OBJECT_EXPECT_COLON),
    ('"hello', ErrorType.STRING_UNTERMINATED),
    ('{:1}', ErrorType.OBJECT_EXPECT_KEY),
    ('{,}', ErrorType.OBJECT_EXPECT_KEY),
    ('{"a"1}', ErrorType.OBJECT_EXPECT_COLON),
    ('{"a":}', ErrorType.OBJECT_EXPECT_VALUE),
    ('{"a":1"b":2}', ErrorType.OBJECT_EXPECT_COMMA),
    ('[,]', ErrorType.ARRAY_EXPECT_VALUE),
    ('[1 2]', ErrorType.ARRAY_EXPECT_COMMA),
    ('}', ErrorType.UNEXPECTED_TOKEN),
    (']', ErrorType.UNEXPECTED_TOKEN),
    ('', ErrorType.EMPTY_INPUT),
    ('  ', ErrorType.EMPTY_INPUT),
])
def test_error_classification(text, expected_type):
    ctx = diagnose(text)
    assert ctx is not None
    assert ctx.error_type == expected_type


@pytest.mark.parametrize("text", [
    '{"a": 1}',
    '[1, 2, 3]',
    '"hello"',
    'null',
    'true',
    '42',
])
def test_valid_json_returns_none(text):
    assert diagnose(text) is None


def test_partial_parse():
    ctx = diagnose('{}]')
    assert ctx is not None
    assert ctx.error_type == ErrorType.PARTIAL_PARSE
    assert ctx.consumed_end == 2


def test_unstrict_control_char():
    text = '{"a": "wor\nld"}'
    assert diagnose(text, strict=True) is not None
    assert diagnose(text, strict=False) is None
