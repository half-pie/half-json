# coding=utf8
import json
from typing import Any, List, NamedTuple, Optional, Tuple

from half_json.json_util import decode_line, errors


class FixResult(NamedTuple):
    success: bool
    line: str
    origin: bool


class JSONFixer:
    def __init__(self, max_try: int = 20, max_stack: int = 3, *, js_style: bool = False) -> None:
        self._max_try = max_try
        self._max_stack = max_stack
        self._js_style = js_style
        self.last_fix: Optional[bool] = None
        self.fix_stack: List[str] = []

    def fix(self, line: str, *, strict: bool = True) -> FixResult:
        try:
            json.loads(line, strict=strict)
            return FixResult(success=True, line=line, origin=True)
        except Exception:
            pass

        ok, new_line = self.fixwithtry(line, strict=strict)
        return FixResult(success=ok, line=new_line, origin=False)

    def fixwithtry(self, line: str, *, strict: bool = True) -> Tuple[bool, str]:
        if self._max_try <= 0:
            return False, line

        self.fix_stack = []
        self.last_fix = None

        ok = False
        for _ in range(self._max_try):
            ok, new_line = self.patch_line(line, strict=strict)
            if ok:
                return ok, new_line

            self.last_fix = line != new_line
            if self.last_fix:
                self.fix_stack.insert(0, new_line)
                self.fix_stack = self.fix_stack[: self._max_stack]

            line = new_line
        return ok, line

    def patch_line(self, line: str, *, strict: bool = True) -> Tuple[bool, str]:
        result = decode_line(line, strict=strict)
        if result.success:
            return True, line

        if isinstance(result.exception, ValueError):
            return self.patch_value_error(line, result.err_info)

        if isinstance(result.exception, StopIteration):
            return self.patch_stop_iteration(line)

        if result.exception is None:
            return self.patch_half_parse(line, result.err_info)

        return False, line

    def patch_value_error(self, line: str, err_info: Any) -> Tuple[bool, str]:
        if err_info["error"] is None:
            return False, line

        error = err_info["error"]
        pos = err_info["pos"]
        nextchar = line[pos : pos + 1]
        lastchar = line[pos - 1 : pos]
        nextline = line[pos:]
        lastline = line[:pos]

        if error == errors.StringUnterminatedString:
            return False, insert_line(line, '"', len(line))
        if error == errors.ObjectExceptKey:
            if nextchar == "":
                return False, insert_line(line, "}", pos)
            if nextchar == ":":
                return False, insert_line(line, '""', pos)
            if lastchar in "{," and nextchar == ",":
                return False, remove_line(line, pos, pos + 1)
            if lastchar == "," and nextchar == "}":
                return False, remove_line(line, pos - 1, pos)
            if nextchar in "[{":
                return False, insert_line(line, '"":', pos)
            if self._js_style:
                # find 'abc'
                if nextchar == "'":
                    nextline = remove_line(nextline, 0, 1)
                    idx = nextline.find(":")
                    if idx != -1 and idx != 0 and nextline[idx - 1] == "'":
                        nextline = remove_line(nextline, idx - 1, idx)

                    return False, lastline + nextline
                # abc:1 --> "aabc":1
                idx = nextline.find(":")
                if idx != -1:
                    line = lastline + insert_line(nextline, '"', idx)
                    return False, insert_line(line, '"', pos)
            # TODO process more case "
            return False, insert_line(line, '"', pos)
        if error == errors.ObjectExceptColon:
            return False, insert_line(line, ":", pos)
        if error == errors.ObjectExceptObject:
            if nextchar == "":
                if lastchar == "{":
                    return False, insert_line(line, "}", pos)
                return False, insert_line(line, "null}", pos)
            if nextchar == "}":
                return False, insert_line(line, "null", pos)
            # TODO guess more
            return False, insert_line(line, '"', pos)
        if error == errors.ObjectExceptComma:
            if nextchar == "":
                return False, insert_line(line, "}", pos)
            return False, insert_line(line, ",", pos)
        if error == errors.ArrayExceptObject:
            if nextchar == "," and lastchar == "[":
                return False, remove_line(line, pos, pos + 1)
            if nextchar == ",":
                return False, insert_line(line, "null", pos)
            if nextchar == "]":
                return False, remove_line(line, pos - 1, pos)
            if nextchar == "":
                if lastchar == "[":
                    return False, insert_line(line, "]", pos)
                return False, insert_line(line, "null]", pos)
            # TODO guess more?
            return False, insert_line(line, "{", pos)
        if error == errors.ArrayExceptComma:
            if len(line) == pos:
                return False, insert_line(line, "]", pos)
            return False, insert_line(line, ",", pos)
        # TODO unknonwn
        return False, line

    def patch_stop_iteration(self, line: str) -> Tuple[bool, str]:
        # TODO clean
        # TODO fix
        # 1. }]
        # 2. ]}
        # 3. constans
        # 4. -
        # 先 patch 完 {[]}
        # TODO: process number
        if line.startswith("-."):
            new_line = "-0." + line[2:]
            return False, new_line
        # patch
        left = patch_lastest_left_object_and_array(line)
        if left == "":
            if not self.last_fix:
                left = patch_guess_left(line)

        new_line = left + line
        return False, new_line

    def patch_half_parse(self, line: str, err_info: Any) -> Tuple[bool, str]:
        obj, end = err_info
        nextline = line[end:].strip()
        nextchar = nextline[:1]
        left = patch_lastest_left_object_and_array(nextline)
        # ??
        if left == "":
            if nextchar == ",":
                left = "["
            elif nextchar == ":" and isinstance(obj, str):
                left = "{"
            else:
                if not self.last_fix:
                    left = patch_guess_left(nextline)

        new_line = left + line[:end] + nextline
        return False, new_line


# TODO better name
def patch_lastest_left_object_and_array(line: str) -> str:
    # '}]{[' --> '[{}]{['
    pairs = {"}": "{", "]": "["}
    breaks = "{["
    left = ""
    for char in line:
        if char in breaks:
            break
        if char in pairs:
            left = pairs[char] + left

    return left


# TODO better name
# TODO 改成 lastest
# TODO {}}]]]] --> { not [
def patch_guess_left(line: str) -> str:
    miss_object = line.count("}") - line.count("{")
    miss_array = line.count("]") - line.count("[")
    if miss_object == miss_array == 0:
        if line[-1:] == '"' and line.count('"') == 1:
            return '"'
    elif miss_object >= miss_array:
        return "{"
    else:
        return "["
    return ""


def insert_line(line: str, value: str, pos: int) -> str:
    return line[:pos] + value + line[pos:]


def remove_line(line: str, start: int, end: int) -> str:
    return line[:start] + line[end:]
