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