# 05 — Pi Agent Engine、会话、任务编排、工具与长任务一致性

> Draft v0.4 · Pi 提供模型交互、工具循环、会话与资源加载；Agent Console 提供数据与安全权威。相关：[Pi 官方集成专题](../PI_AGENT_INTEGRATION.md)、[模型](03_MODEL_ONBOARDING.md)、[Workspace](04_WORKSPACE_AND_ARTIFACTS.md)。

## 1. Pi 不是 SaaS 后台，也不是授权系统

**分层决定**：
- Web（Next.js）：交互。
- API（FastAPI）：Auth、Run 状态机、Workspace ACL、审批、密钥/模型管理、Registry。
- Pi Worker（Node/TS）：SDK AgentSession、模型选择、资源加载、Tool Call Loop。
- Runner/Sandbox：限制进程、内存、网络、文件挂载，控制实际副作用。
- PostgreSQL：Run/Step/Event 和业务元数据的唯一持久权威。
- Session Store：Pi SessionManager 持久对话上下文，与我们的 Conversation 映射。

不要把 Pi `createAgentSession()` 返回对象随手序列化到数据库；会话持久化要遵循官方 `SessionManager`，DB 保存会话索引和授权关系。

## 2. RunSpec（仅服务器签发）

```json
{
  "contract_version": "1",
  "run_id": "uuid",
  "conversation_id": "uuid",
  "workspace_id": "uuid",
  "principal_id": "uuid",
  "mode": "office",
  "model_alias_id": "uuid",
  "tool_policy_id": "uuid",
  "skill_release_ids": ["uuid"],
  "sandbox_profile": "readonly-files",
  "resource_budget": {
    "max_wall_seconds": 120,
    "max_tool_calls": 20,
    "max_output_bytes": 10485760
  },
  "idempotency_key": "unique"
}
```

**边界**：上例中的标识由 API 从已认证身份、权限和用户选择校验后签发；Worker 仍验证 RunSpec 的来源、过期与任务租约。不在 RunSpec 中塞真实 Key 或未验证的任意宿主路径。

## 3. Pi Session、Conversation、Run 的关系

| 对象 | 生命周期 | 故障后如何恢复 |
|---|---|---|
| Conversation | 多轮、可归档 | 永久索引和权限 |
| Pi Session | 一条对话上下文树，可能 compact/fork | SessionManager 持久化与版本兼容 |
| Run | 一个执行请求，有终态 | DB 任务记录与租约 |
| Step | 一次模型生成、工具执行或验证 | 必须区分可重试/不可重试 |
| ToolInvocation | 一次带目标的能力调用 | 授权快照+幂等记录 |
| RunEvent | 追加有序事实流 | SSE 重连与 Replay |
| Artifact | 文件或结构化输出 | 内容哈希 + Run 关联 |

一个 Conversation 可有多个 Run；一个 Run 固定一组模型/Skill/工具权限。会话模型变更只影响新 Run。运行中的 Skill 更新不能热替换当前资源。

## 4. Pi SDK 集成边界

使用官方 `@earendil-works/pi-coding-agent` SDK 的 `createAgentSession`，提供受控 `cwd`、`sessionManager`、`resourceLoader`、`modelRuntime`、`tools`。每轮订阅 Pi 事件并映射到自定义 RunEvent Schema。Pi 版本锁定；上游 API 变更首先要跑编译、契约和恢复测试。

当前官方 SDK 支持自定义 `ResourceLoader`；默认 loader 可能扫描工作目录和 Pi 配置里的 Skills/Extensions。因此**生产环境不让任意用户仓库中的 `.pi/extensions` 自动成为执行代码**。敏感模型凭证通过可信网关提供，不能照搬本地开发的 `~/.pi/agent/auth.json` 当作共享云密钥库。

## 5. 状态机与转换守卫

```text
CREATED → QUEUED → PREPARING → RUNNING → VALIDATING → SUCCEEDED
                         │          │          └→ FAILED
                         │          ├→ WAITING_APPROVAL → RUNNING
                         │          ├→ WAITING_TOOL → RUNNING
                         │          ├→ CANCEL_REQUESTED → CANCELED
                         │          ├→ TIMED_OUT → FAILED
                         │          └→ FAILED
                         └→ FAILED
```

此图是逻辑草图，正式实现须对照 [AGENT_RUNTIME_ARCHITECTURE](../AGENT_RUNTIME_ARCHITECTURE.md) 已有数据库状态枚举进行 ADR/迁移，不能默默新增无法匹配 CHECK 约束的状态。DB 的终态仅允许一次 CAS 提交，`SUCCEEDED` 前必须 Validator 通过。

## 6. Pi 事件到 Web Event 的映射

| Pi 信号 | 内部事件 | 业务含义 |
|---|---|---|
| `message_update.text_delta` | `assistant.delta` | 仅展示中的文本增量 |
| `message_end` | `assistant.final` | 单条消息的规范化最终内容 |
| Tool start/end | `tool.started/finished` | 记录输入摘要、输出摘要、授权决策、时长 |
| `agent_settled` | `run.execution_settled` | Pi 当前自动工作完成；**不是最终 SUCCESS** |
| Error/abort | `run.diagnostic` / `run.cancel_requested` | 由业务状态机最终判定 |
| Validator pass/fail | `run.succeeded/failed` | 产物真实性证据 |

RPC 路径的 prompt ACK 仅表示接收命令，也不代表 Run 完成。事件必须带 run_id、seq、timestamp、scope 和 schema_version；SSE 断连补发按 Last-Event-ID/seq，不允许重复触发 Tool。

## 7. 规划与工具选择

Pi 自己做模型-工具循环；我们的 Tool Gateway 在每个动作**执行前**重新检查 Authorization。动态授权决策包含：
`principal, workspace, resource path/target, action, grant, risk, expiry, policy-version`。

- 读：`read/grep/find/ls`，限定授权 Workspace；P0。
- 写：`write/edit`，先在 Run Snapshot 生成新文件/Diff；受控；P1。
- Bash：高风险，必须独立沙箱，命令、网络、时间、文件与子进程限制；P1 严格放开。
- Git Push / Email Send：外部副作用，P2 起审批并使用幂等键。
- Tool Invocation 输出是**不可信数据**，不可以以“工具显示执行成功”为由绕开验证。

**避免工具白名单陷阱**：即使只给 Pi 显示 read 工具，若可访问的 Extension 运行任意代码，或同进程可直接用 OS File API，仍可能逃过 Tool Gateway。因此运行进程的 OS 权限必须受限制。

## 8. 暂停、取消、重试的难点

### 取消

取消请求写入 DB；Worker 收到后调用 Pi abort，停止后续工具；已经执行完成的外部操作不会自动回滚。UI 只有收到确认终态才能显示“已取消”。Pi 接收到 abort 不保证 shell 子进程立刻停止，必须配合进程组/cgroup 终止与超时。

### 工具重试

读取/幂等查询可有界重试；写文件需 staging 路径和固定输入版本；Git Push / 邮件发送等必须获得幂等确认，无法判断是否已提交时进入 `NEEDS_RECONCILIATION` 类错误分类，而不能直接再次执行。P0 不强求自动续跑一切副作用。

### Worker 崩溃

数据库 lease 过期后标记“未知是否完成”，检查 ToolInvocation 记录和 Artifact 校验，再决定是否重试。不能因为任务被重新领取就从头重放全部高危动作。

### Pi Session 恢复

会话持久化与运行任务恢复不是一回事：Session 恢复可能保留对话历史，但中断的工具执行未必可安全继续。Run 需要从最近确认过的 checkpoint 重建执行上下文，无法确认时失败并展示部分产物。

## 9. Session 长度、上下文压缩和模型切换

- 上下文压缩可能遗漏重要用户约束；重要任务验收指标、文件路径、授权范围存业务状态，而非仅留在聊天历史。
- 模型 context window 不可信时需要动态限制和完整性校验，输出截断不得判 SUCCESS。
- 新模型切换会影响 Pi Session 的上下文与 tool calling 行为，必须显示兼容性警告并将切换固定于新 Run。
- 用户对话历史可永久展示但过老的 Pi Session 可能无法恢复：保留只读历史并允许创建新会话/手动迁移摘要，不假装自动恢复成功。

## 10. 运行成本与资源预算

预算至少四个纬度：Wall Time、Model Tokens/调用次数、Tool Invocations、Output Bytes/磁盘。一个执行中止原因要能区分 budget exhausted、model output truncated、tool deadline、sandbox killed。Budget 上限由服务器与用户共同设定，用户不能超越服务端安全上限。

## 11. 真实 Pi 验收：别用 Mock 冒充

- AC-PI-01：锁定 Pi 包版本并实际编译 SDK，编译失败不得展示“Agent 已集成”。
- AC-PI-02：真实模型执行 read-only Office/Code 各一条，使用指定 Workspace cwd。
- AC-PI-03：Pi Session 两轮会话 + Docker 冷重启后上下文连续；并发两个 Run 不能写同一个 Session。
- AC-PI-04：错 Key / 上游 429 / 网络断开 / output truncation / tool 被拒绝被正确分类。
- AC-PI-05：SSE 重连不遗漏最终事件，也不重放 Tool。
- AC-PI-06：取消后没有继续发起新 Tool，已完成副作用清晰呈现。
- AC-PI-07：Skill 只有当前 Workspace 已安装的固定 Release 可被加载；未经授权项目 Extension 无法自动执行。
- AC-PI-08：Runner 崩溃/磁盘写满时不会显示假成功，重新领取不重复外部副作用。
- AC-PI-09：敏感 Key 不进入 Pi Session、trace、tool 环境和错误栈。
