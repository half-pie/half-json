from __future__ import annotations

from half_json._helpers import insert_at
from half_json.diagnosis import ErrorType, ParseContext
from half_json.rules import FixCandidate


class CloseUnterminatedString:
    name = "close_unterminated_string"

    def applies_to(self, ctx: ParseContext) -> bool:
        return ctx.error_type == ErrorType.STRING_UNTERMINATED

    def apply(self, ctx: ParseContext) -> FixCandidate | None:
        return FixCandidate(
            text=insert_at(ctx.input, '"', len(ctx.input)),
            rule_name=self.name,
        )
