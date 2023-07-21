# Install

```bash
pip install jsonfixer
```
# Usage

```python
In [1]: from half_json.core import JSONFixer

In [2]: f = JSONFixer()

In [3]: f.fix('[{')
Out[3]: FixResult(success=True, line='[{}]', origin=False)

In [4]: f.fix('{"a')
Out[4]: FixResult(success=True, line='{"a":null}', origin=False)

In [5]: f.fix('{"a":}')
Out[5]: FixResult(success=True, line='{"a":null}', origin=False)
```

## 目标

fix invalid/broken/truncated json

# 修复原理

1. JSONDecoderError
2. line context

## HitRatio

根据 checks 里面的工具来衡量修改效果

ABC : autogen --> broken --> check
TSR : run test.sh show.sh ratio.sh

### FixRatio

仅判断 result.success == True

```bash
./runratio.sh fix
```
```
1.  0.4269, 0.4287, 0.4303   # 实现完 12 条规则
2.  0.5037, 0.5084, 0.5077   # string 的 " 补充在末尾
3.  0.5259, 0.5224, 0.5187   # Array 需要 pos - 2
4.  0.5433, 0.5311, 0.5381   # Array 细化一下 [, 的情况
5.  0.7192, 0.7216, 0.7265   # 大改进, FIX 之前的 Bug( parser 被冲掉了)
6.  0.7732, 0.7686, 0.7701   # case: {"a":1 --> 补充 }
7.  0.60  , 0.58             # 去掉了空行
8.  0.6971, 0.6969, 0.6984   # 增加处理 StopIteration
9.  0.7428, 0.7383, 0.7427   # 增加处理 half parse
10. 0.7617, 0.7631, 0.7558   # 细化处理 half parse
11. 0.7608, 0.7612, 0.7650   # 添加从左处理
12. 0.9817, 0.9827, 0.9819   # 增加对字符串的处理
13. 0.8314, 0.8302, 0.8312   # 去掉对字符串的额外处理
14. 0.95X                    # 已不可参考
```

### Real HitRatio

判断 result.success == True

并且解析后的 json 大体和原来一致(equal && dictdiffer)

```bash
./runratio.sh hit
```
```
1. 0.5610, 0.5563, 0.5529   # origin
2. 0.5593, 0.5532, 0.5587   # fix :} --> :null}
```

# TODO

## 目前的缺点 && 发现

3. 数字的支持比较弱 --> -02 / 0. / .0
4. 还不支持分支回溯 --> [{]
7. 突然想到, 应该反思一下, 这个是一个fixer, 而不是一个将任何字符串都转为 json 的东西
   应该明确 JSONFixer 的能力范围, 对 runratio.sh 也应该比较前后两个的 json 相似程度。
   (听起来像无能者的辩白?)
8. 也需要吧 parser 也做成 stack 这样可以解决 ["a] --> ["a"] 这样的 case

1. 考虑分支回溯的方式来试探
2. 解析缺失的 JSON 常量
9.

## BadCase
1. 1- --> {"1-": null}
