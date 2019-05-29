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
            if "parser" not in  e.__dict__:
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
08 object 开始检测 Value 收到 StopIteration
08.1 要么后面没有了
08.2 要么后面不是 "/{/[/n[ull]/t[rue]/f[alse]/number/NaN/Infinity/-Infinity 开头的东西
-- 08.1 后面补上 null}
-- 08.2 无脑补一个 "
09 object 解析完一个 pair 后,下一个不是}, 期待一个 ','
   badcase {"k":1"s":2}
10 在 09 的基础上解析完{"k":1, 发现下一个不是 ", 这个后面再优化(暂时和 06 一致)
   badcase {"k":1,x":2}
11 array 开始检测 Value 收到 StopIteration
11.1 要么后面没有了,补上]
11.2 同 08.2,无脑补一个{ 看看
12 array 解析完前一个 object, 需要一个 ,
    这里 nextchar 既不是 ] 也不是, 代表这个 nextchar 的 end 也已经+1 了，所以减 2
"""

def process_number():
    pass


def find_stop(line):
    try:
        import pdb
        pdb.set_trace()

        # 暂时只考虑 1 行的情况
        obj, end = decoder.scan_once(line, 0)
        # TODO end is only part of line
        return end == len(line), line
    except StopIteration as e:
        return True, ""
    except ValueError as e:
        err_info = inv_errmsg(e, sys.exc_info())
        pos = err_info["pos"]
        nextchar = line[pos: pos+1]
        parser = err_info["parser"]
        errmsg = err_info["errmsg"]
        lastchar = line[pos-1: pos]

        # 02
        if errmsg == "Unterminated string starting at":
            # TODO resolve "abc --> "abc"
            return False, insert_line(line, "\"", len(line))
        # 06
        if errmsg == "Expecting property name enclosed in double quotes":
            # lastchar = line[pos-1: pos]
            # for case {
            # if lastchar == "{" and all([c not in line for c in '"}:']):
            #     return False, insert_line(line, "}", pos)
            return False, insert_line(line, "\"", pos)
        # 07
        if errmsg == "Expecting ':' delimiter":
            return False, insert_line(line, ":", pos)
        # 08
        if parser == "JSONObject" and errmsg == "Expecting object":
            # 08.1
            if nextchar == "":
                return False, insert_line(line, "null}", pos)
            # 08.2
            else:
                return False, insert_line(line, "\"", pos)
        # 09
        if parser == "JSONObject" and errmsg == "Expecting ',' delimiter":
            if nextchar == "":
                return False, insert_line(line, "}", pos)
            return False, insert_line(line, ",", pos)
        # 11
        if parser == "JSONArray" and errmsg == "Expecting object":
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
        if parser == "JSONArray" and errmsg == "Expecting ',' delimiter":
            """
            code:
            end += 1
            if nextchar == ']':
                break
            elif nextchar != ',':
                raise ValueError(errmsg("Expecting ',' delimiter", s, end))
            """
            pos = pos - 1
            nextchar = line[pos: pos +1]
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


def main(infile, outfile):
    inf = open(infile, 'r')
    outf = open(outfile, 'w')
    output = sys.stdout

    total = 0
    hit = 0

    for line in inf:
        try:
            total += 1
            line = line.strip()
            ok, new_line = clear(line)
            if ok:
                outf.write(new_line + "\n")
                hit += 1
            else:
                print(ok, line, new_line)
        except Exception as e:
            print(e, line)
    print("total is {} and hit {} --> ratio:{} \n".format(total, hit, hit*1.0/total))
    inf.close()
    outf.close()


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
