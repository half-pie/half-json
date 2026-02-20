from __future__ import annotations

from half_json._helpers import insert_at, remove_range
from half_json.diagnosis import ErrorType, ParseContext
from half_json.rules import FixCandidate


class FixJSStyleKey:
    """Convert JS-style bare or single-quoted keys to double-quoted."""

    name = "fix_js_style_key"

    def applies_to(self, ctx: ParseContext) -> bool:
        return ctx.error_type == ErrorType.OBJECT_EXPECT_KEY

    def apply(self, ctx: ParseContext) -> FixCandidate | None:
        pos = ctx.pos
        nc = ctx.nextchar
        line = ctx.input
        lastline = line[:pos]
        nextline = line[pos:]

        # Single-quoted key: {'abc':1}
        if nc == "'":
            nextline = remove_range(nextline, 0, 1)
            idx = nextline.find(":")
            if idx != -1 and idx != 0 and nextline[idx - 1] == "'":
                nextline = remove_range(nextline, idx - 1, idx)
            return FixCandidate(lastline + nextline, self.name)

        # Bare key: {abc:1}
        idx = nextline.find(":")
        if idx != -1:
            text = lastline + insert_at(nextline, '"', idx)
            text = insert_at(text, '"', pos)
            return FixCandidate(text, self.name)

        return None
