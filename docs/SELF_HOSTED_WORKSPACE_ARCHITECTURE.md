# SELF_HOSTED_WORKSPACE_ARCHITECTURE — 自托管 Web Agent + Skill Store

> Draft v0.2 (2026-11-16)；设计文档而非实现或测试报告。参考 Open WebUI 用户体验，不等于 fork Open WebUI。

## 1. 核心需求与产品决定

**黄金路径**：`docker compose up -d --build` → 打开 `http://localhost:3000` → 首次管理员初始化 → Web 添加模型的 Provider / Base URL / API Key / Model ID → 选择模型并聊天 → 在自己的 `/{user-id}/workspace` 执行任务 → 侧边栏打开 Skill Store、安装或创建 Skill。

- 首发采用 **self-hosted first**：模型既可为 API 模型，也可为本机 Ollama/vLLM/兼容端点；服务本身不要求公共云账号或云模型。
- **BYOK**：用户或管理员可从 Web 添加、编辑、停用模型连接；供应商 Key 只保存在服务端加密区域。
- **Agent≠聊天 UI**：必须支持流式任务进度、工具调用、受控文件操作、代码执行、预览/下载产物、审批与任务取消。
- **用户既消费又创作**：Skill Store 内含 Explore / Installed / My Skills；普通用户可创建、导入、测试、安装和私有发布；平台治理保留独立权限。
- **本地优先的 Skill Store**：内置离线可浏览的 Skill 索引，用户自有 Registry 存于本机；公共市场是可选扩展。
- **阶段安全门禁**：未完成真实隔离验证之前，只允许单用户可信内置执行；不能为了快速上线默认开放多用户任意脚本执行。

## 2. 交互与首启导航

1. Docker Compose 部署成功，不设置 Provider Key 也能打开 Web 和完成初始化。
2. 首次创建管理员账号；默认关闭公开注册和预置弱密码。
3. Settings → Models → Add Connection：`name`、`protocol`、`base_url`、`api_key`（本地无需认证时为空）、`model_id`。
4. Test Connection：探测地址可达性/鉴权、发现模型或允许手动输入 ID，跑一次最小生成；工具调用单独 smoke test，不能依据 `/models` 成功推断。
5. 首次对话自动创建当前用户 Workspace；Web 展示日志、文件树、文件预览、Diff 和任务产物。
6. 侧边栏 Skill Store：浏览内置技能，查看来源/权限/版本，安装并在 Agent 任务中调用。
7. 重启容器后会话、模型连接、用户文件和安装记录保持不变。

左侧导航：`New Task` / `History` / `Workspace` / `Skill Store` / `My Skills` / `Models` / `Settings`；治理管理入口独立，不把用户自己的 Skill 创作放到 Admin。

## 3. 推荐 Docker 拓扑

```text
browser :3000
    │
    ├─ web (Next.js)
    └─ api (FastAPI)
         ├─ PostgreSQL（元数据与任务队列）
         ├─ 本地持久文件存储（工作区、Skill 包、产物）
         ├─ Model Gateway → 云端 OpenAI-compatible / Ollama / LAN model
         ├─ Skill Registry（本地内置 + 可选公共源）
         └─ Runner Manager → 每个任务的独立安全沙箱
```

基础 Compose 服务：`web`、`api`、`postgres`、`runner-manager`。首发数据库事务队列即可，不强制 Redis；文件先用持久 bind mount，不强制 MinIO。动态运行环境由 Runner Manager 创建，不让 Web/API 直接管理 Docker 容器。

部署建议：默认端口绑定 `127.0.0.1:3000`；对局域网开放时由用户显式启用 TLS、认证、反向代理；镜像正式发行需固定版本或 digest，保留升级回滚与备份指南。

## 4. 用户目录约定（非常重要）

| 位置 | 路径与用途 |
|---|---|
| 用户要求的逻辑路径 | `/{user-id}/workspace` |
| 部署机真实持久路径 | `[DATA_DIR]/users/[internal-uuid]/workspace` |
| 单任务沙箱挂载路径 | `/[internal-uuid]/workspace`（或以工作区根为 `/workspace`） |
| Web 导航 | `/workspace`；可兼容 `/u/[uuid]/workspace` 的 URL |
| Skill 本地包缓存 | `[DATA_DIR]/registry` |
| 执行产物 | `[DATA_DIR]/users/[uuid]/artifacts` |

所有 user-id 均为身份服务生成的内部不可猜测 UUID；**不能用 URL 中的 user-id、用户输入路径或模型提示词决定实际文件挂载**。后端校验对象归属后生成工作目录，拒绝路径穿越、符号链接逃逸和跨用户读取。并发任务优先使用独立 run 副本 / Git worktree，再按审批写回持久 Workspace。

建议先实现 **single-user local mode**；如果以后开放多用户注册，必须先验证逐用户的目录、进程、凭证、沙箱隔离和跨租户授权。

## 5. 模型连接器设计

```text
model_connections:
  id, owner_scope, protocol, base_url,
  encrypted_secret_ref, enabled, timeout
model_aliases:
  connection_id, external_model_id, display_name,
  tool_calling_status, context_window_override
```

- 支持 OpenAI-compatible Chat Completions、可选 Responses、Ollama，以及通过 adapter 扩展的其它供应商。
- Base URL 按容器视角解释：Docker 内的 `localhost` 不是宿主机；访问宿主模型可通过 `host.docker.internal`（Linux 配置 host-gateway）。
- Key 必须用稳定的 `APP_ENCRYPTION_KEY` 加密；API 永远不返回 Key 明文，日志/Trace/Skill 上下文禁止泄漏；模型共享配置不等于共享密钥读取权。
- Model Provider URL 需要防 SSRF：限制可访问地址、跳转、协议和 DNS 变更；对管理员信任的本机/LAN 模型做可审计的显式例外。
- Provider 故障时界面报告 HTTP/认证/模型 ID/超时等不同原因，不导致服务无法启动；允许用户手动录入不支持 `/models` 的供应商模型 ID。

## 6. Agent Runtime 与执行边界

1. AuthContext 获取登录身份，服务端推导 `workspace_id` 与 `owner_id`，锁定 `run_id`、模型、Skill Release。
2. 后端构建 `RunContext`，内含 `working_dir`、只读/写授权、资源与 Token 预算、人工审批要求。
3. Runner Manager 为每次任务提供隔离执行环境，**只**挂载当前用户工作区允许的目录；不暴露宿主机 Docker Socket、其它用户目录、长期 API Key。
4. 执行文件、Git、Office、MCP 工具时进行动作级权限检查；外部发送、大量删除、生产部署必须审批。
5. SSE/WebSocket 实时展示步骤、工具调用、失败重试、文件预览/下载；任务结束回收临时计算环境，持久文件保留。
6. 第三方 Skill 的文档属于不可信指令，Skill 安装、选中和运行授权是三件独立的事。

**不安全的捷径**：把 `docker.sock` 挂到 API/Web、在共享主容器里运行未知 Skill 脚本、把密钥存入浏览器 localStorage、用文件夹名称代替权限校验、允许任意 Base URL 向云元数据地址请求。

## 7. 本地 Skill Store

| 页面 | 功能（目标） |
|---|---|
| Explore | 内置离线 Skill、分类、关键词搜索、详情、权限声明、安装 |
| Installed | 当前工作区已安装版本、启用/停用、锁定、更新、卸载 |
| My Skills | 新建、AI 辅助创建、导入 ZIP/`.skill`、编辑 `SKILL.md`、测试、版本 |
| Run Detail | 显示本次使用的 Skill 及其具体版本、授权、执行日志 |
| Governance (future) | 可见性策略、违规处置、审核、全局封禁与审计 |

本地 Store 不依赖公网运行；如连接远端社区 Registry，必须先告知远端来源、版本、签名/哈希和安全权限，下载后验证内容 digest。保持 `Skill / Release / Listing / Installation` 分离；卸载只影响当前用户/工作区，不触发公共下架。

## 8. API 契约初稿

```http
GET  /api/v1/setup/status
POST /api/v1/setup/initialize-admin
GET  /api/v1/model-connections
POST /api/v1/model-connections
POST /api/v1/model-connections/{id}/test
GET  /api/v1/models
POST /api/v1/agent/runs
GET  /api/v1/agent/runs/{id}/events
POST /api/v1/agent/runs/{id}/approve
GET  /api/v1/workspaces/current
GET  /api/v1/workspaces/current/files
POST /api/v1/workspaces/current/files/upload
GET  /api/v1/skills
GET  /api/v1/skills/installed
POST /api/v1/skills/{id}/install
POST /api/v1/skills/import
```

首次初始化入口必须仅单次可用、结合一次性部署 Token 或同等级保护，并在首次创建后不可再次调用。

## 9. P0-P2 工程门禁

| ID | 端到端测试 | 成功标准 |
|---|---|---|
| SH-01 | Compose 冷启动 | 无 Key 可访问首页并完成一次性初始化 |
| SH-02 | 模型连接 | Web 配 Base URL/Key/ID，生成与错误提示均可复现 |
| SH-03 | 工作区 | 首次任务自动创建 `/{uuid}/workspace` 并映射持久路径 |
| SH-04 | Office | 上传 → 分析 → 生成文件 → 下载 |
| SH-05 | Code | 导入测试仓库 → 受控修改 → Diff → 测试报告 |
| SH-06 | Skill Store | 内置离线 Skill 可见、可安装、可被 Agent 调用 |
| SH-07 | 数据持久性 | 重启后用户、Key（解密可用）、聊天、文件、Skill 安装仍在 |
| SH-08 | 跨用户隔离 | A 通过 API、URL、相对路径、链接无法读取 B 文件或 Key |
| SH-09 | 安全退化 | 错 Key、断网、路径攻击、取消、崩溃均有可诊断行为 |
| SH-10 | 供应链 | 第三方 Skill 的安装不授予默认 shell/network/发送能力 |

P0 重点：**单用户本地安装、模型 BYOK、Web Agent、工作区持久化、内置 Skill 浏览**。P1 补足可信 Skill 创建和完整执行沙箱；P2 才放开公共 Registry 与多用户复杂治理。测试未运行时必须标记 **NOT RUN**。

## 10. ADR & 官方参考

- ADR-SH-001 自托管 Docker-first；不以公网 SaaS 为前提。
- ADR-SH-002 Model Provider 配置在 Web UI，支持 BYOK + 本地模型。
- ADR-SH-003 `/{user-id}/workspace` 是逻辑路径，后端 UUID 和持久挂载绑定。
- ADR-SH-004 Skill Store 是用户主界面功能，不是管理员后台附件。
- ADR-SH-005 不在完成沙箱/权限验收前开放多用户危险执行。
- 待决策：rootless sandbox/microVM 实现、Windows 宿主机路径与权限差异、可选远端 Registry 协议、S3 迁移。

- Open WebUI deployment: https://docs.openwebui.com/getting-started/quick-start/
- Model connections: https://docs.openwebui.com/getting-started/quick-start/connect-a-provider/
- Workspace: https://docs.openwebui.com/features/workspace/
- Skills: https://docs.openwebui.com/features/workspace/skills/
- Hardening: https://docs.openwebui.com/getting-started/advanced-topics/hardening/
