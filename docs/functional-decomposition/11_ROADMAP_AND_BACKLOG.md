# 11 — MVP 任务拆解、优先级、依赖与可验证交付切片

> Draft v0.4 · 路线以**最小可用闭环**为序，不按市场界面数量或微服务数量排期。完整项目上位计划：[MVP_EXECUTION_PLAN](../MVP_EXECUTION_PLAN.md)、[Pi Integration](../PI_AGENT_INTEGRATION.md)。

## 1. 总体排序：先真 Agent、后丰富 Store

```text
Foundation (repo/CI/schemas)
   ↓
Self-hosted Docker + initial auth
   ↓
Model BYOK + real Pi worker + readonly workspace
   ↓
Verified Office/Code fixture + artifacts + task progress
   ↓
Bundled Skill browsing → install → Pi load (P0 complete)
   ↓
Private Skill create/test/version + controlled file writes (P1)
   ↓
Multi-user isolation + public/organization distribution (P2)
   ↓
CLI/SDK/MCP extensions / advanced quality & operations (P3)
```

**本质**：如果模型接入、Pi Runtime、文件系统和结果验证没有做好，就算 Store 有 300 张卡片也没有用户价值；而没有可复用 Skill，Agent 难以形成持续增长的能力资产。

## 2. 功能优先级矩阵

| 模块 | P0 需完成 | P1 需完成 | P2/P3 后续 |
|---|---|---|---|
| Docker/Setup | Compose 冷启、安全单次初始化、健康 | 备份恢复/更新指南 | 组织部署、HA |
| Models | BYOK、Base URL、Model ID、最小生成测试 | Tool capability probe 强化、连接共享 | 高级策略/自动路由 |
| Pi | SDK Worker、只读工具、Session、SSE、取消 | 受限写入/bash/恢复强化 | 多 Agent/并发优化 |
| Workspace | 单用户隔离文件树、上传、产物/持久 | Git worktree/Diff/可恢复写入 | 团队共享、配额 |
| Agent UI | 历史、实时进展、失败诊断 | Review Changes/Skill create | 多端、组织面板 |
| Skill Store | 内置离线列表、安装/禁用/调用 | 私人草稿/导入/测试/版本 | Public/Team Listing/审核/下架 |
| Admin | 实例健康/基本设置/禁危险工具 | 运行审计与紧急暂停 | 用户/团队/公共审核 |
| Security | 默认 loopback、密钥保护、ACL、只读执行 | 沙箱与攻击测试 | 多用户/供应链治理 |

**重要**：安全测试项目不属于“后期提升”而是每阶段阻断门禁。P0 只读操作也需确保它真正无法读取越权目录。

## 3. 推荐 PR 切片（每个都有验收证据）

| PR ID | 内容 | 依赖 | 最小验收 |
|---|---|---|---|
| A00 | Monorepo + lint/typecheck/unit/CI + gotchas | 无 | clean CI，失败会阻断 |
| A01 | Compose + DB migrations + setup/auth | A00 | 无模型可首启，单次 admin |
| A02 | ModelConnection DB/Vault + Web settings + Provider probe | A01 | 真实 Key/URL/ID 测试 |
| A03 | Pi package lock + TS SDK Worker + internal RunSpec | A02 | 真实 SDK build + 受控模型输出 |
| A04 | Run/Step/Event + SSE + crash/cancel | A03 | sequence/replay/terminal states |
| A05 | Workspace FS + 上传/下载/隔离只读 | A04 | traversal、软链接负测 |
| A06 | Office Fixture + Code read-only Fixture + Artifact Validator | A05 | 真实文件/仓库验证 |
| A07 | Bundled Registry + local installations + Pi Skill loader | A03/A05 | Skill 安装并在新 Run 生效 |
| A08 | Browser end-to-end + Restart + Security Gate | A01–A07 | P0 exit gate |
| B01 | Private Skill Draft/Editor/AI create/test | A07/A08 | 双输入评测、版本冲突 |
| B02 | Sandbox write/bash + Git Worktree/Diff + Review | A08 | 未审批不得应用 |
| B03 | Backup/Restore + Upgrade Pi contract tests | A08 | 恢复演练通过 |
| C01 | Multi-user ACL/OS isolation + org roles | B02 | 跨用户对抗通过 |
| C02 | Remote Registry/public Listing/Review/Unlist/Revoke | B01/C01 | 发布/下架/安全阻断完整链路 |

每个 PR 必须包含：变更说明、实际测试命令、成功/失败/NOT RUN、数据迁移、回滚步骤、gotchas。切片规模过大则继续拆分；禁止为了追求 PR 数量而让每个 PR 不能独立验证。

## 4. Phase 0 的可演示场景（签收条件）

最终用户在一台干净的本机运行 Compose、打开 Web、创建账号、输入模型连接、完成模型真实调用、上传一份文档、让 Pi 读取并生成可校验文件、下载结果、打开 Skill Store 安装内置 Skill、再运行一次使用该 Skill、重启确认持久化。

同时通过路径越权、错 Key、网络断开、SSE 重连、取消、磁盘异常至少基本故障矩阵。首发不要求远程市场或复杂 Pi bash；没有安全实现就只支持可信读/文件转换。

## 5. 后端开发依赖：必须先冻结的契约

1. `RunSpec`、SSE `RunEvent` 和状态转换 guard。
2. 用户 UUID → Workspace root → Pi cwd 的安全映射。
3. `ModelConnection` 的加密秘密保存与模型健康探测。
4. `SkillRelease` digest → Installation → Pi ResourceLoader。
5. Tool Gateway 的 `principal/resource/action/grant` 授权快照。
6. Artifact 的内容哈希、版本及校验状态。

这些是“交叉模块接口”，不冻结会造成前后端大量返工。需要 OpenAPI Schema、事件 JSON Schema 和共享 TypeScript 类型生成，而不是前后端各自口头约定。

## 6. 团队分工建议（单人+Codex 也适用）

- Product/UX：用户旅程、异常状态、可访问性、验收场景。
- Runtime：Pi Worker、模型连接、事件、任务恢复。
- Platform：Workspace、存储、沙箱、Tool Gateway。
- Registry：Skill 包、安装、版本、导入、测试。
- QA/Security：Fixture、跨用户/路径负测、CI、E2E。
- Infra：Compose、备份、升级/回滚、运行监控。

一个人使用 Agent 开发也应按模块划分 PR、测试和代码所有权；多个 Coding Agent 并行时先冻结接口契约，避免同时改同一数据库迁移/事件结构。

## 7. Definition of Done

每项功能“完成”须具备：功能代码、至少一个自动化正例、一个关键负例、真实依赖集成测试（如模型或 DB）、运行过程日志/Trace、用户可理解错误、文档更新、迁移与回滚、非绕过式 CI。

**禁止**仅因 UI 有按钮就宣称功能完成。若需要用户手动改 DB 才能安装 Skill、手动复制文件才运行 Pi，说明 E2E 尚未闭环。

## 8. 启动后风险排序

第一优先：认证/数据丢失/越权/原始文件被覆盖/密钥泄漏。
第二优先：模型连接失败无法诊断、Pi 任务挂死、SSE 丢终态、Skill 装载错版本。
第三优先：UI 微交互、排序推荐、组织报表、社交指标。

## 9. 回滚与开关

- 高风险新能力（shell、远端 Registry、团队分享）必须 feature flag，默认关闭直到验收通过。
- Pi 升级失败时可回滚镜像，但 Session/DB 的向后兼容性需验证；不要想当然允许读取所有新格式会话。
- 公开 Skill 有独立 Unlist/Revoke 开关，平台可按 digest 阻断恶意发布。
- 数据迁移遵守 expand/contract，可部署旧镜像并保持数据不丢失的最小读兼容。

## 10. 每阶段 Gate（不受需求催促而省略）

P0：冷部署 + BYOK + 真 Pi + Workspace + Offline Skill Store + E2E + 无 P0 安全漏洞。
P1：私人 Skill 创作/复用 + 受控写/测试 + 正负例评测。
P2：多用户安全验收 + 公共市场发布/下架与治理。
P3：扩展与运维优化，依据真实使用指标决定，不按假想功能堆叠。
