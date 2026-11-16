# Agent Console — Superpowers-style Phased Specs & Implementation Plans

> **状态：DESIGN / NOT IMPLEMENTED** · 2026-11-16 · 当前仓库架构提议，不表示已运行 Docker / Pi / DB / E2E。
>
> 产品：自托管、Docker Compose、Web BYOK（Provider / API Key / Base URL / Model ID）、Pi Agent 独立 Worker、服务端绑定 `/{user-id}/workspace`、内置 Skill Store（用户既消费又创造）。

## 从哪开始

1. **[MASTER_SPEC](specs/2026-11-16-master-product-architecture.md)**：产品目标、系统边界、核心不变量和覆盖矩阵；凡是阶段规范冲突，以它及 [原架构](../PI_AGENT_INTEGRATION.md) 的 ADR 为依据记录新决定。
2. **[WORKFLOW](WORKFLOW_AND_HANDOFF.md)**：按 Superpowers 方法执行：spec → review → plan → RED/GREEN/REFACTOR → 双层 review → evidence → PR → Gate。不是把“写计划”当成“完成代码”。
3. **[PHASES](PHASE_DEPENDENCIES_AND_GATES.md)**：六阶段依赖、停止条件、范围限制和出口准则。
4. **[MASTER PLAN](plans/2026-11-16-master-execution-plan.md)**：任务顺序、每阶段前置条件、原子任务索引和跨阶段集成门禁。
5. **阶段 spec + plan 成对阅读**：先看 `spec` 再执行 `plan`；没有合格 spec 不应开始写代码。
6. **[Evidence & TDD](VERIFICATION_AND_TEST_STRATEGY.md)**：真实测试证据、失败注入、人工审核与 Release Gate。
7. **[Agent handoff](AGENT_EXECUTION_PLAYBOOK.md)**：交给 Codex/Pi Agent 的任务执行指令与交接协议。

## 六个阶段

| 阶段 | Design Spec | Implementation Plan | 最小可验收成果 |
|---|---|---|---|
| P0A Foundation & BYOK | [Spec](specs/2026-11-16-p0a-bootstrap-models-spec.md) | [Plan](plans/2026-11-16-p0a-bootstrap-models-plan.md) | Compose 启动、初始化、模型连接诊断 |
| P0B Pi Runtime & Workspace | [Spec](specs/2026-11-16-p0b-pi-workspace-spec.md) | [Plan](plans/2026-11-16-p0b-pi-workspace-plan.md) | 真 Pi SDK Run、RunEvent、用户文件 |
| P0C Local Skill & E2E | [Spec](specs/2026-11-16-p0c-local-store-e2e-spec.md) | [Plan](plans/2026-11-16-p0c-local-store-e2e-plan.md) | Bundled Skill 安装到 Pi；全链路验收 |
| P1 Private Creator & Safe Writes | [Spec](specs/2026-11-16-p1-creator-sandbox-spec.md) | [Plan](plans/2026-11-16-p1-creator-sandbox-plan.md) | Draft/Release/测试/安全编辑 |
| P2 Org & Public Distribution | [Spec](specs/2026-11-16-p2-governance-registry-spec.md) | [Plan](plans/2026-11-16-p2-governance-registry-plan.md) | 多用户隔离与公共发布/下架/撤销 |
| P3 Ecosystem & Operations | [Spec](specs/2026-11-16-p3-ecosystem-spec.md) | [Plan](plans/2026-11-16-p3-ecosystem-plan.md) | API/CLI/连接器/质量和运维增强（按需求触发） |

## 主线约束

- 不采用 SaaS-first。P0 必须可以离线启动并浏览内置技能，连接远端模型是用户明确配置的行为。
- Pi SDK 是 Agent Engine，不是权限边界；未知 Skill/Extension 不得自动获得 shell、网络、文件系统权限。
- 目录路径由登录用户 UUID 与服务端 Workspace ACL 决定，绝不信任 URL、请求体或 Prompt 指定的 mount。
- `Skill / Release / Listing / Installation` 四对象独立，`Uninstall ≠ Unlist ≠ Revoke`。
- 真实模型测试、模拟测试、构建和手工验收分别标状态。**NOT RUN ≠ PASS**。
- 阶段不因“页面做好了”就通过，必须包含端到端证据与安全负例。

## 参考现有设计

- [原六份工程文档](../MVP_EXECUTION_PLAN.md)
- [自托管架构](../SELF_HOSTED_WORKSPACE_ARCHITECTURE.md)
- [Pi 集成](../PI_AGENT_INTEGRATION.md)
- [79 项功能追踪](../functional-decomposition/13_FEATURE_MATRIX_AND_TRACEABILITY.md)
- [深度功能分析](../functional-decomposition/README.md)

## Superpowers 方法参考

我们**借鉴方法，不直接复制其 Skill 实现或自动声称已安装**：
- https://github.com/obra/superpowers
- https://github.com/obra/superpowers/blob/main/skills/brainstorming/SKILL.md
- https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md
- https://github.com/obra/superpowers/blob/main/skills/test-driven-development/SKILL.md
- https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md
- https://github.com/obra/superpowers/blob/main/skills/verification-before-completion/SKILL.md

## 交付状态

此文档集本身的静态检查可以验收；任何工程代码/数据库/运行安全验收均应标 `NOT RUN`，直到出现确切命令、退出码、日志、镜像版本和 SHA 的可核查证据。
