# coding=utf8

import re
import sys
import json

from json.decoder import JSONDecoder
from json.scanner import py_make_scanner


# errmsg.inv
def inv_errmsg(e):
    message = e.message

    err, left = message.split(':', 1)
    numbers = re.compile(r'\d+').findall(left)
    result = {
        "err": err,
        "lineno": int(numbers[0]),
        "colno": int(numbers[1]),
    }
    if len(numbers) == 3:
        result["pos"] = int(numbers[2])

    if len(numbers) > 3:
        result["endlineno"] = int(numbers[2])
        result["endcolno"] = int(numbers[3])
        result["pos"] = int(numbers[4])
        result["end"] = int(numbers[5])
    return result

decoder = JSONDecoder()
decoder.scan_once = py_make_scanner(decoder)


def find_stop(line):
    try:
        # import pdb
        # pdb.set_trace()
        # 暂时只考虑 1 行的情况
        obj, end = decoder.scan_once(line, 0)
        return True, line
    except StopIteration as e:
        return True, ""
    except ValueError as e:
        err_info = inv_errmsg(e)
        pos = err_info["pos"]
        nextchar = line[pos: pos+1]

        if err_info["err"] == "Expecting object":
            return False, insert_line(line, "null", pos)
        if err_info["err"] == "Expecting ',' delimiter":
            if nextchar == "}":
                return False, insert_line(line, ",", pos)
            elif nextchar == "":
                return False, insert_line(line, "}", pos)
            return False, insert_line(line, ",", pos)
        if err_info["err"] == "Expecting property name enclosed in double quotes":
            return False, insert_line(line, "\"", pos)
        if err_info["err"] == "Unterminated string starting at":
            return False, insert_line(line, "\"", pos)
        raise e


def insert_line(line, value, pos, end=None):
    return line[:pos] + value + line[pos:]


def clear(line):
    for i in range(3):
        ok, line = find_stop(line)
        if ok:
            break
    return line


def main(filename):
    f = open(filename, 'r')
    output = sys.stdout
    for line in f:
        new_line = clear(line.strip())
        output.write(new_line + "\n")

    output.close()
    f.close()


if __name__ == '__main__':
    main(sys.argv[1])
