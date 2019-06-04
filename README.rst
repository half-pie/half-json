
Usage
-----

.. code-block:: python

   In [1]: from half_json.core import JSONFixer

   In [2]: f = JSONFixer()

   In [3]: f.fix('[{')
   Out[3]: FixResult(success=True, line='[{}]', origin=False)

   In [4]: f.fix('{"a')
   Out[4]: FixResult(success=True, line='{"a":null}', origin=False)

目标
----

修复残破的 json

修复原理
--------


#. 根据异常提示来做一些操作, json 预期啥给啥
#. 根据文本前后,删除一些 BadCase

HitRatio
--------

.. code-block:: bash

   ./runtest.sh
   # 查看准确率
   seq 1 10|xargs -I {} ./runtest.sh|grep ratio: |awk '{t += $3; h+= $6}{print h/t}'|tail -1


#. 0.4269, 0.4287, 0.4303   # 实现完 12 条规则
#. 0.5037, 0.5084, 0.5077   # string 的 " 补充在末尾
#. 0.5259, 0.5224, 0.5187   # Array 需要 pos - 2
#. 0.5433, 0.5311, 0.5381   # Array 细化一下 [, 的情况
#. 0.7192, 0.7216, 0.7265   # 大改进, FIX 之前的 Bug( parser 被冲掉了)
#. 0.7732, 0.7686, 0.7701   # case: {"a":1 --> 补充 }
#. 0.60  , 0.58             # 去掉了空行
#. 0.6971, 0.6969, 0.6984   # 增加处理 StopIteration
#. 0.7428, 0.7383, 0.7427   # 增加处理 half parse
#. 0.7617,0.7631, 0.7558   # 细化处理 half parse
#. 0.7608,0.7612, 0.7650   # 添加从左处理
#. 0.9817,0.9827, 0.9819   # 增加对字符串的处理
#. 0.8314,0.8302, 0.8312   # 去掉对字符串的额外处理

目前的缺点 && 发现
------------------


#. 数字的支持比较弱 --> -02 / 0. / .0
#. 还不支持分支回溯 --> [{]
#. 突然想到, 应该反思一下, 这个是一个fixer, 而不是一个将任何字符串都转为 json 的东西
   应该明确 JSONFixer 的能力范围, 对 runratio.sh 也应该比较前后两个的 json 相似程度。
   (听起来像无能者的辩白?)

TODO
----


#. 考虑分支回溯的方式来试探
#. 解析缺失的 JSON 常量

BadCase
-------


#. 1- --> {"1-": null}
