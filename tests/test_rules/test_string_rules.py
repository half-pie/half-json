from half_json.diagnosis import diagnose
from half_json.rules.string_rules import CloseUnterminatedString


def test_close_unterminated_string():
    ctx = diagnose('"hello')
    assert ctx is not None
    rule = CloseUnterminatedString()
    assert rule.applies_to(ctx)
    fix = rule.apply(ctx)
    assert fix is not None
    assert fix.text == '"hello"'
