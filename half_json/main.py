# coding=utf8
import sys

from half_json.core import JSONFixer


def fixjson():
    infile = sys.argv[1]
    outfile = sys.argv[2]

    inf = open(infile, 'r')
    outf = open(outfile, 'w')

    total = 0
    hit = 0

    fixer = JSONFixer()
    for line in inf:
        try:
            line = line.strip()
            if not line:
                continue
            total += 1
            ok, new_line = fixer.fix(line)
            if ok:
                outf.write(new_line + "\n")
                hit += 1
            else:
                print(ok, line, new_line)
        except Exception as e:
            print(e, line)
    print("total is {} and hit {} --> ratio:{} \n".format(total, hit, hit * 1.0 / total))
    inf.close()
    outf.close()
