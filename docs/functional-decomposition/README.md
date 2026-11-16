# Agent Console — 功能拆解与深度产品推演（v0.4）

> 状态：设计草案 / 2026-11-16。文档是目标设计，不是现有实现；没有真实运行的测试均为 NOT RUN。
>
> 上游基线：[自托管设计](../SELF_HOSTED_WORKSPACE_ARCHITECTURE.md)、[Pi Agent 集成](../PI_AGENT_INTEGRATION.md)、[PRD](../PRODUCT_PRD.md)、[安全模型](../SECURITY_MODEL.md)、[Registry](../SKILL_REGISTRY_SPEC.md)。本套文档在用户体验层细化这些约束，不替代正式的 API/DDL 迁移与安全验收。

## 一句话定位

自托管、Web-first、BYOK 的 Pi-powered AI Agent 工作台。面向办公与开发者任务：**配置模型 → 发起任务 → 在用户的隔离工作区执行 → 检查产物 → 将成功方法保存为 Skill → 在 Store 复用**。

## 设计取舍

1. **Better, not bigger**：首发只做一条可演示的 Office 工作流、一条可验证的 Code 工作流和一个 Skill 安装闭环；复杂 SaaS、付费市场、自动发布外部内容延后。
2. **单用户部署先行，多用户隔离要有真实证据**：UI 上的 user-id 不是授权凭证；尚无 per-run sandbox 时不得宣传多用户任意代码执行安全。
3. **用户侧集成创作功能**：Skill 编辑器与用户任务视图同一工作台；管理侧处理系统级策略、审核、违规与日志。
4. **Pi 是 Agent Engine，不是权限边界**：后台 Agent 可以规划、请求工具，但必须在 API/Tool Gateway + OS Sandbox 约束下执行。
5. **Model、Conversation、Run、Workspace、Skill Release、Installation 分别建模**。错误的归一化会造成重试重复副作用、错误下架和跨用户文件泄漏。
6. **完成态必须有证据**：UI 显示完成不等于实际测试通过；任务成功与功能上线都依赖客观校验。

## 文档导读

| 文件 | 回答的问题 | 固定的契约 |
|---|---|---|
| [01_USERS_AND_JOURNEYS.md](01_USERS_AND_JOURNEYS.md) | 谁在什么条件下做什么？全链路失败怎么办？ | JTBD、用户故事、功能分层 |
| [02_CLIENT_IA_AND_INTERACTIONS.md](02_CLIENT_IA_AND_INTERACTIONS.md) | Web UI 信息架构、进度、反馈、可访问性？ | 导航、页面状态、交互模式 |
| [03_MODEL_ONBOARDING.md](03_MODEL_ONBOARDING.md) | 自带模型、Key、Base URL、失败诊断、供应商兼容？ | Model Connection、隐私、路由 |
| [04_WORKSPACE_AND_ARTIFACTS.md](04_WORKSPACE_AND_ARTIFACTS.md) | /{user-id}/workspace 如何真正运行和存储？ | 目录、文件生命周期、隔离、恢复 |
| [05_PI_RUNTIME_AND_SESSIONS.md](05_PI_RUNTIME_AND_SESSIONS.md) | Pi Session、任务状态、工具、重试与上下文？ | RunSpec、Event、Session、审批 |
| [06_SKILL_CREATOR_AND_STORE.md](06_SKILL_CREATOR_AND_STORE.md) | Skill 从使用、创造到发布和下架？ | Release/Listing/Installation |
| [07_ROLES_ADMIN_AND_SECURITY.md](07_ROLES_ADMIN_AND_SECURITY.md) | 用户、管理、平台治理如何分层？ | RBAC/ABAC/Cap Grants、Audit |
| [08_DATA_API_CONTRACTS.md](08_DATA_API_CONTRACTS.md) | 具体实体、API、事件和事务如何协调？ | Schema 演进、幂等、SSE |
| [09_DOCKER_DEPLOY_AND_OPERATIONS.md](09_DOCKER_DEPLOY_AND_OPERATIONS.md) | Docker 部署、备份升级和离线能否可靠？ | Compose、安全默认、恢复 |
| [10_QUALITY_SECURITY_EVALS.md](10_QUALITY_SECURITY_EVALS.md) | 什么证据证明“能用且安全”？ | Fixtures、测试门禁、质量指标 |
| [11_ROADMAP_AND_BACKLOG.md](11_ROADMAP_AND_BACKLOG.md) | MVP 先做什么，怎么切 PR？ | P0-P3、依赖、Definition of Done |
| [12_DECISIONS_AND_RISKS.md](12_DECISIONS_AND_RISKS.md) | 哪些决定已冻结，哪些需要实验？ | ADR、风险、备选方案 |
| [13_FEATURE_MATRIX_AND_TRACEABILITY.md](13_FEATURE_MATRIX_AND_TRACEABILITY.md) | 功能到底有多少、由谁负责、何时验收？ | 79 项功能的角色/阶段/测试映射 |

## 核心场景（端到端验收线）

- **J-01 本地首次使用**：无模型 Key 的 Docker 冷启动 → 安全注册 → Web 配置本地/云端模型 → 首次真实 Pi 流式回复。
- **J-02 Office**：上传样本数据 → 运行 Agent → 生成有效办公文件 → 预览、下载、重启后仍存在。
- **J-03 Code**：导入测试仓库 → 只读诊断 → 受控生成 diff → 运行测试 → 失败与 NOT RUN 清晰区分。
- **J-04 Skill**：浏览内置 Skill → 查看权限/来源 → 安装 → Pi 正确加载固定版本 → 禁用后不能再触发。
- **J-05 故障**：错 Key、断网、超时、取消、重复请求、SSE 断线、沙箱崩溃、磁盘耗尽均可解释、可恢复。
- **J-06 隔离**：用户 A 不能通过 URL、API、软链接、脚本、Skill、Pi Session 访问用户 B 的文件和密钥。

## 证据分类与来源

- **FACT**：可在官方文档/代码中核实的现有产品行为。
- **DESIGN**：本项目建议，不能声称竞品已支持。
- **ASSUMPTION**：尚未用户验证，先记录产品假设。
- **OPEN**：必须做 PoC、许可证核查或安全测试后才能冻结。

官方参考：
- Pi SDK：https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/sdk.md
- Pi Skills：https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md
- Open WebUI Skills：https://docs.openwebui.com/features/workspace/skills/
- Open WebUI Quick Start：https://docs.openwebui.com/getting-started/quick-start/
- Agent Skills 规范：https://agentskills.io/specification

## 一致性检查

每个功能应至少写明：**用户/目标、触发前提、成功路径、异常/恢复、权限与数据、可观测性、客观验收、阶段归属**。所有特性编号以文档里的 `F-`/`NFR-`/`AC-` 形式跟踪；命名、状态、路径以既有架构文档为准，冲突时写 ADR 而不是悄悄修改。
