from __future__ import annotations

from half_json._helpers import insert_at, remove_range
from half_json.diagnosis import ErrorType, ParseContext
from half_json.rules import FixCandidate


class InsertMissingKey:
    name = "insert_missing_key"

    def applies_to(self, ctx: ParseContext) -> bool:
        return ctx.error_type == ErrorType.OBJECT_EXPECT_KEY

    def apply(self, ctx: ParseContext) -> FixCandidate | None:
        pos = ctx.pos
        nc = ctx.nextchar
        lc = ctx.lastchar
        line = ctx.input

        if nc == "":
            return FixCandidate(insert_at(line, "}", pos), self.name)
        if nc == ":":
            return FixCandidate(insert_at(line, '""', pos), self.name)
        if lc in "{," and nc == ",":
            return FixCandidate(remove_range(line, pos, pos + 1), self.name)
        if lc == "," and nc == "}":
            return FixCandidate(remove_range(line, pos - 1, pos), self.name)
        if nc in "[{":
            return FixCandidate(insert_at(line, '"":', pos), self.name)
        # Fallback: insert a quote to start a key
        return FixCandidate(insert_at(line, '"', pos), self.name)


class InsertMissingColon:
    name = "insert_missing_colon"

    def applies_to(self, ctx: ParseContext) -> bool:
        return ctx.error_type == ErrorType.OBJECT_EXPECT_COLON

    def apply(self, ctx: ParseContext) -> FixCandidate | None:
        return FixCandidate(insert_at(ctx.input, ":", ctx.pos), self.name)


class InsertMissingValue:
    name = "insert_missing_value"

    def applies_to(self, ctx: ParseContext) -> bool:
        return ctx.error_type == ErrorType.OBJECT_EXPECT_VALUE

    def apply(self, ctx: ParseContext) -> FixCandidate | None:
        pos = ctx.pos
        nc = ctx.nextchar
        lc = ctx.lastchar
        line = ctx.input

        if nc == "":
            if lc == "{":
                return FixCandidate(insert_at(line, "}", pos), self.name)
            return FixCandidate(insert_at(line, "null}", pos), self.name)
        if nc == "}":
            return FixCandidate(insert_at(line, "null", pos), self.name)
        return FixCandidate(insert_at(line, '"', pos), self.name)


class CloseOrCommaObject:
    name = "close_or_comma_object"

    def applies_to(self, ctx: ParseContext) -> bool:
        return ctx.error_type == ErrorType.OBJECT_EXPECT_COMMA

    def apply(self, ctx: ParseContext) -> FixCandidate | None:
        pos = ctx.pos
        nc = ctx.nextchar
        line = ctx.input

        if nc == "":
            return FixCandidate(insert_at(line, "}", pos), self.name)
        return FixCandidate(insert_at(line, ",", pos), self.name)


class RemoveEmptyStringKey:
    """Remove empty string key pattern like \"\"key to convert it to \"key.

    Example: {""5": "10"} -> {"5": "10"}
    """

    name = "remove_empty_string_key"

    def applies_to(self, ctx: ParseContext) -> bool:
        if ctx.error_type != ErrorType.OBJECT_EXPECT_COLON:
            return False
        # Don't apply if at end of input - could cause infinite loop
        # with close_unterminated_string rule
        if ctx.nextchar == "":
            return False
        # Check if we have "" pattern before current position
        if ctx.lastchar != '"' or ctx.pos < 2:
            return False
        # Check if the key is actually an empty string ""
        return ctx.input[ctx.pos - 2 : ctx.pos] == '""'

    def apply(self, ctx: ParseContext) -> FixCandidate | None:
        # Remove only the first quote, keeping the second to start the actual key
        return FixCandidate(
            remove_range(ctx.input, ctx.pos - 2, ctx.pos - 1), self.name
        )
