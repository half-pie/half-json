## Usage

```python
In [1]: from half_json.core import JSONFixer

In [2]: f = JSONFixer()

In [3]: f.fix('[{')
Out[3]: FixResult(success=True, line='[{}]', origin=False)

In [4]: f.fix('{"a')
Out[4]: FixResult(success=True, line='{"a":null}', origin=False)
```

## 目标

修复残破的 json

## 修复原理

1. 根据异常提示来做一些操作, json 预期啥给啥
2. 根据文本前后,删除一些 BadCase

## 当前测试

```bash
./runtest.sh
# 查看准确率
seq 1 10|xargs -I {} ./runtest.sh|grep ratio: |awk '{t += $3; h+= $6}{print h/t}'|tail -1
```

## HitRatio
1. 0.4269, 0.4287, 0.4303   # 实现完 12 条规则
2. 0.5037, 0.5084, 0.5077   # string 的 " 补充在末尾
3. 0.5259, 0.5224, 0.5187   # Array 需要 pos - 2
4. 0.5433, 0.5311, 0.5381   # Array 细化一下 [, 的情况
5. 0.7192, 0.7216, 0.7265   # 大改进, FIX 之前的 Bug( parser 被冲掉了)
6. 0.7732, 0.7686, 0.7701   # case: {"a":1 --> 补充 }

## 目前的缺点 && 发现

1. 从前往后扫描, 不容易识别 pair 在前面缺失的 -->  {}]
2. 靠异常比较难拿到当时的 Value, nextchar 和 end 倒是好拿
3. 数字的支持比较弱 --> -02 / 0. / .0
4. 还不支持回溯 --> [{]
5. 同一个 case, 处理空白的情况
6. 也许可以统计 [] {} "" 的配合情况

## TODO

1. 考虑尽量改成回溯的方式来试探
2. 解析缺失的 JSON 常量

## BadCase

1. {}]  / []]
2. 00