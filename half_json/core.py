from __future__ import annotations

from typing import NamedTuple

from half_json.diagnosis import diagnose
from half_json.rules import FixCandidate, RuleRegistry
from half_json.rules.array_rules import CloseOrCommaArray, FixArrayElement
from half_json.rules.js_rules import FixJSStyleKey
from half_json.rules.object_rules import (
    CloseOrCommaObject,
    InsertMissingColon,
    InsertMissingKey,
    InsertMissingValue,
)
from half_json.rules.string_rules import CloseUnterminatedString
from half_json.rules.structural_rules import (
    PrependMissingBracket,
    WrapPartialParse,
)


class FixResult(NamedTuple):
    success: bool
    line: str
    origin: bool


def default_registry(*, js_style: bool = False) -> RuleRegistry:
    registry = RuleRegistry()
    registry.register(CloseUnterminatedString())
    if js_style:
        registry.register(FixJSStyleKey())
    registry.register(InsertMissingKey())
    registry.register(InsertMissingColon())
    registry.register(InsertMissingValue())
    registry.register(CloseOrCommaObject())
    registry.register(FixArrayElement())
    registry.register(CloseOrCommaArray())
    registry.register(PrependMissingBracket())
    registry.register(WrapPartialParse())
    return registry


class JSONFixer:
    def __init__(
        self,
        max_try: int = 20,
        max_stack: int = 3,
        *,
        js_style: bool = False,
        rules: RuleRegistry | None = None,
    ) -> None:
        self._max_try = max_try
        self._max_stack = max_stack
        self._js_style = js_style
        self._registry = rules or default_registry(js_style=js_style)

    def fix(self, line: str, *, strict: bool = True) -> FixResult:
        ctx = diagnose(line, strict=strict)
        if ctx is None:
            return FixResult(success=True, line=line, origin=True)

        # Reset stateful rules
        for rule in self._registry._rules:
            if hasattr(rule, "reset"):
                rule.reset()

        for _ in range(self._max_try):
            candidate = self._registry.find_fix(ctx)
            if candidate is None:
                break
            ctx = diagnose(candidate.text, strict=strict)
            if ctx is None:
                return FixResult(success=True, line=candidate.text, origin=False)
            line = candidate.text

        return FixResult(success=False, line=line, origin=False)
