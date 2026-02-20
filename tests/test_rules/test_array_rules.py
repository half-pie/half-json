import sys

import pytest

from half_json.diagnosis import diagnose
from half_json.rules.array_rules import CloseOrCommaArray, FixArrayElement


class TestFixArrayElement:
    rule = FixArrayElement()

    def test_leading_comma(self):
        ctx = diagnose("[,")
        fix = self.rule.apply(ctx)
        assert fix.text == "["

    @pytest.mark.skipif(
        sys.version_info >= (3, 13), reason="Python 3.13+ accepts trailing commas in JSON"
    )
    def test_trailing_comma(self):
        ctx = diagnose("[null,]")
        fix = self.rule.apply(ctx)
        assert fix.text == "[null]"

    def test_empty_array_body(self):
        ctx = diagnose("[")
        fix = self.rule.apply(ctx)
        assert fix.text == "[]"


class TestCloseOrCommaArray:
    rule = CloseOrCommaArray()

    def test_missing_close(self):
        ctx = diagnose("[1 2]")
        fix = self.rule.apply(ctx)
        assert fix.text == "[1 ,2]"
