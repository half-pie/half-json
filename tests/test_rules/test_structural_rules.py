from half_json.diagnosis import diagnose
from half_json.rules.structural_rules import PrependMissingBracket, WrapPartialParse


class TestPrependMissingBracket:
    def test_closing_brace(self):
        rule = PrependMissingBracket()
        ctx = diagnose("}")
        fix = rule.apply(ctx)
        assert fix.text == "{}"

    def test_closing_bracket(self):
        rule = PrependMissingBracket()
        ctx = diagnose("]")
        fix = rule.apply(ctx)
        assert fix.text == "[]"

    def test_negative_decimal(self):
        rule = PrependMissingBracket()
        ctx = diagnose("-.5")
        fix = rule.apply(ctx)
        assert fix.text == "-0.5"


class TestWrapPartialParse:
    def test_partial_with_bracket(self):
        rule = WrapPartialParse()
        ctx = diagnose("{}]")
        fix = rule.apply(ctx)
        assert fix.text == "[{}]"

    def test_partial_with_comma(self):
        rule = WrapPartialParse()
        ctx = diagnose("1, 2")
        fix = rule.apply(ctx)
        assert fix.text == "[1, 2"
