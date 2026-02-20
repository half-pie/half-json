from __future__ import annotations

from half_json.diagnosis import ErrorType, ParseContext
from half_json.rules import FixCandidate


def _patch_latest_left(line: str) -> str:
    """Infer missing opening brackets from leading closing ones.

    e.g. '}]' -> '{' prepended, '[' prepended -> '[{' + '}]'
    """
    pairs = {"}": "{", "]": "["}
    breaks = "{["
    left = ""
    for ch in line:
        if ch in breaks:
            break
        if ch in pairs:
            left = pairs[ch] + left
    return left


def _guess_left(line: str) -> str:
    """Heuristic: guess whether to prepend '{' or '['."""
    miss_obj = line.count("}") - line.count("{")
    miss_arr = line.count("]") - line.count("[")
    if miss_obj == miss_arr == 0:
        if line[-1:] == '"' and line.count('"') == 1:
            return '"'
    elif miss_obj >= miss_arr:
        return "{"
    else:
        return "["
    return ""


class PrependMissingBracket:
    """Handle StopIteration — the scanner couldn't start parsing at all."""
    name = "prepend_missing_bracket"

    def __init__(self) -> None:
        self._last_fix: bool | None = None

    def applies_to(self, ctx: ParseContext) -> bool:
        return ctx.error_type == ErrorType.UNEXPECTED_TOKEN

    def apply(self, ctx: ParseContext) -> FixCandidate | None:
        line = ctx.input
        # Fix malformed negative decimals like "-.5"
        if line.startswith("-."):
            return FixCandidate("-0." + line[2:], self.name)

        left = _patch_latest_left(line)
        if left == "" and not self._last_fix:
            left = _guess_left(line)

        if left == "":
            return None

        result = FixCandidate(left + line, self.name)
        self._last_fix = True
        return result

    def reset(self) -> None:
        self._last_fix = None


class WrapPartialParse:
    """Handle partial parse — decoded something but leftover remains."""
    name = "wrap_partial_parse"

    def __init__(self) -> None:
        self._last_fix: bool | None = None

    def applies_to(self, ctx: ParseContext) -> bool:
        return ctx.error_type == ErrorType.PARTIAL_PARSE

    def apply(self, ctx: ParseContext) -> FixCandidate | None:
        line = ctx.input
        end = ctx.consumed_end
        remaining = line[end:].strip()
        nc = remaining[:1]

        left = _patch_latest_left(remaining)
        if left == "":
            if nc == ",":
                left = "["
            elif nc == ":" and isinstance(ctx.partial_result, str):
                left = "{"
            elif not self._last_fix:
                left = _guess_left(remaining)

        if left == "":
            return None

        result = FixCandidate(left + line[:end] + remaining, self.name)
        self._last_fix = True
        return result

    def reset(self) -> None:
        self._last_fix = None
