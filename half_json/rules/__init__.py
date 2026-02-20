from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from half_json.diagnosis import ParseContext


@dataclass(frozen=True)
class FixCandidate:
    text: str
    rule_name: str


@runtime_checkable
class FixRule(Protocol):
    @property
    def name(self) -> str: ...
    def applies_to(self, ctx: ParseContext) -> bool: ...
    def apply(self, ctx: ParseContext) -> FixCandidate | None: ...


class RuleRegistry:
    def __init__(self) -> None:
        self._rules: list[FixRule] = []

    def register(self, rule: FixRule) -> None:
        self._rules.append(rule)

    def unregister(self, name: str) -> None:
        self._rules = [r for r in self._rules if r.name != name]

    def find_fix(self, ctx: ParseContext) -> FixCandidate | None:
        for rule in self._rules:
            if rule.applies_to(ctx):
                candidate = rule.apply(ctx)
                if candidate is not None:
                    return candidate
        return None
