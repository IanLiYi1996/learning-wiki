# 四个离线记忆练习：准入、失效、并发与回本

整理日期：2026-11-11。[专题导读](README.md)。这是合成数据上的教学演示，不是 Claude memory、数据库、Dreams 或 benchmark 的实现。

Python 3.9+ 标准库；不访问网络、模型、真实租户数据，也不写文件或实际记忆库。两套专题共用一份小脚本：[memory_and_flow_lab.py](https://github.com/IanLiYi1996/learning-wiki/blob/main/scripts/memory_and_flow_lab.py)；测试：[test_memory_and_flow_studies.py](https://github.com/IanLiYi1996/learning-wiki/blob/main/tests/test_memory_and_flow_studies.py)。仓库未发布新文件时，网页源码链接需等待发布。

在仓库根目录运行：

```bash
python -B scripts/memory_and_flow_lab.py --group memory
python -B -m unittest discover -s tests -p 'test_memory_and_flow_studies.py' -v
```

## A. 准入合同不是事实验证器

`memory_gate` 检查声明的租户／项目、证据标签、来源版本和有效期。当前 `interface/v2`、时间 10 的例子：

| 记录 | 结果 |
| --- | --- |
| 当前范围与版本、verified、仍有效 | `admit` |
| 旧版本 v1 | `wrong-version` |
| 未验证假设 | `unverified` |
| 已过有效期 | `expired` |
| 别的租户 | `wrong-scope` |

有效上界为 `valid_before`：到达这个时刻就过期；未来观察报错。还会拒绝 revoked 和未知 source。所有字段只是调用方提供的合成声明，`verified` 不会自己验证真实性，`admit` 也不是外部操作授权。

练习：一条笔记内容本来正确，但当前用户要求相反格式，是否应盲目执行？**不应，准入后仍需检查当前意图与指令优先级。**

## B. 根证据失效，派生内容一起待复核

`invalidate` 接受显式依赖 DAG。例子：

```text
source → note → wiki → report
unrelated
```

根 `source` 改变后，输出 `note、report、source、wiki`，不包括 `unrelated`。函数只给出应复核的节点名，不删除或改写任何记录。

未知节点、悬空依赖、重复 parent 和循环会拒绝。这是显式登记关系上的传播；真实系统没有登记的复制件、外部报告与备份，不能由这个函数自动发现。

## C. 两次“正确写入”，可能丢一条事实

原记录含 α，A 与 B 都读版本 0。A 增加 β；B 用旧副本增加 γ 并覆盖，最终只剩 α、γ。例子输出 `naive_last_write_facts` 展示这一丢写。

`cas_write` 要求当前版本等于读到的版本。B 的旧版本写入被拒绝；重新读到版本 1 后，把 γ 合入已有 α、β，得到三个事实。

这里用顺序操作模拟并发交错，没有线程或真实数据库事务。它不能裁决相互矛盾的内容，也不证明真实 wiki 已达到串行化或零丢写。

## D. 算清构建与更新成本

`break_even(120,10,7,1)` 返回净节约 **2／题**，相等点 **60 题**。要求最小正整数 N，使记忆方案总成本不高于 baseline。

若每题记忆开销更高，或相同但还有正构建成本，返回 `None`；没有这个简单线性模型中的有限回本点。零构建、完全相同开销在第一题就相等，但不代表存在收益。

成本是虚构预算单位，不是费率或投资建议。真实更新时间可能随查询、漂移和缓存非线性变化，需要重写成本合同。

## 四道自测

1. `admit` 证明内容真实了吗？**没有，只是通过声明的机械检查。**
2. 删除 source，外部报告会自动更正吗？**不会；本例只标记登记的依赖。**
3. CAS 成功，β 与 γ 就没有语义冲突了吗？**没有，还需审阅内容。**
4. 每题省 2 单位，就能忽略构建 120 吗？**不能，本例需要 60 题达到相等点。**

这些练习只验证小数组、类型、边界和文档数字。下一步应写明权限、事实依据、真实删除与长期收益的验收，而不是立即连接真实用户资料。
