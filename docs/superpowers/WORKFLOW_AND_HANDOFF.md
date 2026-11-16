# Superpowers-style 研发协议：Spec → Plan → TDD → Review → Verify

> 本文件是 **Agent Console 工程行为契约**，而不是未经核验的 “Superpowers 已执行” 记录。

## 0. 出发点与方法来源

借鉴 https://github.com/obra/superpowers 的工作方法，包括 brainstorming、using-git-worktrees、writing-plans、subagent-driven-development / executing-plans、test-driven-development、systematic-debugging、verification-before-completion、requesting-code-review、finishing-a-development-branch。上游版本会变化，执行时应在实际 Agent 环境读取已安装的对应 Skill，并优先遵守其当前指令；**当前文档只是为仓库编写的本地研发协议**。

### 五个禁止

- 没有可审查 Design Spec 就开始跨模块开发。
- 没有**看见测试失败**就写最小修复并声称完成 TDD。
- 以 mock 模型测试替代真实 Pi + 真实 Provider 集成验收。
- 把 LLM “我完成了”、CI 未运行或文档检查等同代码验收。
- 直接在 `main` 实验或不经用户授权合并 PR。

## 1. 每个 Feature 的唯一闭环

```text
Discover Intent / Current Repo State
  → Write small Design Spec (goals, non-goals, architecture, data/permission, errors, AC)
  → Spec Review (product correctness + security constraints)
  → Write implementation plan (one checkable deliverable per task)
  → Worktree/Branch + clean baseline (record actual test evidence)
  → Per Task: RED → GREEN → REFACTOR → test → commit
  → Review 1: spec compliance, Review 2: code quality/security
  → Integrate tests / E2E / failure injection
  → Verification before completion (read outputs; preserve failures)
  → PR + gotchas + ADR/risk updates + user review
  → Next phase only after explicit exit gate
```

如果是**明确授权实现**且 Spec 已由用户前面确认，可以连续执行计划，遇到非阻断问题按 ADR 做小范围判断；如遇不可逆操作、越权风险、跨仓库/生产环境变更则停下取得授权。

## 2. Spec 写作格式（各 Phase 固定）

1. Context & JTBD：谁、为什么现在做。
2. Goals / Non-goals：可观察成果，不做什么。
3. User Journeys：成功路径和至少 3 个负面/异常路径。
4. Domain & Boundaries：所有者、权限/数据与信任边界。
5. Interfaces：UI/API/SSE/Schema/Tool/Skill Contract（提案，冻结时给 JSON Schema/OpenAPI）。
6. Error & Recovery：取消、重复请求、数据冲突、进程崩溃、断网等。
7. Security & Privacy：攻击面与默认拒绝策略。
8. Testing：功能 E2E、静态/契约、故障注入、负例。
9. Exit Gate：客观且不可模糊的通过要求。
10. Open Decisions：未知不能偷偷当成已知。

**原则**：Spec 说明什么正确、为什么，不是把完整源码塞进 Spec。

## 3. Plan 写作格式

每份实施计划包含：
- `Goal`、`Architecture`、`Tech Stack`、`Spec` 的文首元数据；
- Global constraints（必须包含独立 Pi Worker、私有工作区、密钥脱敏、Skill 权限与 NOT RUN）；
- 任务编号与依赖，**每任务一个可独立被 reviewer 拒绝的产物**；
- 任务文件路径、预计新增/修改的类型或 API、测试名称、运行命令、预期 RED 与 GREEN；
- 完整步骤至少包括 “写失败测试 → 确认失败原因正确 → 写最小实现 → 运行指定测试 → 重构/运行关联检查 → commit”；
- reviewer 需要注意的五大输入类/边界；
- 阶段完整性检查：Spec AC → Task → Test → Evidence；
- 最后由人工/授权的 Agent 决定怎样实施（subagent 或 inline）。

**计划不可越过已定义架构**。遇到未解决协议问题，应先安排 PoC+ADR 任务，而不是让实现 Agent 自己发明兼容性行为。

## 4. 任务级工作协议

每个 Task 使用不可跳过的步骤：

1. 阅读本阶段 Spec、当前 Task（仅本任务必需上下文）和已实现的接口文件；
2. 检查基线、依赖任务 commit 和当前 worktree 无未提交不相关文件；
3. 新增一个具体失败测试（或定义并运行失败的集成验证），执行并记录预期失败；
4. 实现最小功能，执行该测试并确认变绿；
5. 运行关联测试、静态检查、API Contract 和必要安全负例，不能只执行单个 happy-path；
6. 审查本任务：接口符合 Spec、权限最小、错误可诊断、无假测试/硬编码；
7. Commit 并将证据写到 `docs/gotchas.md` / 对应 PR 记录；
8. Review A（Spec 合规）：满足用户故事、AC、权限、非目标？
9. Review B（质量/安全）：是否测试可靠、没有路径或密钥问题、无重复代码？
10. 任一 Critical/Important 未处理，任务保持 BLOCKED，不标 DONE。

如果 Agent Harness 没有 subagent 工具，明确采用 inline 执行，并在阶段末安排独立代码复审；**不能假称执行了 fresh-subagent review**。

## 5. 前置检查与多 Agent 协作

- 使用独立 branch/worktree，记录 base commit；开始前运行已有完整 baseline（如果仓库还没有测试，记录 `NOT AVAILABLE`，先创建真实可失败的 test harness）。
- 任务之间共享接口必须先冻结，特别是 RunSpec、RunEvent、AuthContext、WorkspacePath、ModelConnection、Skill Release。
- 可并行的：Web UI shell、模型协议 mock/fixture、Skill 元数据 UI（需共享类型冻结）。
- 不能随意并行的：DB migration 与 API schema 重写；Pi Session 格式与 Worker 事件；权限与 OS mount 模型；同一文件编辑。
- 子 Agent 不得创建新测试后跳过其执行，不得跳过 lint/CI，不得在失败时写“暂时忽略”。

## 6. Systematic debugging

遇到异常先收集：完整错误类别、最小复现、代码/配置差异、依赖版本、环境。然后形成假设 → 设计能区分假设的实验 → 确定根因 → 加失败回归 → 最小修复 → 运行全部关联测试。禁止一次改多项掩盖真正原因。每次将 root cause 与 prevention 写到 `docs/gotchas.md`。

## 7. Verification before completion

完成断言必须回答：
- 哪个具体命令？在哪个 Commit、镜像与配置？
- 实际退出码、输出摘要、测试数及日志存在哪？
- 结果覆盖的是 unit、integration、E2E、security 哪一个范围？
- 失败和 NOT RUN 是否明确列出？
- 计划内每个 AC 能否定位到 Test ID 和证据文件？
- 用户数据、密钥、外部副作用是否得到保护？

说明“我检查了”“我应该已经修复”不是证据。

## 8. Phase Gate 强制规则

Phase 完成时用 [Gates](PHASE_DEPENDENCIES_AND_GATES.md) 的检查表，以下任意项阻断下一阶段：P0 安全越权、关键路径不能复现、DB/Schema 不兼容、Pi 真实会话无法恢复、产生不可逆副作用、测试被跳过却标绿。必要时缩小功能、关闭 feature flag，不准删除失败测试。

## 9. Agent 交接最小包

- 当前 Branch/Commit/base；
- 设计 Spec + 实施 Plan 路径；
- 未完成 Task ID / 最近通过的验收；
- 测试命令与真实结果；
- 运行条件与需要的凭证（**只写变量名，不提交秘密**）；
- 活跃风险与故障复现；
- 下一步唯一明确动作与禁止碰触区域。

见 [AGENT_EXECUTION_PLAYBOOK](AGENT_EXECUTION_PLAYBOOK.md)。
