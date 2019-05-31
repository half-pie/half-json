# coding=utf8
from half_json.json_util import decoder
from half_json.json_util import errmsg_inv
from half_json.json_util import errors


def check_line(line):
    # 暂时只考虑 1 行的情况
    try:
        _, end = decoder.scan_once(line, 0)
        return end == len(line), None
    except StopIteration as e:
        return False, None
    except ValueError as e:
        err_info = errmsg_inv(e)
        if err_info["error"] is None:
            raise e
        return False, err_info


def insert_line(line, value, pos, end=None):
    return line[:pos] + value + line[pos:]


def remove_line(line, start, end):
    return line[:start] + line[end:]


def patch_line(line, context=None):
    ok, err_info = check_line(line)
    if ok:
        return True, line
    if err_info is None:
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


def clear(line):
    ok = False
    for i in range(40):
        ok, line = patch_line(line)
        if ok:
            break
    return ok, line
