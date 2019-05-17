# coding=utf8

import re
import sys
import json

from json.decoder import JSONDecoder
from json.scanner import py_make_scanner


"""
def errmsg(msg, doc, pos, end=None):
    # Note that this function is called from _json
    lineno, colno = linecol(doc, pos)
    if end is None:
        fmt = '{0}: line {1} column {2} (char {3})'
        return fmt.format(msg, lineno, colno, pos)
        #fmt = '%s: line %d column %d (char %d)'
        #return fmt % (msg, lineno, colno, pos)
    endlineno, endcolno = linecol(doc, end)
    fmt = '{0}: line {1} column {2} - line {3} column {4} (char {5} - {6})'
    return fmt.format(msg, lineno, colno, endlineno, endcolno, pos, end)
    #fmt = '%s: line %d column %d - line %d column %d (char %d - %d)'
    #return fmt % (msg, lineno, colno, endlineno, endcolno, pos, end)
"""

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


# 暂时只考虑 1 行的情况
def find_stop(line):
    d = JSONDecoder()
    d.scan_once = py_make_scanner(d)
    try:
        # import pdb
        # pdb.set_trace()
        obj, end = d.scan_once(line, 0)
        return line
    except ValueError as e:
        err_info = inv_errmsg(e)
        pos = err_info["pos"]
        if err_info["err"] == "Expecting object":
            return insert_line(line, "null", pos)
        if err_info["err"] == "Expecting ',' delimiter":
            if line[pos:] == "":
                return insert_line(line, "}", pos)
            return insert_line(line, ",", pos)
        raise e


def insert_line(line, value, pos, end=None):
    return line[:pos] + value + line[pos:]


def clear(line):
    new_line = find_stop(line)
    return new_line


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
