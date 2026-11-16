# 12 — 架构决策记录、替代方案、风险登记与尚需验证的问题

> Draft v0.4 · 本文件主动记录可能推翻当前设计的证据。**已决定**不等于**已实测**。与 [Pi Integration](../PI_AGENT_INTEGRATION.md)、[QA](10_QUALITY_SECURITY_EVALS.md) 和 [Roadmap](11_ROADMAP_AND_BACKLOG.md) 共同使用。

## 1. 本项目最容易犯的六个架构错误

1. **把 Pi 当作操作系统沙箱**：Pi 的 Tool 选择和 Extension 机制不能提供进程安全边界。
2. **把本地 Workspace 等同 Web 路由**：`/{user-id}/workspace` 必须有真实授权映射和运行时隔离。
3. **把 Skill 安装等同执行授权**：恶意 `SKILL.md` 与脚本可以诱导 Tool 调用，应该独立能力授权。
4. **把“模型连上了”当“Agent 能用了”**：Tool capability、输出完整性、兼容流式协议均需实际测试。
5. **把发布/删除/下架混成一个状态**：损坏已有用户安装、版本历史和权益。
6. **从第一天做多租户 SaaS**：引入身份、隔离、运营和公共治理负担，反而无法证明本地自托管核心价值。

## 2. 已冻结的设计决策（待真实工程验证）

| ADR | 决策 | 为什么 | 否定它需要何种证据 |
|---|---|---|---|
| ADR-001 | Docker Compose local-first | 用户明确希望自己本地部署 | 大量目标用户装机失败且另一种打包明显改善 |
| ADR-002 | Web BYOK Base URL/API Key/Model ID | 兼容远端/本地模型，降低配置文件门槛 | Pi 所选版本无法可靠接入，必须改适配层 |
| ADR-003 | Pi SDK 为内置 Agent Engine | 复用会话/工具/Skills/模型适配 | 锁定版本不可用或许可证/安全风险不可接受 |
| ADR-004 | Node Pi Worker + FastAPI 控制平面 | 保持 Pi TS SDK 与现有业务架构边界 | 实际测试表明跨语言开销严重破坏可靠性 |
| ADR-005 | `/{user-id}/workspace` 是逻辑路径 | 保证按身份映射并可持久化 | 用户明确要求某一容器物理路径及其约束 |
| ADR-006 | 个人/本地 Skill Store 首发 | 离线有价值，不依赖公共注册表 | 无法提供足够内置技能完成首批场景 |
| ADR-007 | Skill Creator 在 Client 内 | 用户消费/生产身份重合 | 实际用户研究要求高级功能另独立 |
| ADR-008 | Task 成功依赖 Validator | 减少假成功与数据污染 | 不应被取消；只能改验证器细节 |
| ADR-009 | 高风险 Tool 需 Gateway + Sandbox | 防提示注入/越权/扩展脚本 | 不应降低；有更严格替代可考虑 |
| ADR-010 | 先 single-user，再多用户 | 降低 P0 攻击面 | 多用户是商业阻断需求且安全资源齐备 |

## 3. 关键方案对照和决策条件

### 3.1 Pi SDK vs RPC

- SDK：直接集成 TypeScript、访问会话/资源 API、可类型约束；需要 Node Worker 和版本锁定。
- RPC：进程隔离、跨语言易接入；JSONL 事件与命令关联更复杂，进程恢复需重建。
- 决策：SDK 正式，RPC PoC/回归路径；**不是说 SDK 比 RPC 更安全**——两者都需要 OS 沙箱。
- 实验：真实模型两轮、取消、事件先后、资源重载、100 次短任务稳定性、出错自动恢复。

### 3.2 FastAPI + Node vs Node 一体化

- 两语言方案：既有 API/数据层清晰，Pi 无需 Python 绑定；代价是运维和内部协议。
- Node 一体化：部署简单，但容易把 Pi 进程与 API 权限混同，后续隔离难。
- 决策：保持清晰 Worker 边界；若实测内部协议过于复杂，可把控制平面迁到 Node，但不能合并信任域。

### 3.3 PostgreSQL + 文件卷 vs SQLite + 单容器

- SQLite：单用户原型更简单，容易备份，但并发 Run/Queue/行级租约和迁移逻辑需要额外设计。
- PostgreSQL：更稳健的事务与索引，支持未来多用户，代价是 Compose 多一个服务。
- 决策：沿用现有 PostgreSQL Schema；如果早期部署遇到大量 DB 维护问题再做实证评估，不在中途无计划切换。

### 3.4 本地 bind mount vs MinIO/S3

- 本地文件卷符合单机可备份与低复杂度目标。
- S3/MinIO 方便多机横向扩展，但首发增加进程/凭证/一致性复杂度。
- 决策：P0 本地卷+内容哈希，保留对象存储接口，P2 有负载证据再扩。

### 3.5 直接写 Workspace vs 快照/工件化

- 直接写适合 demo、最小复杂度，却容易破坏原件。
- 任务独立工件或 Git worktree 让 Diff/验证/回滚可控。
- 决策：首发只读输入 + 新文件产物；代码编辑 P1 采用 Git worktree，办公原件覆盖需明确审批。

### 3.6 公共远端 Skill Registry vs 纯本地

- 公共目录利于传播，但需要审核、侵权举报、恶意包、安全阻断和长期运营。
- 本地技能首先证明 Agent 能力复用，生态规模不作首发阻断项。
- 决策：P0 bundled，本地私有 P1，公共 Registry P2。若市场规模增长成为明确用户痛点，再构建独立公共服务。

## 4. 风险登记（触发条件、严重度、措施、验收）

| ID | 风险 | Severity | 触发条件/早期信号 | 缓解与验收 |
|---|---|---|---|---|
| R01 | Pi 上游 API/包名变化 | 高 | SDK typecheck 失败 | pin release + contract tests |
| R02 | Pi Extension 未受信任代码执行 | P0 | 任意项目 extensions 自动加载 | 自定义 loader + OS 权限限制 + 恶意仓库负测 |
| R03 | 用户跨目录文件泄漏 | P0 | URL/软链接读到其他卷 | server path resolver + sandbox mount + 负测 |
| R04 | Key 落入 Pi Session/工具日志 | P0 | 哨兵字符串出现在 trace | Vault/proxy + 脱敏扫描 |
| R05 | Provider 不支持 Function Call | 高 | 只回答文字但无法工具调用 | 能力 Probe + chat-only 降级 |
| R06 | 假成功/输出截断 | P0 | 模型结束而 Artifact 无效 | Validator Gate，NOT RUN 不计通过 |
| R07 | 任务重试重复发送 | P0 | 工具回执丢失时触发再次发送 | idempotency/outbox/reconcile |
| R08 | Session JSONL 版本不兼容 | 高 | Pi 升级后旧会话无法加载 | 迁移/兼容读取测试 |
| R09 | Docker 宿主网络问题 | 中 | host.docker.internal 不可达 | 引导和真实 Linux/macOS/Windows 测试 |
| R10 | Skill 版本自动变化 | 高 | 当前 Run 加载了不同 digest | immutable release + pinned snapshot |
| R11 | 个人 Skill 暗含敏感资料 | 高 | 导出包发现 PII | 脱敏扫描 + 用户预览 |
| R12 | 公共平台治理规模过大 | 中 | P0 花大量时间做审核/计费 | P2 才交付公共 Registry |
| R13 | Admin 权限膨胀 | 高 | 管理员默认能看所有私钥/文件 | 最小权限 + 审计 + 用例 |
| R14 | 数据卷恢复不一致 | 高 | DB 引用 Artifact 不存在 | 一致性备份 + 冷恢复演练 |
| R15 | 工具调用延迟/成本过高 | 中 | 单任务频繁不必要 Tool | Budget + 质量指标优化 |

对 P0 类风险：上线后果无法接受，门禁未通过就关闭相关功能；严重风险不能以“文档已警告”为解决方式。

## 5. 必须 PoC 才能决定的内容（OPEN）

| Experiment | 争议点 | 实验方法 | 决策输出 |
|---|---|---|---|
| EXP-01 | Pi SDK 对自定义 Base URL/代理凭证适配 | 实际 SDK + 兼容模型测试 | 是否需要 ModelRuntime adapter |
| EXP-02 | ResourceLoader 能否彻底禁项目未知 Extension | 含恶意 `.pi/extensions` 的 fixture | 完全自定义 loader / sandbox 配置 |
| EXP-03 | Pi Session 重启与并发隔离 | 多轮、重启、同会话双消息 | SessionManager storage & lease |
| EXP-04 | Docker per-run 沙箱成本/启动延迟 | 并发 1/2/4 受限任务 | rootless/sandbox 选型 |
| EXP-05 | 工作区逻辑路径与实际挂载 | Docker Linux/macOS/Windows 实测 | 跨平台路径映射标准 |
| EXP-06 | 本机/局域网模型的 SSRF 允许策略 | 管理员配置/恶意请求负测 | 网络出入站策略 |
| EXP-07 | Office 非文本文件生成质量 | CSV/XLSX/PDF fixtures | P0 实际支持文件格式 |
| EXP-08 | Skill 自动选择质量 | 正负例 50–100 任务集 | P0 默认自动加载还是显式选用 |

实验不得以“接口存在/例子能跑”替代实际负向验证。每个 Experiment 的结果应转为 ADR 和永久测试。

## 6. 推翻设计的条件和变更控制

当外部官方 API 或许可证发生变化，先记录来源日期与受影响边界；如果改变 Tool/Session/Store 契约，需要同步更新上游 [README](README.md)、六份架构文件与功能拆解，并标记 Breaking Change。新能力必须有迁移策略、升级门禁和真实回滚测试。

任何架构改动要回答：它缩短哪一条用户旅程？增加哪一种失败模式？能用什么客观证据证明更好？若答案只有“更先进”或“未来可能有用”，默认延后。

## 7. 当前工程事实（不能夸大）

- 本套文件是 GitHub 设计文档，不代表已创建 Pi Worker、Web UI、API、Docker、Postgres 实库或任何 Skill。
- 文档结构/链接检查不能证明模型 SDK 兼容或安全隔离。
- 真实 Pi SDK 构建、模型联通、容器化 E2E、恶意 Skill 评测、DB Migration、安全沙箱：**NOT RUN**。
- 本项目目前需要先按 [Roadmap](11_ROADMAP_AND_BACKLOG.md) 完成第一个可复现的真实 PR。
