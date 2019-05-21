# coding=utf8

import re
import sys
import traceback
import functools
import json.decoder

from json.decoder import JSONDecoder
from json.scanner import py_make_scanner
from json.decoder import py_scanstring


# errmsg.inv
def inv_errmsg(e, exc_info):
    exc_type, exc_value, exc_traceback_obj = exc_info

    message = e.message
    # err, left = message.split(':', 1)  # badcase Expecting ':' delimiter
    idx = message.rindex(':')
    errmsg = message[:idx]
    left = message[idx + 1:]
    numbers = re.compile(r'\d+').findall(left)
    result = {
        "errmsg": errmsg,
        "parser": e.__dict__.get("parser", ""),
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


# 记录 Exception 被哪个 parser 抛出的
def add_parser_name(parser):

    # @functools.wraps
    def new_parser(*args, **kwargs):
        try:
            return parser(*args, **kwargs)
        except Exception as e:
            e.__dict__["parser"] = parser.__name__
            raise e
    return new_parser


def make_decoder():
    # json.decoder.scanstring = py_scanstring

    decoder = JSONDecoder()
    decoder.parse_object = add_parser_name(decoder.parse_object)
    decoder.parse_array = add_parser_name(decoder.parse_array)
    decoder.parse_string = add_parser_name(py_scanstring)
    decoder.parse_object = add_parser_name(decoder.parse_object)

    decoder.scan_once = py_make_scanner(decoder)

    json.decoder.scanstring = add_parser_name(py_scanstring)
    return decoder


decoder = make_decoder()

"""
ValueError 抛出
01. _decode_uXXXX "Invalid \\uXXXX escape"
02. py_scanstring "Unterminated string starting at"
03. py_scanstring "Invalid control character {0!r} at".format(terminator)
04. py_scanstring "Unterminated string starting at"
05. py_scanstring "Invalid \\escape: " + repr(esc)
06. JSONObject "Expecting property name enclosed in double quotes"
07. JSONObject "Expecting ':' delimiter"
08. JSONObject "Expecting object"
09. JSONObject "Expecting ',' delimiter"
10. JSONObject "Expecting property name enclosed in double quotes"
11. JSONArray  "Expecting object"
12. JSONArray  "Expecting ',' delimiter"

01 先不看,不研究
02 badcase: " --> "" success
03 控制符 pass
04 unicode \\u 的 pass
05 同上
06 object 后面没有跟随 " , badcase: {abc":1} --> {"abc":1}
07 object key 后面没有 : , badcase: {"abc"1} --> {"abc":1}
"""


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
        err_info = inv_errmsg(e, sys.exc_info())
        pos = err_info["pos"]
        nextchar = line[pos: pos+1]
        parser = err_info["parser"]
        errmsg = err_info["errmsg"]

        if errmsg == "Expecting object":
            return False, insert_line(line, "null", pos)
        if errmsg == "Expecting ',' delimiter":
            if nextchar == "}":
                return False, insert_line(line, ",", pos)
            elif nextchar == "":
                return False, insert_line(line, "}", pos)
            return False, insert_line(line, ",", pos)
        if errmsg == "Expecting , delimiter":
            if nextchar == "}":
                return False, insert_line(line, ",", pos)
            elif nextchar == "":
                return False, insert_line(line, "}", pos)
            return False, insert_line(line, ",", pos)
        # 06
        if errmsg == "Expecting property name enclosed in double quotes":
            return False, insert_line(line, "\"", pos)
        if errmsg == "Expecting ':' delimiter":
            return False, insert_line(line, ":", pos)
        if errmsg == "Unterminated string starting at":
            return False, insert_line(line, "\"", pos)

        raise e


def insert_line(line, value, pos, end=None):
    return line[:pos] + value + line[pos:]


def clear(line):
    for i in range(3):
        # import pdb
        # pdb.set_trace()
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
