# coding=utf8
import json
from collections import namedtuple

from half_json.json_util import decode_line
from half_json.json_util import errors


FixResult = namedtuple('FixResult', ['success', 'line', 'origin'])


class JSONFixer(object):

    def __init__(self, max_try=20, max_stack=3):
        self._max_try = max_try
        self._max_stack = max_stack

    def fix(self, line):
        try:
            json.loads(line)
            return FixResult(success=True, line=line, origin=True)
        except Exception:
            pass

        ok, new_line = self.fixwithtry(line)
        return FixResult(success=ok, line=new_line, origin=False)

    def fixwithtry(self, line):
        if self._max_try <= 0:
            return False, line

        # record
        self.fix_stack = []
        for i in range(self._max_try):
            self.fix_stack.append(line)

            ok, line = self.patch_line(line)
            if ok:
                break

        return ok, line

    def patch_line(self, line):
        result = decode_line(line)
        if result.success:
            return True, line

        if isinstance(result.exception, ValueError):
            return self.patch_value_error(line, result.err_info)

        if isinstance(result.exception, StopIteration):
            return self.patch_stop_iteration(line)

        if result.exception is None:
            return self.patch_half_parse(line, result.err_info)

        return False, line

    def patch_value_error(self, line, err_info):
        if err_info["error"] is None:
            return False, line

        error = err_info["error"]
        pos = err_info["pos"]
        nextchar = line[pos: pos + 1]
        lastchar = line[pos - 1: pos]
        # TODO
        # nextline = line[pos:]
        # lastline = line[:pos]

        # 02
        if error == errors.StringUnterminatedString:
            # TODO resolve "abc --> "abc"
            return False, insert_line(line, "\"", len(line))
        # 06
        if error == errors.ObjectExceptKey:
            # quick
            if nextchar == "":
                return False, insert_line(line, "}", pos)
            # miss key
            if nextchar == ":":
                return False, insert_line(line, "\"\"", pos)
            # miss a pair
            if nextchar == "," and lastchar in "{,":
                return False, remove_line(line, pos, pos + 1)
            # fix-error
            if lastchar == "," and nextchar == "}":
                return False, remove_line(line, pos - 1, pos)
            # {[ or {"a":1,[ --> "":[
            if nextchar in "[{":
                return False, insert_line(line, "\"\":", pos)
            # dosomething
            # if lastchar == "{":
            return False, insert_line(line, "\"", pos)
        # 07
        if error == errors.ObjectExceptColon:
            return False, insert_line(line, ":", pos)
        # 08
        if error == errors.ObjectExceptObject:
            # 08.1
            if nextchar == "":
                # quick
                if lastchar == "{":
                    return False, insert_line(line, "}", pos)
                return False, insert_line(line, "null}", pos)
            # :} --> :null}
            if nextchar == "}":
                return False, insert_line(line, "null", pos)
            # 08.2
            return False, insert_line(line, "\"", pos)
        # 09
        if error == errors.ObjectExceptComma:
            if nextchar == "":
                return False, insert_line(line, "}", pos)
            return False, insert_line(line, ",", pos)
        # 11
        if error == errors.ArrayExceptObject:
            # fix [, --> [
            if lastchar == "[" and nextchar == ",":
                return False, remove_line(line, pos, pos + 1)
            if nextchar == ",":
                return False, insert_line(line, "null", pos)
            # ,] --> ]
            if nextchar == "]":
                return False, remove_line(line, pos - 1, pos)
            # 11.1
            if nextchar == "":
                # quick
                if lastchar == "[":
                    return False, insert_line(line, "]", pos)
                return False, insert_line(line, "null]", pos)
            # 11.2
            return False, insert_line(line, "{", pos)
            # 也许可以删掉前面的 , 补一个]
        # 12
        if error == errors.ArrayExceptComma:
            """
            code:
            end += 1
            if nextchar == ']':
                break
            elif nextchar != ',':
                raise ValueError(errmsg("Expecting ',' delimiter", s, end))
            """
            pos = pos - 1
            nextchar = line[pos: pos + 1]
            # 11.1
            if nextchar == "":
                return False, insert_line(line, "]", pos)
            # 11.2
            return False, insert_line(line, ",", pos)
        # unknonwn
        return False, line

    def patch_stop_iteration(self, line):
        # TODO fix
        # 1. }]
        # 2. ]}
        # 3. constans
        # 先 patch 完 {[]}
        left = patch_lastest_left_object_and_array(line)
        if left == "":
            last_notfix = (len(self.fix_stack) >= 2 and self.fix_stack[-2] == line)
            if last_notfix:
                left = patch_guess_left(line)

        new_line = left + line
        return False, new_line

    def patch_half_parse(self, line, err_info):
        obj, end = err_info
        nextline = line[end:].strip()
        nextchar = nextline[:1]
        left = patch_lastest_left_object_and_array(nextline)
        # ??
        if left == "":
            if nextchar == ",":
                left = "["
            elif nextchar == ":" and isinstance(obj, basestring):
                left = "{"
            else:
                last_notfix = (len(self.fix_stack) >= 2 and self.fix_stack[-2] == line)
                if last_notfix:
                    left = patch_guess_left(nextline)

        new_line = left + line[:end] + nextline
        return False, new_line


# TODO better name
def patch_lastest_left_object_and_array(line):
    # '}]{[' --> '[{}]{['
    pairs = {'}': '{', ']': '['}
    breaks = '{['
    left = ""
    for char in line:
        if char in breaks:
            break
        if char in pairs:
            left = pairs[char] + left

    return left


# TODO 改成 lastest
# {}}]]]] --> { not [
def patch_guess_left(line):
    miss_object = line.count('}') - line.count('{')
    miss_array = line.count(']') - line.count('[')
    if miss_object == miss_array == 0:
        if line[-1:] == '"' and line.count('"') == 1:
            return '"'
    elif miss_object >= miss_array:
        return '{'
    else:
        return '['
    return ''


def insert_line(line, value, pos, end=None):
    return line[:pos] + value + line[pos:]


def remove_line(line, start, end):
    return line[:start] + line[end:]
