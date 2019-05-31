# coding=utf8
import sys
import json
import random


def borken(s):
    idx = random.randint(0, len(s) + 1)
    return s[:idx] + s[idx + 1:]


def main(inflie, outfile):
    inf = open(inflie, 'r')
    outf = open(outfile, 'w')
    for line in inf:
        line = line.strip()
        if not line:
            continue
        for i in range(random.randint(3, 10)):
            new_line = borken(line)
            if not new_line:
                continue
            try:
                json.loads(new_line)
            except Exception:
                # only broken
                outf.write(new_line)
                outf.write('\n')

    inf.close()
    outf.close()


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
