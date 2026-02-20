from __future__ import annotations


def insert_at(text: str, value: str, pos: int) -> str:
    return text[:pos] + value + text[pos:]


def remove_range(text: str, start: int, end: int) -> str:
    return text[:start] + text[end:]


def build_bracket_stack(text: str, end: int | None = None) -> tuple[str, ...]:
    """Return unmatched opening brackets up to position `end`."""
    if end is None:
        end = len(text)
    stack: list[str] = []
    in_string = False
    escape = False
    for i in range(min(end, len(text))):
        ch = text[i]
        if escape:
            escape = False
            continue
        if ch == '\\' and in_string:
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch in ('{', '['):
            stack.append(ch)
        elif ch == '}' and stack and stack[-1] == '{':
            stack.pop()
        elif ch == ']' and stack and stack[-1] == '[':
            stack.pop()
    return tuple(stack)
