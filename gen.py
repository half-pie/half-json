# coding=utf8
import json
import random

def gen_random_str():
    chars = range(33, 127)
    s = ""
    for i in range(random.randint(0, 10)):
        s += chr(random.choice(chars))
    return s

def gen_random_int():
    return random.choice([0, 1, 0.0, -1, -0.2, 123123123123121312312312, 32323e3])

def get_random_object():
    funcs = [dict, list, gen_random_str, gen_random_int]
    obj = random.choice(funcs)()
    if isinstance(obj, dict):
        for i in range(random.randint(0, 3)):
            obj[gen_random_str()] = get_random_object()
    if isinstance(obj, list):
        for i in range(random.randint(0, 4)):
            obj.append(get_random_object())
    return obj


def main():
    for i in range(1000):
        obj = get_random_object()
        print(json.dumps(obj))


if __name__ == '__main__':
    main()
