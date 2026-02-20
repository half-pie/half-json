from __future__ import annotations

from half_json._helpers import insert_at, remove_range
from half_json.diagnosis import ErrorType, ParseContext
from half_json.rules import FixCandidate


class FixArrayElement:
    name = "fix_array_element"

    def applies_to(self, ctx: ParseContext) -> bool:
        return ctx.error_type == ErrorType.ARRAY_EXPECT_VALUE

    def apply(self, ctx: ParseContext) -> FixCandidate | None:
        pos = ctx.pos
        nc = ctx.nextchar
        lc = ctx.lastchar
        line = ctx.input

        if nc == "," and lc == "[":
            return FixCandidate(remove_range(line, pos, pos + 1), self.name)
        if nc == ",":
            return FixCandidate(insert_at(line, "null", pos), self.name)
        if nc == "]":
            return FixCandidate(remove_range(line, pos - 1, pos), self.name)
        if nc == "":
            if lc == "[":
                return FixCandidate(insert_at(line, "]", pos), self.name)
            return FixCandidate(insert_at(line, "null]", pos), self.name)
        return FixCandidate(insert_at(line, "{", pos), self.name)


class CloseOrCommaArray:
    name = "close_or_comma_array"

    def applies_to(self, ctx: ParseContext) -> bool:
        return ctx.error_type == ErrorType.ARRAY_EXPECT_COMMA

    def apply(self, ctx: ParseContext) -> FixCandidate | None:
        pos = ctx.pos
        line = ctx.input

        if len(line) == pos:
            return FixCandidate(insert_at(line, "]", pos), self.name)
        return FixCandidate(insert_at(line, ",", pos), self.name)
