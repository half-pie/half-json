# coding=utf8
import json
from collections import namedtuple

from half_json.json_util import decode_line
from half_json.json_util import errors


FixResult = namedtuple('FixResult', ['success', 'line', 'origin'])


class JSONFixer(object):

    def __init__(self, max_try=20):
        self._max_try = max_try

    def fix(self, line):
        try:
            json.loads(line)
            return FixResult(success=True, line=line, origin=True)
        except Exception:
            pass

        ok, new_line = self.fixwithtry(line)
        return FixResult(success=True, line=new_line, origin=False)

    def fixwithtry(self, line):
        if self._max_try <= 0:
            return False, line
        for _ in range(self._max_try):
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
            # 08.2
            return False, insert_line(line, "\"", pos)
        # 09
        if error == errors.ObjectExceptComma:
            if nextchar == "":
                return False, insert_line(line, "}", pos)
            return False, insert_line(line, ",", pos)
        # 11
        if error == errors.ArrayExceptObject:
            # fix-error
            if lastchar == "[" and nextchar == ",":
                return False, remove_line(line, pos, pos + 1)
            if nextchar == ",":
                return False, insert_line(line, "null", pos)
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
        # TODO StopIteration
        return False, line


def insert_line(line, value, pos, end=None):
    return line[:pos] + value + line[pos:]


def remove_line(line, start, end):
    return line[:start] + line[end:]
