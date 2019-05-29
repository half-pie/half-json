# coding=utf8
from half_json.json_util import decoder
from half_json.json_util import errmsg_inv
from half_json.json_util import errors


def find_stop(line):
    try:
        # 暂时只考虑 1 行的情况
        obj, end = decoder.scan_once(line, 0)
        # TODO end is only part of line
        return end == len(line), line
    except StopIteration as e:
        return True, ""
    except ValueError as e:
        err_info = errmsg_inv(e)
        error = err_info["error"]
        pos = err_info["pos"]
        nextchar = line[pos: pos+1]
        # lastchar = line[pos-1: pos]

        # 02
        if error == errors.StringUnterminatedString:
            # TODO resolve "abc --> "abc"
            return False, insert_line(line, "\"", len(line))
        # 06
        if error == errors.ObjectExceptKey:
            # lastchar = line[pos-1: pos]
            # for case {
            # if lastchar == "{" and all([c not in line for c in '"}:']):
            #     return False, insert_line(line, "}", pos)
            return False, insert_line(line, "\"", pos)
        # 07
        if error == errors.ObjectExceptColon:
            return False, insert_line(line, ":", pos)
        # 08
        if error == errors.ObjectExceptObject:
            # 08.1
            if nextchar == "":
                return False, insert_line(line, "null}", pos)
            # 08.2
            else:
                return False, insert_line(line, "\"", pos)
        # 09
        if error == errors.ObjectExceptComma:
            if nextchar == "":
                return False, insert_line(line, "}", pos)
            return False, insert_line(line, ",", pos)
        # 11
        if error == errors.ArrayExceptObject:
            # ?
            if nextchar == ",":
                return False, insert_line(line, "null", pos)
            # 11.1
            if nextchar == "":
                return False, insert_line(line, "null]", pos)
            # 11.2
            else:
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
            else:
                return False, insert_line(line, ",", pos)
        raise e


def insert_line(line, value, pos, end=None):
    return line[:pos] + value + line[pos:]


def clear(line):
    ok = False
    for i in range(10):
        ok, line = find_stop(line)
        if ok:
            break
    return ok, line
