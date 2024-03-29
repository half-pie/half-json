# coding=utf8

import sys

from half_json.core import JSONFixer


def fixjson() -> None:
    infile = sys.argv[1]
    outfile = sys.argv[2]

    inf = open(infile, "r")
    outf = open(outfile, "w")

    total = 0
    hit = 0

    fixer = JSONFixer()
    for line in inf:
        try:
            line = line.strip()
            if not line:
                continue
            total += 1
            result = fixer.fix(line)
            if result.success:
                outf.write(result.line + "\n")
                if not result.origin:
                    hit += 1
            else:
                print(result)
        except Exception as e:
            print(e, line)
    print(f"total is {total} and hit {hit} --> ratio:{hit * 1.0 / total} \n")
    inf.close()
    outf.close()
