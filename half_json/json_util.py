# coding=utf8

import json.decoder
from collections import namedtuple
from json.decoder import JSONDecoder
from json.scanner import py_make_scanner
from json.decoder import py_scanstring
from json.decoder import JSONDecodeError as PyJSONDecodeError


class JSONDecodeError(object):

    def __init__(self, parser, message):
        self.message = message
        self.parser = parser

    def __eq__(self, err):
        return err.parser == self.parser and self.message in err.message


class errors(object):

    StringInvalidUXXXXEscape = JSONDecodeError("py_scanstring", "Invalid \\uXXXX escape")
    # 2 different case
    StringUnterminatedString = JSONDecodeError("py_scanstring", "Unterminated string starting at")
    StringInvalidControlCharacter = JSONDecodeError("py_scanstring", "Invalid control character")
    StringInvalidEscape = JSONDecodeError("py_scanstring", "Invalid \\escape")
    ObjectExceptColon = JSONDecodeError("JSONObject", "Expecting ':' delimiter")
    ObjectExceptObject = JSONDecodeError("JSONObject", "Expecting value")
    # 2 different case
    ObjectExceptKey = JSONDecodeError("JSONObject", "Expecting property name enclosed in double quotes")
    ObjectExceptComma = JSONDecodeError("JSONObject", "Expecting ',' delimiter")
    ArrayExceptObject = JSONDecodeError("JSONArray", "Expecting value")
    ArrayExceptComma = JSONDecodeError("JSONArray", "Expecting ',' delimiter")

    @classmethod
    def get_decode_error(cls, parser, message):
        err = JSONDecodeError(parser, message)
        for _, value in cls.__dict__.items():
            if isinstance(value, JSONDecodeError):
                if err == value:
                    return value
        return None

    """
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


def errmsg_inv(e):
    assert isinstance(e, PyJSONDecodeError)
    parser = e.__dict__.get("parser", "")
    errmsg = e.msg
    localerr = errors.get_decode_error(parser, errmsg)
    result = {
        "parsers": e.__dict__.get("parsers", []),
        "error": localerr,
        "lineno": e.lineno,
        "colno": e.colno,
        "pos": e.pos,
    }
    return result


def record_parser_name(parser):
    def new_parser(*args, **kwargs):
        try:
            return parser(*args, **kwargs)
        except Exception as e:
            if "parser" not in e.__dict__:
                e.__dict__["parser"] = parser.__name__
            if "parsers" not in e.__dict__:
                e.__dict__["parsers"] = []
            e.__dict__["parsers"].append(parser.__name__)
            raise e
    return new_parser


def make_decoder():
    json.decoder.scanstring = record_parser_name(py_scanstring)

    decoder = JSONDecoder()
    decoder.parse_object = record_parser_name(decoder.parse_object)
    decoder.parse_array = record_parser_name(decoder.parse_array)
    decoder.parse_string = record_parser_name(py_scanstring)
    decoder.parse_object = record_parser_name(decoder.parse_object)

    decoder.scan_once = py_make_scanner(decoder)
    return decoder


decoder = make_decoder()


DecodeResult = namedtuple('DecodeResult', ['success', 'exception', 'err_info'])


def decode_line(line):
    try:
        obj, end = decoder.scan_once(line, 0)
        ok = end == len(line)
        return DecodeResult(success=ok, exception=None, err_info=(obj, end))
    except StopIteration as e:
        return DecodeResult(success=False, exception=e, err_info=None)
    except ValueError as e:
        err_info = errmsg_inv(e)
        return DecodeResult(success=False, exception=e, err_info=err_info)
