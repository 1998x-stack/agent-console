# 09 — Docker 本地部署、升级、备份、恢复、诊断与可运维性

> Draft v0.4 · 本产品的首发交付物是**用户能自己部署并在 Web 真正使用**的实例，而不只是 API 或漂亮 UI。相关：[自托管架构](../SELF_HOSTED_WORKSPACE_ARCHITECTURE.md)、[Pi](05_PI_RUNTIME_AND_SESSIONS.md)、[质量](10_QUALITY_SECURITY_EVALS.md)。

## 1. 一键启动不等于“没有复杂性”

用户运行 `docker compose up -d --build` 应能启动界面，但完整真实链路包括：镜像、DB schema、密钥、模型网络、Pi SDK、工作目录、Skill 缓存、用户权限、执行资源。每一层可能单独失败，需要产品化诊断，而不是把所有失败写成 502。

首发目标：普通开发者可用 Docker Compose 完成本机部署；Windows/Docker Desktop、macOS 与 Linux 的 bind mount 差异需要实测，不能仅靠 Linux 开发机绿色结果宣布跨平台支持。

## 2. 最小部署拓扑

```text
Browser :3000 → web
              → api → postgres / data volumes
                     → model-gateway
                     → pi-worker → sandbox-runner
                     → local skill-registry
```

建议 Compose 服务 `web, api, postgres, pi-worker, runner-manager`；首发队列可依赖 Postgres 任务表，不强制 Redis。正式运行沙箱可由单独安全服务管理，不能把宿主高权限 Docker Socket 无限制传给 Web/API/Pi Worker。

**部署默认**：绑定 `127.0.0.1:3000`，仅本地访问；开放到 LAN 需显式配置 HTTPS、反向代理、可信主机、认证、CSRF 和请求速率限制。强制持久 `APP_SECRET_KEY`/`APP_ENCRYPTION_KEY`，新建后重启不随机变化。

## 3. 目录、配置与数据

| 数据 | 持久化位置 | 备份是否必须 |
|---|---|---|
| PostgreSQL | `[DATA_DIR]/postgres` | ✓（一致性备份） |
| Workspace 文件 | `[DATA_DIR]/users/[uuid]/workspace` | ✓ |
| Pi Session JSONL | 受控 Session Store | ✓ |
| 加密模型连接/元数据 | DB | ✓ |
| 加密主密钥 | 环境 secret 或安全密钥文件 | ✓，必须分离安全保存 |
| Skill Release 内容 | `[DATA_DIR]/registry` | ✓，若非内置可重建 |
| Run Artifact | `[DATA_DIR]/users/[uuid]/artifacts` | ✓，按保留策略 |
| 缓存、临时沙箱 | `[DATA_DIR]/cache` / 临时路径 | 可清理，不能当持久数据 |

**特别提醒**：只复制数据库不能恢复真实 Workspace 文件；只复制文件而丢失密钥会使原模型连接无法解密；恢复后的文件属主/SELinux/AppArmor 也可能影响读写。备份/恢复一定要做一次完整演练。

## 4. 首次部署体验

1. 运行 Compose，healthcheck 显示 `web/api/db/pi-worker` 的阶段性状态，数据初始化是幂等迁移。
2. 进入 `/setup` 页面，看见“存储准备好/Agent 运行引擎准备好/尚未配置模型”的明确步骤。
3. 初始化仅一次管理员，防并发重复初始化。
4. 配模型后跑模型连接测试和真实 Pi 一个字回复；失败时给出可操作诊断。
5. 在 Workspace 查看生成文件，安装内置 Skill 并复用。
6. 关闭并重新打开容器，数据保持；更新指南明确何时备份和回滚。

如果没有 Key，首页仍应开放设置、历史文件和 Skill 浏览，而不是整个应用启动崩溃。

## 5. 健康检查分为三类

- **Liveness**：进程在运行，异常退出后可重启。
- **Readiness**：依赖数据库、关键存储可访问，API/Worker 可接受新任务。
- **Functional Probe**：真的通过一次 Pi 调用模型和/或读取 Workspace Fixture；需要用户明确启动，防止开机自动消耗 Token。

不建议 healthcheck 每 10 秒调用一次付费模型。运行状态页展示最近一次 Functional Probe 时间、使用的模型别名、结果与故障类型。

## 6. 环境变量与 Web Settings 的边界

- Compose 只负责基础设施、数据目录、主密钥、网络端口和可选系统管理员初始化 token。
- 模型 API Key / Base URL / Model ID 优先在 Web 配置并以加密形式持久化。
- 用户账户和 Skill 记录不应直接塞进 YAML；离线模式不应自动下载任意模型或默认发送 Telemetry。
- 可通过可选 env bootstrap 供自动部署使用，但一旦写入 DB 后要明确 precedence；避免重启时把 UI 修改的 Key 静默覆盖。

## 7. 升级策略

| 情况 | 处理 |
|---|---|
| 只更新 Web UI | 版本兼容 API contract，失败可回滚镜像 |
| 更新 API Schema | expand/contract migration、备份、迁移日志 |
| 更新 Pi 包 | 锁 tag/package，跑会话兼容、Skills、Tool、事件测试 |
| 更新 Skill bundled 包 | 不自动替换用户安装 Release，显示升级建议 |
| 反向代理/TLS 改动 | 验证 Cookie、CSRF、SSE 长连接、下载链接 |
| 用户在 P1 后开启多用户 | 必须先过隔离、存储 ACL、沙箱安全测试 |

正式发布镜像固定版本或 digest，不使用 `latest` 当可重复部署证明；更新前输出备份指令，更新失败要能回滚应用与 DB/会话兼容状态。

## 8. 备份恢复流程（设计）

**Backup**：暂停/协调写入，获得 PostgreSQL 一致性备份、工作区/Session/Registry 快照及元数据 manifest；加密主密钥单独安全保存；记录版本、时间、校验和，不把用户 Key 明文写入备份日志。

**Restore**：在空实例恢复加密密钥→数据库→文件卷→Pi Session、Registry；修复 UID/GID 文件权限；校验关联 Artifact digest；通过至少一条历史会话、一个文件下载、一个 Skill 安装和一个新 Run 来验证。

**灾难场景**：磁盘损坏、加密 Key 遗失、镜像升级后 DB 不兼容、恢复到较旧版本时现有 Session 格式无法读取。必须提前定义可读但不可继续的降级体验，不能假装任何升级都可无损倒退。

## 9. 日志与可观测性

关键维度：`request_id, run_id, user_id_hash, workspace_id, pi_session_ref, model_alias_id, skill_release_digest, event_seq, error_code`。默认不记录用户消息全文/敏感文件/完整请求头。日志可分 debug/standard/security，敏感操作审计独立存储并限制读者。

指标：模型请求成功率、连接 Probe 分类、Pi Worker readiness、任务排队与时长、失败分布、磁盘/内存/CPU、Artifact 校验失败、Skill 触发、崩溃恢复。人类可读的错误库是产品的一部分。

## 10. 故障诊断矩阵

| 故障 | 可见现象 | 排查/产品反馈 |
|---|---|---|
| Docker 端口占用 | Web 无法打开 | 检查绑定端口和 Compose logs |
| DB 无法连接 | Setup 卡住 | readiness 给出数据库不可用 |
| Linux 模型宿主网络 | 连接失败 | 提示 host.docker.internal / host-gateway |
| GPU/Ollama 不存在 | 模型不可达 | 不使整个 Web 不可用 |
| 磁盘耗尽 | 文件任务失败 | quota/存储错误且不损坏旧文件 |
| Worker 崩溃 | Run 停止进展 | lease 超时→明确 FAILED/待人工恢复 |
| Pi 升级后 Session 错误 | 旧聊天无法继续 | 保留只读历史，新建 Session，错误证据 |
| Skill 缓存丢失 | 已安装但资源不可用 | 校验 digest，提示修复/重装 |
| TLS/SSE 代理超时 | 输出中途停 | 通过 Last-Event-ID 恢复 |
| 数据卷权限错误 | 无法创建 Workspace | 明确 UID/GID/SELinux 提示 |

## 11. 运维验收

AC-OPS-01 Docker 空数据卷启动，无 Key 仍可 UI 初始化。
AC-OPS-02 重启后用户、连接、会话、文件、Skill 固定版本仍在。
AC-OPS-03 打印日志不会泄漏 API Key，默认本机绑定。
AC-OPS-04 全量备份→新卷恢复→旧会话读取、新任务执行、文件下载、Skill 使用通过。
AC-OPS-05 错 Key、DB 中断、Pi Worker Crash、磁盘满等故障可检测可解释。
AC-OPS-06 Pi/npm 版本固定，升级后执行 SDK build+Session read+Skill loader 回归。
AC-OPS-07 不支持的平台明确标记 NOT TESTED；不能只凭 Compose 语法认为跨平台验收成功。
