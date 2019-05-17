import sys
import json

from json.decoder import JSONDecoder
from json.scanner import py_make_scanner


def find_stop(line):
    d = JSONDecoder()
    d.scan_once = py_make_scanner(d)
    # TODO
    try:
        obj, end = d.scan_once(line, 0)
    except StopIteration as e:
        raise e
    return line


def clear(line):
    try:
        json.load(line)
        return line
    except Exception as e:
        pass
    new_line = find_stop(line)
    return new_line


def main(filename):
    f = open(filename, 'r')
    output = sys.stdout
    for line in f:
        result = clear(line)
        output.write(result)

    output.close()
    f.close()


if __name__ == '__main__':
    main(sys.argv[1])
