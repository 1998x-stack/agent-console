# PI_AGENT_INTEGRATION — Pi 作为内置 Agent Engine 的架构设计

> Draft v0.3 · 2026-11-16 · **设计规范，并非运行成功的证明**。
>
> 决策：Agent Console 默认且唯一内置的通用 Agent Harness 采用 **Pi**；Web 应用拥有身份、工作区、密钥、权限、Skill 发布和审计，Pi 负责模型交互与工具调用循环。Office 与 Code 使用同一 Pi 内核、不同可用 Tool/Skill 和执行策略。
>
> 依赖：[自托管与工作区](SELF_HOSTED_WORKSPACE_ARCHITECTURE.md)｜[Runtime](AGENT_RUNTIME_ARCHITECTURE.md)｜[Registry](SKILL_REGISTRY_SPEC.md)｜[安全](SECURITY_MODEL.md)｜[数据](DATA_MODEL.md)｜[执行计划](MVP_EXECUTION_PLAN.md)。

## 1. 官方版本与范围核对（2026-11-16）

官方仓库 `https://github.com/badlogic/pi-mono` 当前重定向到 `https://github.com/earendil-works/pi`；官方 npm 安装标识已显示 `@earendil-works/pi-coding-agent`，需要以**选定提交/tag 和对应实际 npm 包**验证锁文件；许多第三方文章使用旧 `@mariozechner/pi-coding-agent`，不可在新代码中假定它与当前 API 等价。

| Pi 组件 | 用途 | Agent Console 采用方式 |
|---|---|---|
| `pi-ai` | 多模型抽象、流式事件与供应商适配 | 通过 Pi coding-agent 的模型接口复用，不另写 Agent LLM loop |
| `pi-agent-core` | Agent loop、状态与工具调用 | 优先间接由 coding-agent 使用 |
| `pi-coding-agent` | SDK Session、Tools、ResourceLoader、Events、Skills | **首选 Node TypeScript Worker 内嵌 SDK** |
| `pi --mode rpc` | JSONL 子进程双向通信 | **备选/集成回归测试路径**，Python/其它语言直连可用 |
| Pi Skills | Agent Skills 标准；按需载入 `SKILL.md` | 由我们的 Skill Registry 管理安装，注入显式受信任 Skill 清单 |
| Pi Extensions | TypeScript 运行时扩展、自定义 Tools、MCP | 仅经过平台审核的内置扩展，不能将市场 Skill 当 extension 自动运行 |
| Pi MCP | 官方现支持内置 MCP 扩展 | P2 按组织策略显式接入，SDK 需按文档加载/绑定扩展 |

**关键事实**：Pi 不自带可作为可信边界的权限系统；Pi 的内置 `read`、`write`、`edit`、`bash` 及 extensions 在其进程 OS 权限下运行。不能把“工具白名单 UI”当作沙箱。官方建议使用容器/沙箱隔离，Pi 本身也支持 SDK/RPC；MCP 已成为官方内置扩展能力，不能引用旧版“No MCP”论述。

## 2. 明确采用的集成方式

### 方案 A：Node.js Pi Worker + TypeScript SDK（**推荐上线架构**）

- 保留既有 Next.js Web 与 FastAPI 业务 API（身份、模型设置、Registry、审计、文件操作）；新增独立 `pi-worker` 服务，由 Node.js 运行 Pi SDK。
- API 创建任务时，经服务内部已认证的队列/私网接口下发**服务端签发 RunSpec**；Worker 不接受浏览器直连或用户指定路径。
- 每个并发 Run 使用独立 Pi `AgentSession`，拥有明确 `cwd`、`SessionManager`、`ResourceLoader`、Tool allowlist、Budget，调用完成或取消必须 `dispose()`。
- Worker 把 Pi SDK 事件转换为**我们的稳定事件协议**，发给 API 事件存储/SSE；Web 不能依赖 Pi 的原始 TS 类型。
- 为隔离，Pi Worker 进程自身也应放进独立的受控执行环境或在其下启动隔离 per-run process。**仅仅把 SDK 放进 API 的同一 Node 进程无法建立安全边界**。

### 方案 B：`pi --mode rpc` 子进程（**可落地的 P0 PoC / 调试回退**）

- API 或 Node Adapter 启动 Pi RPC 子进程，stdin/stdout 严格逐 LF 分隔 JSONL，解析响应和流式事件。
- 接口保持与方案 A 一致的 `RunSpec → UnifiedEvent`；后续可切换 SDK 而无需修改前端和数据库。
- RPC 模式允许双向控制，`prompt` 的成功回执只意味着被接受，**不是任务完成**；以 `agent_settled` 作为 Pi 自动工作完成观察点，然后再由我们做结果验证与终态提交。
- 进程退出/断连时要能区分 Agent 失败、调用超时、取消；不能把“RPC 命令已返回”显示为成功。

| 选项 | 优势 | 风险/缺点 | 结论 |
|---|---|---|---|
| TypeScript SDK | 类型安全、直接控制 Session、Tools、Skills 和事件 | 需要 Node Worker，与 Python API 多语言通信 | **正式推荐** |
| RPC 子进程 | 进程边界清晰，跨语言接入快 | JSONL framing、错误/取消/恢复与事件关联复杂 | P0 互操作验证、降级 |
| 自研 Agent loop | 自由度最大 | 重复实现 Pi 的核心能力和维护升级成本 | 不做 |
| 将 Pi 直接挂在 Web/API 主容器 | 最快 demo | OS 权限与密钥暴露，难以隔离 | 禁止用于不可信代码执行 |

## 3. 逻辑部署图

```text
Browser  :3000
    │  HTTPS / session + CSRF
    ▼
Web (Next.js) ──→ API (FastAPI)
                   ├─ Authentication / Workspace ACL / Run & Approval DB
                   ├─ Model Provider Vault / Proxy (API Key、Base URL、Model ID)
                   ├─ Skill Registry / Skill Version / Installation
                   └─ Run queue / event stream (SSE)
                            │ authenticated internal channel
                            ▼
                        Pi Runner Manager
                            │ verifies signed RunSpec, limits concurrency
                            ▼
                       Pi Agent Worker (Node/SDK)
                            ├─ Pi AgentSession + SessionManager
                            ├─ bounded ResourceLoader (only pinned Skills)
                            ├─ audited tool adapters + policies
                            ├─ per-run mounted authorized workspace
                            └─ Model proxy with short-lived run credential
                                       │
                                       ▼
                              External LLM / local Ollama
```

**最小可测试构成**：Web + API + PostgreSQL + Pi Worker + 可信工具环境。动态沙箱启动需要单独的隔离组件/守护进程；不能向 Web/API 或任意 Skill 注入高权限 Docker Socket。

## 4. User / Workspace / Pi Session 映射

| 业务对象 | 唯一标识 | 关系与持久化 |
|---|---|---|
| User | `users.id` (UUID) | 由登录会话推导，不接受自由指定的 user ID |
| Workspace | `workspaces.id` | 归属于 User/Org；以服务端 ACL 判断文件访问 |
| Conversation | `agent_conversations.id` | 一个用户在某 Workspace 中的长期会话 |
| Pi Session | `pi_session_refs` | 对应 Conversation 的 Pi JSONL 树/持久状态引用 |
| Agent Run | `agent_runs.id` | 单次 prompt / step 调度与审计，记录运行终态 |
| Skill Installation | `skill_installations` | 关联 Workspace 和固定不可变 Skill Release |
| Model Connection | `model_connections` | BYOK 配置、范围和加密密钥引用，不放在 Pi Session 内 |

用户要求的逻辑目录严格保持 `/{user-id}/workspace`；在宿主机映射 `[DATA_DIR]/users/[internal-uuid]/workspace`，Pi Session 的 `cwd` 必须由 Runner 服务端从已授权 Workspace 映射生成，不从 HTTP 参数、提示词或 Git 项目配置读取。Pi 会按 `cwd` 发现目录中的资源；**首发必须控制自动读取 `AGENTS.md`、`.pi/extensions` 等第三方项目资源的信任级别**。

Session 生命周期：
1. 首次会话创建唯一 Pi Session，按工作空间与登录身份关联，并在持久数据卷保存受限访问的上下文。
2. 新消息必须在正确的 Pi Session 上继续，保留原模型上下文、工具输出和 compaction；不要简单手工赋值 `session.agent.state.messages`。
3. 任务取消：转发 `abort()` 并等待空闲，再释放资源；客户端断开 SSE 不等于取消任务。
4. Session 重载/恢复：优先使用官方 `SessionManager` 的持久化方式，启动时验证文件属主、运行锁与恢复版本；不能让两个 Worker 同时写同一个 Pi Session。
5. 内存中的 session.subscribe() 只对当前 Session 生效，运行替换/分支后重新订阅；长期审计由我们的 DB 事件日志保存。

**并发约束**：同一 Conversation 一次只允许一个活跃执行；不同 Conversation 允许并行但隔离。任务重试不能重放已经产生外部副作用的工具调用。

## 5. Model Connection → Pi 的映射（BYOK）

Web 保持 `Provider / Protocol / Base URL / API Key / Model ID` 的配置体验，由 Server Model Gateway 进行校验与存储；Pi 内的 `ModelRuntime` 或受控 `models.json` 注入选定模型，不让用户直接在公共 Worker 的 `~/.pi` 写配置。

- **原生支持**：Pi 已有的供应商优先走内置接口。OpenAI-compatible、Ollama、vLLM、LM Studio 等通过兼容协议配置 `models.json` 或 SDK Model Runtime。
- **密钥保管**：宿主 Vault 加密持久化密钥；Pi Runner 只拿到每次运行授权、短时效、范围有限的 **模型代理凭证**；最终 API Key 不写入 Pi 工作区、日志、Skill 包或长驻环境变量。
- **本地模型**：用户 Web 填 `http://host.docker.internal:11434/v1` 等端点；Linux host-gateway 需要 Compose 明确配置，不能假设 Docker 容器内 `localhost` 指宿主机。
- **模型发现**：`/models` 不存在时允许用户手工添加 Model ID；最小 completion smoke + 独立 tool-calling smoke。Local model 不具备可靠 tools 时展示“仅聊天/受限工具”兼容性。
- **SSRF 安全**：Provider Base URL 限制协议、DNS 解析、重定向和不可访问目标；本地/LAN 例外仅管理员明确授权，避免通过自由 Base URL 读取宿主/内网元数据。
- **Pi 配置安全**：Pi 的 `models.json` 可支持环境变量、甚至命令型密钥解析。**不允许用户提交任意 `!command` 作为 credential provider**，只由受信任管理逻辑生成完整配置或使用 SDK 自定义模型输入。

## 6. Pi SDK 集成最小验证代码（示意：需按锁定版本实际编译）

以下沿用官方 SDK 的 `createAgentSession`/`SessionManager`/`subscribe`/`dispose` 用法，仅演示**读工具和 cwd 绑定**。不是完整的安全沙箱实现。

```ts
import {
  createAgentSession,
  SessionManager,
} from "@earendil-works/pi-coding-agent";

async function runPiReadOnly(cwd: string, prompt: string) {
  const { session } = await createAgentSession({
    cwd,                                  // 来自服务端已校验的工作区
    tools: ["read", "grep", "find", "ls"], // P0 只读
    sessionManager: SessionManager.inMemory(cwd),
  });

  const unsubscribe = session.subscribe((event) => {
    if (event.type === "message_update"
      && event.assistantMessageEvent.type === "text_delta") {
      // 转成内部 RunEvent；实际实现需要关联 runId、序号和持久化
      process.stdout.write(event.assistantMessageEvent.delta);
    }
  });

  try {
    await session.prompt(prompt);
  } finally {
    unsubscribe();
    session.dispose();
  }
}
```

**注意**：若使用默认 `ResourceLoader` 会自动发现项目 Skills / Extensions；上述代码的只读工具选择**不构成安全边界**。产品实现应显式提供受控 `ResourceLoader`，并在独立 sandbox 执行，方可处理不可信仓库/Skill。SDK API 细节必须在指定 Pi release + 锁文件上实测。

## 7. Skill Store → Pi ResourceLoader

所有安装与审核仍由我们自己的 Registry 管理，Pi 负责按需加载。保持 `Skill / Release / Listing / Installation` 四层：

```text
Skill Store: Install selected digest
  → Registry verify manifest & content SHA-256
  → Installation(workspaceId, releaseId, enabled)
  → Pi Runner compile allowed Skill list for Run
  → ResourceLoader receives exact authorized skills
  → Pi advertises name + description (progressive disclosure)
  → Pi reads SKILL.md only when needed
  → Tool Gateway enforces capabilities independently
```

- **安全策略**：只把已启用、兼容、版本锁定的 Skill 注入本次 Pi Session；不依赖 Pi 从当前目录递归扫描一切可见 Skill。
- **版本更新**：Registry 发布不可变 Release；用户批准升级后，新 Run 使用新版本，已有 Run 继续旧 digest；运行记录必须记实际版本与哈希。
- **资源路径**：安装 Skill 作为只读版本目录呈现；Skill 自身写入放工作空间或沙箱临时目录。防 ZIP slip、符号链接逃逸、脚本依赖投毒。
- **运行调用**：Pi 的 Agent Skills 规则是先注入 name/description，匹配任务再按需读取全文；`/skill:name` 可显式调用。自动触发质量由我们的评测测量，不能假设总能选对。
- **禁止混淆**：`Skill` 是数据与说明；`Extension` 是能在 Pi 进程中执行的 TS 代码；`MCP Server` 是工具服务。不可把用户上传 Skill 包直接注册为 Pi Extension。
- **技能生效时间**：某个 Session 内安装新 Skill 后，应显式 reload 或创建新 Session / Run，并给 Web 用户明确提示，不默默修改正在执行的资源集合。
- **第三方来源**：本地/社区 Skill 可用但默认禁用危险工具。内置可信 Skill 可以专设更宽策略但也不绕过授权。

## 8. Office/Code 模式与 Tool Gateway

| 模式 | Pi Tool | Worker 能力 | 审批规则 |
|---|---|---|---|
| Office read | `read`/`grep`/`find`/`ls` | 仅授权工作区文档 | P0 允许 |
| Office write | 受控 `write`/`edit` 或文档专用 Tool | 预览、版本/备份、原子提交 | P0 受控，覆盖原文件时提示 |
| Code read | `read`/`grep`/`find`/`ls` | 只读测试仓库或 worktree | P0 允许 |
| Code edit | 受控 `write`/`edit` | Git worktree，生成 diff | P1 可恢复写入 |
| Code shell | `bash` 包装器 | sandbox，超时/网络/资源限制 | P1 起，按命令风险 |
| External actions | 自定义 extensions/tools / MCP | GitHub PR、邮件发送等 | 明确受众/目标的动作级人工审批 |

**Tool Gateway 是操作前决策点**（调用主体、路径、目标、能力授权、idempotency key、审计），不能只依赖 Pi 的 Prompt、内置确认弹窗或 Extension `tool_call` 事件。Pi 执行器的容器或 microVM 仍须提供独立 OS 级约束。对 Office 文档处理优先使用独立受控文件 Tool，不允许任意项目脚本默认执行。

## 9. 统一事件流与 Web 任务进展

Pi SDK 的 `session.subscribe` 可以提供 `message_update`、`message_end`、Tool execution、retry、compaction 等事件；`agent_end` 不是最终可结算事件，`agent_settled` 表示 Pi 不再自动继续，之后仍需我们的结果验证。

| Pi Signal | 我们的事件 | Web 表示 |
|---|---|---|
| 用户提交 prompt 成功 | `run.accepted` | 已排队 |
| `message_update.text_delta` | `assistant.delta` | 流式正文 |
| Tool start/progress/end | `tool.started` / `tool.progress` / `tool.finished` | 步骤进度 |
| `message_end` | `assistant.message_final` | 校正最终回答 |
| model retry/compaction | `run.diagnostic` | 重试/上下文整理 |
| `agent_settled` | `run.execution_settled` | 执行完成，进入验证 |
| Validator passed | `run.succeeded` | 任务成功、产物可查看 |
| 用户取消/timeout/runner crash | `run.canceled` / `run.failed` | 明确错误和恢复入口 |

- 所有事件包含 `run_id`、`sequence`、`timestamp`、`type`、`payload`；持久化并支持 `Last-Event-ID` 重连补发、去重与顺序校验。
- **控制平面唯一权威**是数据库里的 Run 状态。Pi event 是运行信号，不直接覆盖业务终态或审批。
- 接收 Web 的 `cancel`、`approve` 后，API 校验用户与目标操作授权，再通知 Pi Worker。SSE 断开不默认取消执行。
- 正常终止需要区分“模型停下”“验证失败”“用户中断”“Runner 崩溃”“超时”与“工具被拒绝”，不允许假绿灯。

## 10. 数据模型增量（逻辑与 DDL 要求）

补充数据库 `agent_conversations`、`pi_session_refs`、`pi_runtime_profiles`（或同等表/列），建议字段如下：

| 表 | 主要字段 | 不变量 |
|---|---|---|
| `agent_conversations` | id, workspace_id, created_by_user_id, title, status | ACL 绑定 Workspace |
| `pi_session_refs` | id, conversation_id, session_store_ref, pi_package_version, format_version, revision, updated_at | 唯一活动 writer；仅服务端可指定存储位置 |
| `pi_runtime_profiles` | id, workspace_id, mode, allowed_tool_names, sandbox_profile, default_model_alias_id | Profile 策略不接受前端扩大 |
| `agent_run_resources` | run_id, release_id, content_sha256, model_alias_id, sandbox_image_digest | 记录每次运行的真实依赖，便于复现 |

对现有 `agent_runs` 增加 `conversation_id`、`engine = pi`、`pi_session_ref_id`、`workspace_snapshot_ref`、`cancellation_reason` 等字段时，先做前后兼容迁移，不在旧 DDL 上直接假定字段已存在。Pi 的 JSONL Session 有独立上下文树，DB 保存索引与运行审计；不可用我们自己的消息表写入一半上下文绕过 Pi SessionManager。

## 11. 实际工程切片：先跑通最小闭环

### Phase 0A（Pi PoC）— 在受控测试机器上验真实 SDK 行为

1. 选定一个 Pi release/tag 与 Node 版本，锁 npm 依赖，记录许可证与 commit；禁止使用 `latest` 漂移。
2. 创建 `pi-worker`，在隔离测试目录使用只读工具调用一个配置好的 OpenAI-compatible 或本地模型。
3. 验证 `prompt`、`message_update`、`message_end`、`agent_settled`、`abort/dispose`、Token 限额和错误恢复。
4. 使用 SessionManager 验证连续两轮、Pi Session 文件保存、重启续聊；断连不丢会话。
5. 验证显式 Skills 注入与版本切换，禁止自动加载测试目录里的恶意 `.pi/extensions`。
6. 补上一个用 `pi --mode rpc` 的兼容性 smoke，核对 JSONL framing 与完成判据。
7. 验证真实容器挂载只允许用户工作区、Provider key 不出现在日志/工具环境/Skill。
8. 测试失败、取消、重试、隔离攻击均有可复现的错误/恢复路径。

### Phase 0B（Docker Web E2E）

`docker compose up -d --build` → 初始化账户 → Web 添加 Provider（Base URL/Key/Model ID）→ 测试连接 → Pi Worker 完成一轮 Office 只读/文件任务与 Code 仓库只读任务 → `/{user-id}/workspace` 中看到产物 → 打开 Skill Store 并调用内置 Skill → 重启保持持久化。

### Phase 1

完善 per-run sandbox（含 bash），实现 Code 修改 + Diff + 回归测试、私人 Skill 创建/导入/测试/锁版本，并覆盖并发、权限、恢复与密钥代理；**未通过隔离门禁不得开放第三方任意代码**。

### Phase 2

公共 Registry 与发布/下架治理，MCP 工具适配、组织管理、多用户执行隔离，完成安全评测与兼容性矩阵。

### 客观验收指标

| ID | 断言 | 证据 |
|---|---|---|
| PI-01 | Pi 依赖固定版本，SDK 示例真实编译 | lockfile + Node test output |
| PI-02 | 指定 LLM Provider 经 Web 配置可运行 | Provider connection + Pi run trace |
| PI-03 | Pi Run 使用已授权 `cwd`，不能跨用户访问 | filesystem negative E2E |
| PI-04 | 连续对话/重启恢复 Pi Session | session resume test |
| PI-05 | Pi event 规范化且 run 可重连 | SSE replay / dedupe test |
| PI-06 | Skill 版本锁定且只加载已安装能力 | pinned digest + loader test |
| PI-07 | 执行超时/取消/崩溃不会错误标为成功 | failure-injection suite |
| PI-08 | 没有明文 API Key、非授权文件或高权限 socket 暴露 | secrets & mount inspection |
| PI-09 | Office/Code 受控工具能完成预设 Fixture | output validation + code tests |
| PI-10 | 原生 MCP（P2）按策略连接、不越权调用 | MCP permission matrix |

所有没有实际运行的验收都写 **NOT RUN**。本 PR 仅更新架构文档，没有构建 Worker、运行 Pi、配置模型或启动 Docker。

## 12. ADR / 风险及迁移

- **ADR-PI-001** 使用官方 Pi 作为内置 Agent Engine，不独立实现 Agent loop；Node SDK Worker 与 Python 业务 API 分离。
- **ADR-PI-002** UI/API 依赖我们自己的 Run/Event/Skill contracts，不暴露 SDK 或 RPC 私有事件结构。
- **ADR-PI-003** Pi 默认的代码工具和 extensions 不能直接运行在 Web/API 进程或跨用户共享权限域。
- **ADR-PI-004** Provider Key 由 Host Vault/Model Gateway 持有，Pi 最多获取有限期的模型代理凭证。
- **ADR-PI-005** Skill Store 交给 Registry；Pi ResourceLoader 只能装载已授权的 Release，且 Tool 权限须二次验证。
- **ADR-PI-006** Session 持久化遵循官方 SessionManager；业务 Run 状态与可重放审计仍由 PostgreSQL 负责。
- **ADR-PI-007** Pi 包名/版本存在上游变更风险，使用真实 release/tag + npm lockfile + contract tests；升级必须经过 SDK/ResourceLoader/API 快照回归。

待确认：Pi SDK 许可/依赖传染检查、Node 的锁定发行版、真实模型网关 token 注入 API、授权的 Skill ResourceLoader 完全隔离测试、Per-run sandboxes 的技术选型与恢复语义。

## 官方参考（2026-11-16）

1. Pi 项目与最新包名：https://github.com/earendil-works/pi
2. SDK 文档：https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/sdk.md
3. SDK 示例：https://github.com/earendil-works/pi/tree/main/packages/coding-agent/examples/sdk
4. RPC / CLI Integration：https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/cli-integration.md
5. Skills 及 Agent Skills 格式：https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md
6. Models：https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/models.md
7. Extensions 及权限告警：https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/extensions.md
8. Isolation / Containerization：https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/containerization.md
