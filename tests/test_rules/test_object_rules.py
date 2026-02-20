import pytest

from half_json.diagnosis import diagnose
from half_json.rules.object_rules import (
    CloseOrCommaObject,
    InsertMissingColon,
    InsertMissingKey,
    InsertMissingValue,
)


class TestInsertMissingKey:
    rule = InsertMissingKey()

    def test_empty_after_brace(self):
        ctx = diagnose('{')
        fix = self.rule.apply(ctx)
        assert fix.text == '{}'

    def test_colon_without_key(self):
        ctx = diagnose('{:1}')
        fix = self.rule.apply(ctx)
        assert fix.text == '{"":1}'

    def test_trailing_comma(self):
        ctx = diagnose('{"a":1,}')
        fix = self.rule.apply(ctx)
        assert fix.text == '{"a":1}'

    def test_double_comma(self):
        ctx = diagnose('{,,')
        fix = self.rule.apply(ctx)
        assert fix.text == '{,'


class TestInsertMissingColon:
    rule = InsertMissingColon()

    def test_missing_colon(self):
        ctx = diagnose('{"a"1}')
        fix = self.rule.apply(ctx)
        assert fix.text == '{"a":1}'


class TestInsertMissingValue:
    rule = InsertMissingValue()

    def test_empty_value(self):
        ctx = diagnose('{"a":}')
        fix = self.rule.apply(ctx)
        assert fix.text == '{"a":null}'

    def test_empty_after_colon(self):
        ctx = diagnose('{"a":')
        fix = self.rule.apply(ctx)
        assert fix.text == '{"a":null}'


class TestCloseOrCommaObject:
    rule = CloseOrCommaObject()

    def test_missing_comma(self):
        ctx = diagnose('{"a":1"b":2}')
        fix = self.rule.apply(ctx)
        assert fix.text == '{"a":1,"b":2}'
