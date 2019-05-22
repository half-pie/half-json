## 目标

修复残破的 json

## 修复原理

1. 根据异常提示来做一些操作, json 预期啥给啥
2. 根据文本前后,删除一些 BadCase

## 当前测试

```
python gen.py > random.json
python broken.py random.json random.broken.json
python clear.py random.broken.json random.fix.json
```
