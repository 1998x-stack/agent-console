# 07 — 用户、创作者、管理员、公共治理与安全边界

> Draft v0.4 · 对标 Apple App Store Connect 的开发者管理思想，但不照搬“创作者必须离开 Client 去管理后台”；用户侧和治理侧权限是两回事。参考：[Security Model](../SECURITY_MODEL.md)、[Skill Store](06_SKILL_CREATOR_AND_STORE.md)。

## 1. 两个层次、五类权限主体

- **Ordinary User**：执行 Agent、管理本人 Workspace/模型密钥、创建和安装私人 Skill。
- **Creator**：是 User 在某个 Skill 上具有 owner/edit rights 的状态，不是全局特殊角色。
- **Workspace/Organization Admin（P2）**：管理团队成员、共享资源、发布策略，而不是自动取得所有人的明文密钥。
- **Deployment Admin**：负责本地实例、用户准入、系统更新、备份、网络/模型端点允许列表和运行容量。
- **Registry Moderator（P2）**：只在接入公共 Registry 后存在，负责跨用户公开资产审核、紧急撤销、申诉；与本地部署管理员分离。

**为什么**：P0 单用户也需要初始化管理员，但创建 Skill 不应被“管理员身份”捆绑。未来多用户扩展时，三种管理员若混成一类，将导致权限范围不可解释和敏感数据被无必要访问。

## 2. 功能归属矩阵

| 功能 | User/Creator Client | Local Admin | Org Admin(P2) | Registry Moderator(P2) |
|---|---|---|---|---|
| Chat/Run/Cancel 自己的任务 | ✓ | 自己任务 | 自己任务 | 无 |
| 添加个人 BYOK 模型 | ✓ | 可设配置策略 | 可设组织策略 | 无 |
| 查看个人 Key 明文 | 不提供再次读取 | 不提供 | 不提供 | 不提供 |
| 访问 Workspace 文件 | 自己已授权范围 | 仅经特定维护授权 | 组织许可范围 | 无 |
| 创建/编辑/测试私人 Skill | ✓ | ✓ | ✓ | ✓（自己的） |
| 安装/禁用/卸载 Skill | ✓ | 全局允许/禁止策略 | 组织允许/禁止策略 | 无 |
| 私人发布 | ✓ | 无需审核 | 按组织策略 | 无 |
| 团队分享/审批 | 提交/按授权操作 | 系统策略 | ✓ | 无 |
| 公共市场上架 | 提交申请 | 管理外发许可 | 外发策略 | 审核 |
| 创作者主动 Unlist | 自己上架资产 | 策略控制 | 按组织权属 | 违规干预 |
| 安全 Revoke/Quarantine | 无 | 本地紧急阻断 | 组织阻断 | 公共源阻断 |
| 审计/监控 | 自己运行记录 | 系统安全视图 | 组织聚合视图 | 公共审核 |
| 用户/账户管理 | 自己账号 | 本地实例用户 | 团队成员 | 无 |

表格是**本产品目标设计**，不是竞品已实现功能的声明。

## 3. 权限模型必须是组合，而非 role == admin

每个敏感调用：`Decision = RBAC ∩ Resource Ownership/ABAC ∩ Capability Grant ∩ Sandbox Allowance`。

- RBAC：功能角色能不能执行某种动作。
- ABAC：该 Workspace/Skill/文件/模型连接是否属于调用者或有授权分享。
- Capability Grant：读哪个目录、写哪个文件、向哪个域名发送、调用哪个工具，授权有效期多久。
- Sandbox：即使 API 判定通过，OS 级挂载/网络依然限制后果。
- 审批是对**具体动作实例**的授权，不是放开整个 Session 任意网络权限。

示例：用户拥有 `skill.create`，但不自动拥有 `shell.exec`；能安装高风险 Skill 不意味着可以执行其脚本；Deployment Admin 能停用系统模型，但不自动拥有用户的原始服务商 Key。

## 4. 高风险动作分级

| 等级 | 例子 | 默认 UX | 审计 |
|---|---|---|---|
| L0 | 模型回答、纯文本变换 | 直接执行 | 请求/模型 ID |
| L1 | 读取被授权 Workspace 文件 | 透明展示 | 路径、工具、结果摘要 |
| L2 | 新建文件、修改沙箱副本 | 有 Diff/预览，可恢复 | 写入版本与哈希 |
| L3 | 覆盖原件、提交 Git 远端、发送消息 | 明确目标、变化和一次性审批 | 审批人、目标、版本 |
| L4 | 删除大量文件、生产部署、全局高危配置 | 默认禁止；专门管理员操作流程 | 双重确认/审计 |

风险分级与数据敏感性结合。普通“写入文件”若发生在共享财务目录，可能比单纯读取测试仓库更高风险。

## 5. Trust Boundaries 与攻击路径

```text
Browser (untrusted input)
   → API/Auth (trusted control-plane)
   → RunSpec signed / validated
   → Pi Worker (not a security boundary)
   → Tool Gateway + isolated sandbox
   → user-authorized workspace & external services
External: model response / Skill / Git repo / uploaded doc / MCP result = untrusted
```

安全设计不只“防 SQL 注入”。还要防：
- Prompt Injection：办公文档、Git README、Skill 描述诱导 Pi 泄漏密钥。
- Supply Chain：第三方 Skill/Extension 夹带可执行 JS、Shell 或依赖投毒。
- SSRF：用户配置 Model Base URL，脚本访问内网/云元数据地址。
- Cross-user Path：路径拼接、软链接、Zip Slip、Runner mount 权限过大。
- Session Fixation / Cross-session Events：Run ID 猜测、SSE 缺 ACL、错误事件归属。
- Approval Replay：同一审批被重复调用或审批参数与实际 Tool 不一致。
- Secret Exfiltration：SDK Session、工具输出、日志、Artifact 误记录服务商 Key。
- Admin Power Creep：管理员错误地拥有所有用户聊天、文件及 Key 明文访问权。

## 6. Pi 执行隔离绝不是 Tool 白名单

Pi 自带的 `bash`、`read`、`write`、`edit` 能触达 Worker 的 OS 资源；Pi Extensions 是可执行的 TypeScript。SDK `tools: ["read"]` 能影响 Agent 可见工具，但无法提供容器级安全保证。必须在真正受限的进程/沙箱中运行，限制网络/文件/环境/资源、禁用未知 Extension 自动发现，禁止把 Docker Socket 暴露给普通 API。

即便把 Tool Call Gateway 包在 Pi Extension 事件上，Worker 依然可能访问未授权文件——除非 OS mount 和内部服务 ACL 限制它。安全性要以负例攻击测试作为证明。

## 7. 首次启动与身份认证

- 单用户实例首次管理员创建必须仅一次有效，并防并发争抢；不带预置密码，初始化接口不可远程滥用。
- 默认仅绑定 loopback；用户若公开到 LAN/互联网，应启用 TLS、身份验证、会话安全、CSRF、暴力破解限速、反向代理可信 IP 配置。
- 后端 Session Cookie 与 Model Key 分离；管理员会话过期、角色变更、删除用户时，工作区 Task 与 SDK 会话是否仍执行必须有明确策略。
- 如支持多用户（P2），新用户默认 pending / invite-only，不开放公共自助注册后立刻给予 Shell 执行权。

## 8. 管理控制台功能：P0/P1 与未来

**P0 必须**：初始化状态、模型共享策略开关、存储使用量、Runner Health、备份/恢复入口、日志错误摘要、禁用高危工具。不要在 P0 设计审查员排班、复杂收费系统。

**P1**：审计过滤、失败任务诊断、用户数据导出/删除、系统级 Skill allow/deny list，管理员可暂停所有高风险执行。

**P2**：用户和组织、授权与资源共享、审批队列、公共上架审核、举报、紧急撤销、申诉、滥用速率限制。

管理员必须看到“对方资源的元数据”还是“内容原文”？默认先让管理员查看运行计数、错误分类、状态和资源占用；查看用户文件/对话须单独权限与显式审计，不因部署管理员身份自动获得所有内容。

## 9. 平台治理流程（仅公共市场）

`Submitted → Automated Checks → Human Review (if required) → Published / Rejected`；
违规处置：`Report → Triage → Quarantine/Unlist/Revoke → Notify → Appeal → Restore/Confirm`。

“Unlist”影响新安装；“Revoke”可禁止既有安装执行；紧急处置应有到期复核和审计证据。用户私人 Skill 的普通编辑不需要等待公共审核。创作者有主动下架权，平台保留独立安全阻断权。

## 10. 隐私、备份与退出

默认本地保存聊天、工作区与 Skill；模型 API 调用需要提示数据会发到用户选定的供应商，不能承诺全离线（除非选本地模型且无远程源）。导出用户数据、删除账号、日志保留、备份密钥和恢复都要有明确行为；“删除账号”并不必然马上物理销毁被其它用户合法安装的公开技能版本，要明确定义后续合规策略。

## 11. 测试门禁

- AC-SEC-01 用户 A 不能通过 API、SSE、文件路径、Skill 元数据、模型连接访问 B。
- AC-SEC-02 伪造审批/重复审批/过期审批不能执行 Tool。
- AC-SEC-03 Prompt Injection 不会突破 Tool Gateway 和沙箱。
- AC-SEC-04 未经审核的 Pi Extension 不能从用户仓库目录自动加载。
- AC-SEC-05 API Key 不在浏览器响应、错误堆栈、Session JSONL、Sandbox Env、日志或 Artifacts 中出现。
- AC-SEC-06 公共 Listing 下架与安全 Revoke 的实际行为可区分且被审计。
- AC-SEC-07 首次管理员初始化并发测试：只能创建一个管理员、无后门弱密码。
- AC-SEC-08 未通过多用户隔离前，UI/文档不能宣称多用户 Shell 执行安全。
