# coding=utf8
import sys
import json

from half_json.core import JSONFixer

f = JSONFixer(100)


def json_equal(line, origin):
    return json.loads(line) == json.loads(origin)


def main(inflie, outfile):
    inf = open(inflie, 'r')
    outf = open(outfile, 'w')

    total = 0
    hit = 0
    fix = 0

    for line in inf:
        info = json.loads(line)
        result = f.fix(info['broken'])
        info['fixed'] = result.success
        info['fix'] = result.line
        info['hited'] = False
        if info['fixed']:
            info['hited'] = json_equal(result.line, info['origin'])

        outf.write(json.dumps(info))
        outf.write('\n')

        if info['fixed']:
            fix += 1
        if info['hited']:
            hit += 1
        total += 1

    print('total: %d fix: %d hit: %d' % (total, fix, hit))
    print('fix ratio: %f' % (fix * 1.0 / total))
    print('hit ratio: %f' % (hit * 1.0 / total))

    inf.close()
    outf.close()


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
