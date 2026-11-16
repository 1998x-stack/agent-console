# 06 — Skill Store：发现、安装、创造、测试、发布、下架与演化

> Draft v0.4 · 重点不是“把 App Store 搬到 AI 时代”，而是让同一个用户在使用中创造能力；此处定义客户端业务，参照 [Registry 领域规范](../SKILL_REGISTRY_SPEC.md)、[Pi ResourceLoader](../PI_AGENT_INTEGRATION.md)。

## 1. 三条不同的产品生命线

用户看到的是一个 Skill，但系统要分清：
- **Skill**：创作者拥有的抽象能力资产，带名称、描述、类别、所有权与 Fork 来源；
- **Release**：不可变的内容版本，绑定 digest、manifest、依赖与质量证据；
- **Listing**：某个 Release 在个人/团队/公共市场的展示与可发现性；
- **Installation**：某个 Workspace 安装、启用并锁定的具体 Release。

这四个对象不能并为一张表。否则创作者“下架”会错误删除所有人的安装；用户“卸载”会错误改变市场可见性；创建新草稿会悄悄改变已经执行的工作流。

## 2. 首发市场分层

| 来源 | 谁维护 | 默认可用 | 更新/信任 | 目标阶段 |
|---|---|---|---|---|
| Bundled 内置技能 | 平台发行版 | 离线可浏览 | 随镜像或受信 manifest 更新 | P0 |
| Local 私人技能 | 当前用户 | 仅自己或本机授权用户 | 私人 Draft / Release | P1 |
| Imported 包 | 当前用户导入 | 导入后需验证/确认 | 明确来源 + SHA + 风险声明 | P1 |
| Remote Registry | 社区/外部维护 | 默认 opt-in | 下载验证、供应链风险 | P2 |
| Organization Catalog | 企业管理员批准 | 按组织策略 | 成员授权、发布门禁 | P2+ |

即使远程市场不可用或完全离线，用户也能打开 Store，查看内置技能、已安装技能和自己的技能。首发不强求公共集中服务端；团队/公共审核属于后续不同的部署形态。

## 3. 用户侧六个核心页面

1. **Explore**：搜索、分类、来源、能力描述、运行模式兼容、信任/风险/权限标记、安装。
2. **Skill Detail**：作者、版本、维护信息、输入/输出示例、`SKILL.md` 阅读、支持文件目录、需要的 Tool/模型能力、安装量（有真实数据时才展示）。
3. **Installed**：版本、启用/禁用、更新、卸载、最近被调用的任务；更新是显式操作，不自动升级已运行任务。
4. **My Skills**：Drafts、Private Releases、版本历史、编辑、复制/Fork、导入导出、可见范围。
5. **Skill Studio**：自然语言生成与手动编辑并存；`SKILL.md`、references/scripts/assets 文件树、Diff、权限说明、测试运行。
6. **Publication / History**：申请上架、审核结果、上架/下架、版本回滚、安装影响提示、申诉。P2 才完整开放公共入口。

## 4. 搜索与选择：不要把“最热”当“最适合”

MVP 检索：技能名称与描述关键词、类别、是否已安装、当前模式和 Tool 能力过滤。P2 可使用混合检索 BM25/向量 + 质量排序。排序候选必须经过安全/兼容性硬过滤，不能因高下载量覆盖“不允许访问文件”的策略。

搜索结果应告诉用户“这个 Skill 做什么、何时不适用、依赖什么”，而不是只展示下载按钮。对于同名但不同作者的 Skill 必须带来源和 digest 识别；不要隐瞒来源不明的问题。

## 5. 安装 UX 与数据事务

```text
Select Skill → Verify source/package/digest
  → Show capability and risk disclosure
  → Check Workspace ACL & policy
  → Create Installation (pinned release)
  → Commit
  → New Pi Run uses authorized ResourceLoader snapshot
```

**关键推演**：
- 安装是对一个 Workspace 的行为，不是对全局 Agent 或所有用户生效。
- 安装**不等于运行授权**：若 Skill 要求 bash/network，运行时仍要独立授权并在 Sandbox 约束下执行。
- 当前 Run 已开始时新增 Skill，不热变更其快照；下一轮显示生效提示。
- 导入包先在隔离解析环境中进行限制解压、路径/大小/文件数/类型检查，避免 Zip Slip、压缩炸弹、符号链接逃逸。
- 安装失败要能从事务上回滚 Installation；包缓存可能留下无引用文件，由 GC 清理。

## 6. Pi ResourceLoader 绑定

平台每次 Run 构建 `AllowedSkillSnapshot(workspace_id, release_ids, content_digests, granted_tools)`。Pi 通过受控 ResourceLoader 看到这些 Skill 的 name/description，并根据任务需要加载正文。不能让默认 loader 递归扫描当前 Git 项目的任意 Skills/Extensions，并假定其都已审核。

用户明确选择某 Skill 时，应支持手动指定；AI 自动选择需要独立 Precision/Recall 评测。Skill 名称/描述本身可能含 prompt injection，不能成为系统级可信指令。

## 7. 创作工作流：从成功任务到私人 Skill

步骤：
1. 任务成功后呈现 `Save as Skill`；用户也可从 My Skills 新建。
2. 让 Pi 从本次**用户批准的**任务步骤、规则和结果中提取可复用方法。默认**不复制**原始客户数据、密钥、邮箱地址、完整聊天和文件样本。
3. 生成 `SKILL.md`，约束 `name`、`description`、When To Use、Inputs、Procedure、Verification、Known Limitations 和 Tool dependency。
4. 静态检查：命名与 frontmatter 规范、引用文件存在、越权请求、包尺寸、敏感信息扫描、许可证和来源提示。
5. 用户在 Skill Studio 预览 Diff，补充真实成功/失败示例，选择由沙箱运行测试。
6. 至少使用另一份与原任务不同的 fixture，避免把原任务答案硬编码为“通用技能”。
7. 保存 Draft / 发布私人 Release / 安装到当前 Workspace。只有自己能用不需要公共审核。
8. 后续需要公开分享时，从这个已验证的 Release 发起 Listing 审核。

### AI 自动生成风险

- 会把一次偶然成功的步骤当作通用规则 → 测试包含不同输入。
- 可能把用户私密内容写进 `SKILL.md` → 保存前脱敏预览 + 手动确认。
- 会生成不存在的命令/API 参数 → 测试基于真实工具版本执行。
- 可能产出超长文件导致模型阅读截断 → 长资料放 references，正文保留流程概要。
- 用户修改创建中的文件产生冲突 → 使用 `expected_revision` CAS，拒绝静默覆盖。

## 8. Release 与 Listing 状态机

```text
Draft → VALIDATING → READY → immutable RELEASE
                      └── FAILED → Draft revision
Private Release → installed/used
               → Team Listing submitted → approved/rejected
               → Public Listing submitted → approved/rejected
Public Listing → PUBLISHED → UNLISTED → RESTORED / ARCHIVED
Public Release → VALIDATED → QUARANTINED / REVOKED (security action)
```

**Release 安全撤销与 Listing 下架不同**。被判定恶意的某一 digest 可阻断执行，但不能简单覆盖旧版本文件；应记录原因、通知受影响 Installation、保留必要证据。

## 9. 用户下架、删除、卸载：必须分清七个动作

| 动作 | 谁操作 | 新安装 | 既有安装 | 执行 |
|---|---|---|---|---|
| Disable Installation | 安装用户 | 不变 | 当前空间标记禁用 | 新 Run 不加载 |
| Uninstall | 安装用户 | 不变 | 当前空间移除 | 不再加载 |
| Unlist | 创作者/组织授权者 | 停止新分发 | 旧安装保留 | 按原授权继续 |
| Archive Skill | 创作者 | 不可再新编辑/公开 | 依存版本保留 | 按策略 |
| Revoke Release | 安全治理者 | 阻断 | 安装标警告 | 对指定版本阻断执行 |
| Delete Draft | 草稿作者 | 不影响 | 不影响 | 不影响 |
| Delete all | 特殊合规/数据操作 | 单独评估 | 涉及依赖和备份 | 不允许一键无审计删除 |

主动 Unlist 应展示“将不再允许新增安装，现有安装如何处理”的确认页；对于本地私人 Skill，删除前列出正在使用它的 Workspace/Conversation。公开市场如有付费权益（P3）还需独立处理，不在 MVP 偷偷默认。

## 10. 版本与依赖策略

- `skill_release(version, digest)` 不可变；修改生成新 Release，唯一 digest 与签名按受信来源策略验证。
- Installation 默认锁定确切 Release，避免后台更新导致执行不复现。
- Update 提供变更 Diff、权限增量、兼容性变化和测试结果；新增高危权限需要重新授权。
- Fork 派生拥有独立 Skill ID，保留 source attribution、license 和 provenance，不能把别人的公共 Skill 私有化而抹去来源。
- 依赖：P0 不做自动安装任意脚本依赖；若脚本引用外部依赖，明确其在 sandbox 内是否可用、下载网络权限和确定性锁定版本。
- 当某个版本被 Revoke，必须防止“回滚到同一恶意 digest”的绕过。

## 11. Creator Studio 的验证标准

建议每个 Skill 携带最小 evaluation manifest：一条正例触发、一条负例不应触发、至少一条真实任务输出验证。测试结果必须区分 `PASSED`、`FAILED`、`NOT_RUN`、`BLOCKED`；测试日志与实际 Release digest 相连。

用户不必写代码就能发起一次“测试技能”，但 UI 不能因此绕过执行安全和测试真实性。执行有风险的文件/脚本时按普通 Agent Run 走审批和 sandbox。

## 12. 客观验收

AC-SK-01：离线 Docker 启动后内置 Store 可浏览，搜索结果本机可索引，不发隐式公网请求。
AC-SK-02：安装固定 Release，Pi 只能看到当前 Workspace 已启用的 Skill；另一个用户不可直接加载。
AC-SK-03：同名、恶意 ZIP、资源链接逃逸、digest 不符、超大包均拒绝并留错误证据。
AC-SK-04：Draft 多轮修改有版本冲突检测，测试失败不生成可发布 Release。
AC-SK-05：禁用/卸载影响新 Run，不修改全局 Listing；Unlist 不回收已有私人安装内容。
AC-SK-06：版本升级、回滚、Revoke 对当前运行与下一个 Run 的行为可解释且可复现。
AC-SK-07：Save as Skill 不能把模型 API Key 或用户私人文件原文悄悄写入导出包。
AC-SK-08：Skill 有正例/负例触发基准集，实际误触发率可测。
