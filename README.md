# Agent Console — Pi-powered self-hosted Agent + Skill Store

> Draft v0.3｜2026-11-16｜**设计文档，不代表产品已实现或测试已运行**

## 产品目标

一个面向办公用户和开发者的 Agent Workspace：用户可以完成任务，也可以把有效任务沉淀为 Skill，经历创建 → 测试 → 版本化发布 → 私人/团队/公共分发 → 维护/下架；平台对执行安全和公共生态进行治理。

## 推荐阅读顺序与职责（六份基础文档 + 两份专题）

| # | 文档 | 决定什么 | 主要产出 |
| --- | --- | --- | --- |
| 1 | [PRODUCT_PRD](docs/PRODUCT_PRD.md) | 用户与功能范围 | JTBD、Story、UI IA、验收 |
| 2 | [SECURITY_MODEL](docs/SECURITY_MODEL.md) | 什么操作允许 | Threat Model、RBAC/ABAC/Grants |
| 3 | [DATA_MODEL](docs/DATA_MODEL.md) | 数据对象和事务不变量 | ER、基线 DDL、索引与迁移 |
| 4 | [AGENT_RUNTIME_ARCHITECTURE](docs/AGENT_RUNTIME_ARCHITECTURE.md) | Agent 如何可靠执行 | 状态机、SSE、Queue、Tool Gateway |
| 5 | [SKILL_REGISTRY_SPEC](docs/SKILL_REGISTRY_SPEC.md) | Skill 如何演化与流通 | 包格式、Release/Listing、分发与下架 |
| 6 | [MVP_EXECUTION_PLAN](docs/MVP_EXECUTION_PLAN.md) | 开发顺序与何时算完成 | P0–P3、任务依赖、CI Gate |

**阅读顺序不等于写作顺序**：先明确 PRD，再同步冻结 Security / Data / Runtime / Registry 的共享契约，最后执行 MVP 计划。

## 六个跨文档不变量

1. 创作者和消费者是**同一个用户**在不同场景的行为；普通用户可以创建、测试、管理自己的 Skill。
2. `Skill`、`SkillRelease`、`SkillListing`、`SkillInstallation` 是不同对象，不能合并成一张表。
3. 安装 Skill **不等于**授予其工具权限；Policy Engine 是权威授权来源。
4. `unlist`（停止新分发）和 `revoke`（停止执行受影响版本）完全不同。
5. Agent 的任务进展是持久事件流，SSE 支持重连；不能把聊天 token 流等同任务状态。
6. 未实际执行的测试必须标为 `NOT_RUN`；不得把模型声称成功当作验收结果。

## 文档状态与后续事项

- 当前是 `Draft v0.1`：含 API/DDL 草案、状态机与测试矩阵；尚未运行工程测试。
- 创建真实仓库时，请同步添加 `docs/gotchas.md`，并为未定决策补充 `docs/adr/`。
- 参考基线：[Agent Skills](https://agentskills.io/specification)、[MCP 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28)、[OWASP GenAI](https://genai.owasp.org/llm-top-10/)。

## 验证本套 Markdown 文件

```bash
python3 scripts/validate_docs.py
```

此脚本只验证文档存在性、内部 Markdown 链接与代码围栏平衡；**不是 API、数据库或安全实现的测试**。

## 新增：自托管部署与用户工作区（优先阅读）
本项目的首要交付形态为**用户本地 Docker Compose 部署的 Web Agent**：首次在 Web 配置模型提供商、API Key、Base URL 和 Model ID；每位用户的 Agent 通过受控执行环境访问逻辑目录 `/{user-id}/workspace`；内置离线可用的 Skill Store 与我的 Skill。

详见 **[SELF_HOSTED_WORKSPACE_ARCHITECTURE.md](docs/SELF_HOSTED_WORKSPACE_ARCHITECTURE.md)**（Draft v0.2）。本文件是架构规范，**不是已经完成部署或通过 E2E 的证明**。建议在阅读六份原设计文档前先阅读该文件。

## 内置引擎决策：Pi Agent（Draft v0.3）

**正式确定使用 Pi 作为内置 Agent Engine**，而不是独立开发 LLM Agent loop。新增 [PI_AGENT_INTEGRATION.md](docs/PI_AGENT_INTEGRATION.md)，规定独立 Node/TypeScript Pi Worker、SDK / RPC 适配、Model Gateway、Pi Session、受控 Skill ResourceLoader、Tool Gateway、安全沙箱以及 Pi 专项 E2E。

Pi 上游已迁移到 [earendil-works/pi](https://github.com/earendil-works/pi)，官方包名为 `@earendil-works/pi-coding-agent`（需发行版锁定和实际验证）。**Pi 本身不提供可信的文件/进程/网络权限隔离**；隔离、审批、密钥控制仍由本项目提供。原六份文档保留业务契约；新增两份实施专题：[自托管架构](docs/SELF_HOSTED_WORKSPACE_ARCHITECTURE.md)、[Pi 集成](docs/PI_AGENT_INTEGRATION.md)。

仍为设计阶段：Pi SDK 构建、Docker 启动、模型调用、沙箱和 E2E 全部 **NOT RUN**。

## 功能深度推演与实施设计（v0.4）

在原有 6 份工程基础设计、自托管专题和 Pi 集成专题之外，新增 **[功能拆解系列文档](docs/functional-decomposition/README.md)**。覆盖用户画像/端到端旅程、Web IA、BYOK 模型连接、用户工作区、Pi Runtime、Skill Store 创作/发布/下架、管理员与安全、API 与数据一致性、Docker 运维、对抗评测、PR Backlog、ADR 风险，以及 **79 项功能追踪矩阵**和 Open WebUI × Pi 的参考实现对照。

**阅读顺序**：先看 [功能目录](docs/functional-decomposition/README.md)，再看 [13 功能矩阵](docs/functional-decomposition/13_FEATURE_MATRIX_AND_TRACEABILITY.md)，根据工作项阅读各专题。完整设计不代表已实现；Docker、Pi SDK、DB Migration 和真实 E2E 仍为 **NOT RUN**。

## Superpowers-style 六阶段 Spec / Plan（v0.5）

已规划 **P0A → P0B → P0C → P1 → P2 → P3** 的配对规格与实施计划，共 **50 个可测试任务**，并提供开发协议、RED/GREEN/REFACTOR 证据模板、Agent 交接、阶段 Gate、风险与验证脚本。

- [系列文档入口](docs/superpowers/README.md)
- [Master Product Spec](docs/superpowers/specs/2026-11-16-master-product-architecture.md)
- [Master Implementation Plan](docs/superpowers/plans/2026-11-16-master-execution-plan.md)
- [Superpowers-style workflow](docs/superpowers/WORKFLOW_AND_HANDOFF.md)
- [Phase gates](docs/superpowers/PHASE_DEPENDENCIES_AND_GATES.md)
- [Agent instructions](AGENTS.md)

计划里的路径、测试和接口均为**目标工程设计**，不代表已存在。真实 Pi SDK、模型、Docker、E2E、安全隔离和迁移验收仍为 **NOT RUN**。

文档结构检查（在有本地仓库的环境中执行）：

```bash
python3 scripts/validate_docs.py
python3 scripts/validate_phased_docs.py
```
