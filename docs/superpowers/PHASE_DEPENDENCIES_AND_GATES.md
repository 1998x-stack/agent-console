# 六阶段依赖图与 Exit Gates

> 状态：目标设计。所有 Exit Gate 当前默认 **NOT RUN / NOT PASSED**，无真实证据禁止跳过。

## 1. 依赖拓扑

§§§mermaid
flowchart TD
  P0A["P0A · Self-hosted Setup & BYOK"] --> P0B["P0B · Pi Runner & Workspace"]
  P0B --> P0C["P0C · Local Skill & E2E"]
  P0C --> P1["P1 · Private Creator & Safe Writes"]
  P1 --> P2["P2 · Org / Public Registry & Governance"]
  P2 --> P3["P3 · Ecosystem & Operating Maturity"]
  P0A -. "Revalidation at every phase" .-> Q["Security / Contract / Migration Gates"]
  P0B -.-> Q
  P0C -.-> Q
  P1 -.-> Q
  P2 -.-> Q
  P3 -.-> Q
§§§

其中 P3 的组件按真实需求激活；不要求为了“路线完成”实现全部功能。P0B/P0C 可迭代，但**不得绕过单用户的文件/密钥隔离要求**。

## 2. 通用入口（Entry Gate）

- 上阶段 Spec、Plan、AC 和测试证据已链接；
- API/DB/事件/Runner 共享接口存在明确版本与兼容测试；
- 开发分支隔离且前一次提交测试 baseline 真实可复现；
- 任何需要新增权限的任务都有安全/失败测试计划；
- 未解决的重要设计争议记录为 ADR + PoC，而非实现 Agent 的自由发挥；
- 人类决定可以进入下一阶段；尤其多用户/公共市场需要明确安全批准。

## 3. 阶段退出条件

| Phase | 真正的可交付用户成果 | 阻断性验收 | 尚不承诺 |
|---|---|---|---|
| P0A | 干净机器 Compose 启动；通过 Web 初始化与配置真实兼容模型 | 无 Key 可启动；初始化原子；密钥不泄漏；模型连接失败可解释；DB 持久 | Pi 代码工具执行 |
| P0B | Pi 从 Web 接收任务，在当前用户目录读取文件并生成受控 Artifact | 真 Pi + 真实模型 smoke、流式事件与重连、Pi Session 冷重启、安全目录绑定、取消终态 | Bash/多租户任意脚本 |
| P0C | Web 内置离线 Skill Store，安装固定 Release 并由 Pi 在新 Run 使用 | 安装/禁用真实影响装载；包完整性/恶意 zip 测试；全链路浏览器 E2E；备份基础演练 | 公共发布和收费 |
| P1 | 用户从任务生成、编辑、测试和安装自己的 Skill，安全生成代码 Diff | 受限写/测试沙箱、负例触发评测、权限/凭证对抗、数据恢复与冲突 | 默认直接发邮件/推生产 |
| P2 | 经验证的多用户/组织分享与公共发布、Unlist、Revoke | 跨用户 OS 隔离、审核原子性、供应链验证、旧安装权益、安全处置可复现 | 复杂大规模计费 |
| P3 | CLI/SDK、授权连接器、搜索优化、规模化运维 | 兼容测试、升级/回滚、压测有据、运营指标真实 | 不经需求验证的全平台功能 |

## 4. 不可稀释的 P0 阻断项

- 非授权读取任何其他用户或宿主敏感文件；明文 Key 出现在日志/Session/Tool Env；
- Web 初始化存在重复管理员/弱默认密码；
- Pi Runner 可利用项目 §.pi/extensions§ 任意在主服务权限域执行；
- Run Status = SUCCEEDED，但验证器未运行或 Artifact 已损坏；
- 终止/重试重复产生外部副作用；
- 无法从全新数据卷启动及重启保留核心持久数据；
- 无法恢复/解释 SSE 断连后的任务状态。

## 5. Gate 证据格式

§§§text
Phase ID:
Branch/Commit/Image digest:
Host OS + Docker version:
Pi package version + lockfile:
Test command / exit code / count:
Fixture + Oracle:
Negative / security tests:
Failure / NOT RUN:
Artifacts / logs paths (redacted):
Decision: PASS / FAIL / BLOCKED / NOT RUN
Approved by / date:
§§§

§PASS§ 必须具备真实命令输出和风险评审；文档完整不能作为阶段 Gate 的 §PASS§ 证据。默认从 §NOT RUN§ 开始。

## 6. 迁移/变更与恢复门禁

每阶段涉及数据库/会话或 Skill 包格式变化时：
- DB 使用 expand → backfill → read compatibility → constraints；
- Pi Session 格式升级必须测试旧样本可读或明确只读降级；
- Skill 发布版本内容不可变，已安装 Release 不被偷偷覆盖；
- Docker 镜像/数据卷备份与恢复需要一次“空环境还原”演练；
- 回滚步骤必须能在失败后保留用户工作目录。

## 7. 阶段外紧急修复

严重漏洞可以中断当前阶段；先复现 → 写失败回归 → 修复 → 验证 → 复盘 §docs/gotchas.md§，并对更高阶段依赖做回归。紧急修复不能以“后期再补测试”为常态。
