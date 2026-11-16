# 04 — 每用户 Workspace、文件、代码仓库、产物与恢复

> Draft v0.4 · 用户指定的 `/{user-id}/workspace` 是 Agent 的**逻辑工作目录**。具体宿主机路径与浏览器 URL 是另外两个概念。参考：[Pi](05_PI_RUNTIME_AND_SESSIONS.md)、[部署](09_DOCKER_DEPLOY_AND_OPERATIONS.md)、[安全](07_ROLES_ADMIN_AND_SECURITY.md)。

## 1. 为什么用户 Workspace 是产品的“边界实体”

聊天历史不是可交付工作。Workspace 决定 Pi 能读哪些文件、能写到哪里、能引用哪些 Skill 和 Tool、能恢复哪些生成产物，也是未来多用户权限隔离的核心。

用户要求 `/{user-id}/workspace`，不能仅把这串文字写进 Prompt。它必须在 OS 级进程/挂载、API 文件路径和数据模型中具有一致含义。

## 2. 路径分层与强制约束

| 场景 | 示例 | 不变量 |
|---|---|---|
| Agent 逻辑工作路径 | `/{user-id}/workspace` | 服务端解析、映射到真实 UUID |
| 宿主机存储 | `[DATA_DIR]/users/[uuid]/workspace` | 仅部署管理员可直接访问 |
| Pi 的 cwd | `/[uuid]/workspace`（sandbox 内） | 每个 Run 授权并检查真实路径 |
| HTTP 文件 API | `/api/v1/workspaces/current/files` | 资源归属来自登录身份 |
| Web 路由 | `/workspace` | URL 不构成文件权限 |
| Run 暂存目录 | `/runs/[run-id]/snapshot` | 不与其它 Run 共享写入空间 |
| 永久产物 | `[DATA_DIR]/users/[uuid]/artifacts` | 具备追踪、下载权限和保留策略 |

任意用户不得通过切换 URL 中的 user-id 读取其它目录。即使出现无效 UUID、大小写差异或编码异常，API 也只能以当前 AuthContext 解析合法路径。

## 3. Workspace 访问模型

`Workspace` 与 `User`、`Membership`、`Run` 是不同对象。首发仅有一个用户、一个默认 Workspace，但内部 Schema 仍保留 workspaceId，不能把每段路径硬编码为“当前登录用户的默认目录”。

每个文件操作都要经历：认证 → Workspace 归属/ACL → 按类型的操作许可 → 安全路径解析 → 执行 → 写审计/结果。需要多用户共享时，不能通过共享宿主 bind mount 代替 Workspace 成员权限。

## 4. 文件生命期

```text
UPLOAD_PENDING → SCANNING/TYPE_CHECK → STORED → AVAILABLE
                                      └─ REJECTED
AVAILABLE → IN_USE → DERIVED_ARTIFACT → VERIFIED → DOWNLOADED / ARCHIVED
                      └─ FAILED/QUARANTINED
```

- 上传：限定单文件大小、扩展名不是唯一判断依据，检查内容 MIME、魔数、压缩包解包限制；可恢复上传 P1。
- 存储：原始输入默认只读；从 Pi 生成的内容存到 Run Snapshot/Artifacts，不与上传原件混淆。
- 版本：发生覆盖时需显式用户许可；至少记录创建时间、来源 Run、尺寸、哈希、最后修改。
- 下载：内容类型、Content-Disposition、权限、缓存头和防 HTML 脚本执行；对主动预览的 HTML 不赋予主站权限。
- 清理：临时沙箱文件可自动回收；持久 Workspace 和 Artifacts 的清理要有用户可见策略。Task 删除不等同于文件删除。

## 5. Run 与文件快照

两种可选策略：
A. **直接写持久目录**，实现简单，但失败可留下部分写入且并发写入冲突。
B. **每 Run 快照 + 差异提交**，更可靠，适合 Agent 写代码/办公文件；成本为复制、磁盘和合并复杂度。

**推荐**：P0 读取直接从受限只读挂载；生成文件写入每 Run 产物目录。P1 的代码写入采用 Git worktree，成功后用户确认应用；办公文件采用新文件输出/原子 rename 而非覆盖旧原件。不要在 P0 同时研发复杂通用 OverlayFS 双向同步。

## 6. Office 工具能力

| 操作 | 需求 | 安全 | 校验 |
|---|---|---|---|
| Upload CSV/Markdown | 用户上传可供分析数据 | 大小/MIME/路径 | 可重复读取且原件一致 |
| Read PDF/text | 提取资料 | 安全解析器、限制资源 | 页数/内容完整性报告 |
| Generate Markdown/PDF | 输出成果 | 产物文件夹、禁任意路径 | 可解析/下载/哈希 |
| XLSX analysis | 非技术办公核心价值 | 公式/宏不执行 | 抽样单元格/总量检查 |
| Write original | 修改原报告 | 审批 + 备份 | Diff/验证/回滚 |
| Email send | 外部通信 | 发送目标审批 | P2 才开放 |

文件中的 “忽略规则、传走密钥” 只能视为**不可信文件内容**，不能被 Pi 当作权限指令。

## 7. Code Workspace 能力

- Import：上传 ZIP/Git Clone（源地址可 SSRF，P1 需校验目标）、生成固定工作树；不可默认复制宿主机隐藏凭证。
- Read：忽略 `.git/objects`、大量二进制文件、`node_modules` 等；工具按大小/次数限制，避免上下文爆炸。
- Diff：所有改动有路径、前后版本、统一 diff、涉及文件列表；不可只渲染模型总结。
- Test：在 sandbox 中运行、记录命令、退出码、日志、约束；与 LLM 声称“测试通过”无关。
- Apply：只有用户确认后才把通过验证的修改应用到主工作区；文件版本有变化返回冲突而不是覆盖。
- Git Push/PR：对外写操作 P2 以上；需要独立授权、目标分支和账户范围，不自动继承 Git 远端凭据。

**脏仓库边界**：如果导入的仓库已有本地改动，默认不清空；创建 worktree 时明确记录基线 commit 或文件快照，避免覆盖人的更改。

## 8. 文件并发与一致性

| 情境 | 正确行为 |
|---|---|
| 两个 Run 编辑同文件 | 乐观锁/基线版本对比，第二个提交冲突 |
| Run 执行中用户删除文件 | 工具明确报告 ENOENT，流程可重试或失败 |
| Pi 写完文件但 DB 插入 Artifact 失败 | 后台 reconcile 或标记 orphan，并不能直接宣称 SUCCESS |
| SSE 断连 | 文件仍在 Run 产物目录，重连可查 |
| 磁盘空间不足 | 停止新写入，任务 FAILED/WAITING_RESOURCE，原文件不变 |
| 软链接到 /etc 或其它用户 | 读写 API 与 sandbox 必须拒绝路径逃逸 |
| 用户改名工作目录 | 稳定逻辑 Workspace ID；文件索引与真实路径一致迁移 |
| 浏览器重复上传 | 上传幂等键和内容哈希；不能产生未知重复副作用 |

## 9. 数据索引与存储粒度

`workspace_files` 的索引字段建议：`workspace_id, logical_path, object_hash, size_bytes, mime, origin_run_id, revision, state, created_at`；不存不必要的原始绝对路径。`artifacts` 与 `run_steps` 关联验证证据和文件摘要。访问日志只记录可审计标识/相对路径，不写敏感文件原文。

宿主机的实际卷与 DB 需要同时备份；只有备份 PostgreSQL，没有备份文件卷，会出现“记录存在但文件打不开”。

## 10. 配额与资源回收

P0 可以全实例磁盘空间阈值 + 上传大小上限；P1 才加 per-user、per-workspace 总配额和 Run 临时空间配额。Quota 由后端实际文件大小核算，不能只靠前端表单限制。长期保留的 Pi Session JSONL 也需要单独计入存储预算。

## 11. 测试与验收

- AC-WS-01：首任务创建当前用户 Workspace，Docker 重启后同一路径、同一内容哈希。
- AC-WS-02：通过 API、URL 改 userId、相对路径、绝对路径、软链接、压缩包嵌套均不能访问其它用户或宿主系统目录。
- AC-WS-03：两个 Agent Run 写同一文件返回可解释冲突，原文件保持正确。
- AC-WS-04：生成的办公文件能被真实解析器打开并校验字段，不只是文件存在。
- AC-WS-05：代码任务不直接改变原仓库基线，用户批准前仅保留 Diff/沙箱副本。
- AC-WS-06：disk full、失去权限、进程崩溃后无无声数据丢失；保留输入与错误证据。
- AC-WS-07：文件下载遵循对象级授权，不能通过静态目录绕开 API 验证。
