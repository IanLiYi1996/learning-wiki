# 免费离线实验：准入、容量与会话状态

整理日期：2026-11-04。这三个实验只用 Python 标准库、虚构候选和小状态机，不创建容器／VM、不执行陌生代码、不联网、不读取凭据、不访问云账户、不修改系统。它们说明测量与协议的区别，**不是 sandbox 实现、安全扫描器或真实产品评测**。

## 如何运行

在 Learning Wiki 仓库根目录：

```bash
python3 scripts/agent_sandbox_lab.py
python3 scripts/agent_sandbox_lab.py --json
python3 -m unittest discover -s tests -p 'test_agent_sandbox.py' -v
```

代码：[agent_sandbox_lab.py](https://github.com/IanLiYi1996/learning-wiki/blob/main/scripts/agent_sandbox_lab.py)，测试：[test_agent_sandbox.py](https://github.com/IanLiYi1996/learning-wiki/blob/main/tests/test_agent_sandbox.py)。网页不执行 Python；以上仓库链接需要本轮变更发布后才可在线访问，本地工作区已有文件。

## 实验一：最快的候选为什么不能赢

对应[选型章](08-selection-and-architectures.md)。四个虚构候选有相同的四个教学门槛：runtime、egress、identity、cleanup。字段表示**人为提供的教学证据**，不是从真实配置采集。

| 候选 | 假想首命令延迟 | 门槛 | 应有结果 |
| --- | --- | --- | --- |
| fast_unverified | 20 ms | runtime 未知 | 拒绝 |
| wide_egress | 40 ms | egress 失败 | 拒绝 |
| vetted_example | 150 ms | 四项均明确通过 | 准入 |
| slower_vetted | 300 ms | 四项均明确通过 | 准入 |

程序输出 `winner: vetted_example`。原因是先做硬门槛准入，再在准入集合比较延迟；没有用“速度多加 20 分”抵消网络要求。

把缺失字段、`None`、字符串 `"true"` 或整数 `1` 放进门槛，仍不能准入；模型只接受明确布尔 `True`。这演示未知不能偷偷变成通过，不证明现实证据足够。

预期思考：如果所有候选都失败，应输出无胜者，而不是挑出最不差的一项并宣称符合要求。真实验收还应核对证据来源、策略版本与过期时间。

## 实验二：λW 是平均算术，不是尾部保障

对应[生产章](10-production-and-benchmarks.md)。假设：

- 到达率 2 个任务／秒；
- 平均占用 30 秒；
- 目标利用率 0.7；
- 10 个未分配预热槽位；
- 每槽位假想内存 512 MiB。

应输出：

```text
mean_in_service = 60
online_slots = 86
total_slots = 96
slot_memory_mib = 49152
```

49152 MiB 为 48 GiB。没有计入宿主、guest 固定开销、VMM、page cache、controller、proxy、故障和突发。预热实例不是“免费容量”，但平均在服量也不是 p95 并发。

练习：改变平均占用或空闲池，看成本怎么变化；再解释为什么这还不能证明尾延迟 SLA。程序拒绝 NaN、无穷、负值、布尔伪装数字，以及不在 `(0, 1]` 的利用率。

## 实验三：名字没变，旧连接也不该继续获权

对应[生命周期](06-lifecycle-and-orchestration.md)与[网络身份](09-network-identity-and-data.md)。教学记录关联 tenant、policy、generation、state。

预期检查：

| 检查 | 预期 |
| --- | --- |
| Ready 前 | False |
| Running 中正确上下文 | True |
| 错租户／错策略 | False |
| Paused 中 | False |
| 恢复后的旧 generation | False |
| 恢复后的新 generation | True |
| Terminated 后 | False |

暂停后经 Provisioning 恢复，会使 generation 从 1 变成 2；旧上下文不能沿用。非法状态跳转和终态重新启用会抛出 `ValueError`。

这里比较的是已知字段，不包含任何密码学身份、JWT 签名、真实 broker、网络连接撤销、并发锁或分布式存储。在生产中，调用方自报字段不能作为信任根；控制面必须在认证与任务授权后生成可信上下文。

## 这些实验没有测什么

没有测内核逃逸、gVisor syscall、KVM、GPU、多租户宿主、DNS／IPv6、凭证注入、浏览器、产物扫描、数据删除、snapshot 随机状态或控制面故障。本地测试通过只说明这些教学模型的实现与文档预期一致。

真正 PoC 需要明确目标环境、授权范围、测试标记、资源费用和验收合同，见[生产验收](10-production-and-benchmarks.md)。本轮不自动创建这些资源。

[专题导读](README.md) · [学习路线](learning-roadmap.md) · [来源与研究边界](sources.md)
