from __future__ import annotations

import json
import json.decoder
from dataclasses import dataclass
from enum import Enum, auto
from json.decoder import JSONDecoder, py_scanstring  # type: ignore[attr-defined]
from json.scanner import py_make_scanner  # type: ignore[attr-defined]
from typing import Any


class ErrorType(Enum):
    STRING_UNTERMINATED = auto()
    STRING_INVALID_ESCAPE = auto()
    STRING_INVALID_CONTROL = auto()
    STRING_INVALID_UXXXX = auto()
    OBJECT_EXPECT_KEY = auto()
    OBJECT_EXPECT_COLON = auto()
    OBJECT_EXPECT_VALUE = auto()
    OBJECT_EXPECT_COMMA = auto()
    ARRAY_EXPECT_VALUE = auto()
    ARRAY_EXPECT_COMMA = auto()
    UNEXPECTED_TOKEN = auto()
    PARTIAL_PARSE = auto()
    EMPTY_INPUT = auto()


# Maps (parser_name, message_substring) -> ErrorType
_ERROR_MAP: list[tuple[str, str, ErrorType]] = [
    ("py_scanstring", "Unterminated string starting at", ErrorType.STRING_UNTERMINATED),
    ("py_scanstring", "Invalid \\uXXXX escape", ErrorType.STRING_INVALID_UXXXX),
    ("py_scanstring", "Invalid \\escape", ErrorType.STRING_INVALID_ESCAPE),
    ("py_scanstring", "Invalid control character", ErrorType.STRING_INVALID_CONTROL),
    (
        "JSONObject",
        "Expecting property name enclosed in double quotes",
        ErrorType.OBJECT_EXPECT_KEY,
    ),
    ("JSONObject", "Expecting ':' delimiter", ErrorType.OBJECT_EXPECT_COLON),
    ("JSONObject", "Expecting value", ErrorType.OBJECT_EXPECT_VALUE),
    ("JSONObject", "Expecting ',' delimiter", ErrorType.OBJECT_EXPECT_COMMA),
    ("JSONArray", "Expecting value", ErrorType.ARRAY_EXPECT_VALUE),
    ("JSONArray", "Expecting ',' delimiter", ErrorType.ARRAY_EXPECT_COMMA),
]


@dataclass(frozen=True)
class ParseContext:
    """All context a fix rule needs."""

    input: str
    error_type: ErrorType
    pos: int
    message: str
    bracket_stack: tuple[str, ...]
    nextchar: str
    lastchar: str
    partial_result: Any = None
    consumed_end: int = 0


def _record_parser_name(parser: Any) -> Any:
    """Decorator that attaches parser name to exceptions."""

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return parser(*args, **kwargs)
        except Exception as e:
            if "parser" not in e.__dict__:
                e.__dict__["parser"] = parser.__name__
            raise

    wrapper.__name__ = parser.__name__
    return wrapper


def _make_decoder(*, strict: bool = True) -> JSONDecoder:
    """Create a JSONDecoder with parser-name tracking.

    Note: json.decoder.scanstring must be patched at module level because
    JSONObject references it from module scope — no way to inject per-decoder.
    """
    decoder = JSONDecoder(strict=strict)
    decoder.parse_string = _record_parser_name(py_scanstring)  # type: ignore[attr-defined]
    decoder.parse_object = _record_parser_name(decoder.parse_object)  # type: ignore[attr-defined]
    decoder.parse_array = _record_parser_name(decoder.parse_array)  # type: ignore[attr-defined]
    decoder.scan_once = py_make_scanner(decoder)  # type: ignore[attr-defined]
    return decoder


# Patch json.decoder.scanstring once so JSONObject uses our tracked version.
# This is unavoidable: JSONObject hard-references the module-level scanstring.
json.decoder.scanstring = _record_parser_name(py_scanstring)  # type: ignore[attr-defined]

_decoder_strict = _make_decoder(strict=True)
_decoder_unstrict = _make_decoder(strict=False)


def _classify_error(parser: str, message: str) -> ErrorType | None:
    for p, msg_sub, etype in _ERROR_MAP:
        if parser == p and msg_sub in message:
            return etype
    return None


def diagnose(text: str, *, strict: bool = True) -> ParseContext | None:
    """Parse *text* and return a ParseContext describing the failure, or None if valid."""
    from half_json._helpers import build_bracket_stack

    if not text.strip():
        return ParseContext(
            input=text,
            error_type=ErrorType.EMPTY_INPUT,
            pos=0,
            message="empty input",
            bracket_stack=(),
            nextchar="",
            lastchar="",
        )

    decoder = _decoder_strict if strict else _decoder_unstrict
    try:
        obj, end = decoder.scan_once(text, 0)  # type: ignore[attr-defined]
        if end == len(text):
            return None  # valid JSON
        # Partial parse — decoded something but there's leftover
        remaining = text[end:].strip()
        return ParseContext(
            input=text,
            error_type=ErrorType.PARTIAL_PARSE,
            pos=end,
            message="partial parse",
            bracket_stack=build_bracket_stack(text, end),
            nextchar=remaining[:1],
            lastchar=text[end - 1 : end],
            partial_result=obj,
            consumed_end=end,
        )
    except StopIteration:
        return ParseContext(
            input=text,
            error_type=ErrorType.UNEXPECTED_TOKEN,
            pos=0,
            message="unexpected token",
            bracket_stack=build_bracket_stack(text),
            nextchar=text[:1],
            lastchar="",
        )
    except ValueError as e:
        parser = e.__dict__.get("parser", "")
        etype = _classify_error(parser, e.msg)  # type: ignore[attr-defined]
        if etype is None:
            return None  # unknown error, treat as unfixable
        pos = e.pos  # type: ignore[attr-defined]
        return ParseContext(
            input=text,
            error_type=etype,
            pos=pos,
            message=e.msg,  # type: ignore[attr-defined]
            bracket_stack=build_bracket_stack(text, pos),
            nextchar=text[pos : pos + 1],
            lastchar=text[pos - 1 : pos],
        )
