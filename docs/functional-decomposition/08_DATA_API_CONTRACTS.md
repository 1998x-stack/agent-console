# 08 — 数据结构、API、Run Events 与跨模块一致性契约

> Draft v0.4 · 本文件是**API/DB 设计细化**，不代表迁移已执行。以 [DATA_MODEL.md](../DATA_MODEL.md) 的已有 Schema 为基线；改变 enum/主键前必须单独 migration PR 与兼容性测试。

## 1. 领域对象与关系

```text
User ─1:N─ Workspace ─1:N─ Conversation ─1:N─ Run ─1:N─ RunStep
           │                                   │          │
           │                                   └── RunEvent/Approval/Artifact
           ├─ Installations ─→ SkillRelease ─→ Skill (owner + lineage)
           └─ RuntimeProfile/DefaultModel
User/Deployment ─→ ModelConnection ─1:N─ ModelAlias
SkillRelease ─→ Listing (private/team/public scope)
Conversation ─→ PiSessionRef (persisted session reference, single writer)
Run ─→ ModelAlias + selected SkillRelease digests + sandbox image
```

**理由**：会话与 Run 分离避免失败请求污染历史；Release 与 Listing 分离支持创作者 Unlist 但既有 Installation 可控；ModelAlias 与 Connection 分离以支持相同服务多个模型。API 和 worker 不应接受未经校验的 foreign keys 作为授权依据。

## 2. 最小主键与约束

| 实体 | 唯一性/外键 | 不变量 |
|---|---|---|
| Workspace | id; owner_user_id/ org_id | 同时属于用户和组织的规则需明确；首发个人 |
| Conversation | id, workspace_id, created_by | 权限与目录由 workspace 决定 |
| PiSessionRef | conversation_id unique + store ref | 单写者 + 版本 |
| Run | id, workspace_id, idempotency_key | 创建请求去重 |
| RunEvent | (run_id, seq) unique | 单调、可重放、不覆盖 |
| ToolInvocation | run_id, invocation_id, attempt | 外部写入恰好一次 *效果* 只能靠业务幂等 |
| ModelConnection | id + owner_scope | Key 加密引用与模型元数据分开 |
| Release | (skill_id, version), digest immutable | 禁止 UPDATE 变更已发布包 |
| Listing | id, scope, status, approved_release_id | scope/审核/可见性 |
| Installation | (workspace_id, skill_id) current release | 只能安装当前 Workspace 可用 Release |
| Artifact | id, run_id, digest | 受访问控制且内容真实存在 |

**修改前核查**：当前 Schema 是否已有 `agent_runs`、`skill_releases`、`model_aliases` 等实际字段；不能凭文档直接运行 ALTER。

## 3. API 风格与幂等性

推荐 REST + SSE；版本号从 `/api/v1` 开始。输入全部经 Schema 约束。创建/发布/审批/外部写入要提供 `Idempotency-Key`；资源修改使用 `ETag` 或 `expected_revision` 乐观锁。前端只能提交“选择哪一个 Workspace/Model”，最终所有者、路径和权限由后端验证。

| 操作 | Endpoint（设计提议） | 校验/响应 |
|---|---|---|
| 首次初始化 | POST `/api/v1/setup/initialize-admin` | 仅一次，冲突返回 409 |
| 新增模型 | POST `/api/v1/model-connections` | key 加密、base_url 策略，201 |
| 测模型 | POST `/api/v1/model-connections/{id}/test` | probe results，含 capability evidence |
| 发起 Run | POST `/api/v1/agent/runs` | 201/202，返回 run_id |
| 查 Run | GET `/api/v1/agent/runs/{id}` | 权限验证，状态/错误/进度 |
| 流式事件 | GET `/api/v1/agent/runs/{id}/events` | SSE，可用 Last-Event-ID |
| 取消 | POST `/api/v1/agent/runs/{id}/cancel` | 幂等；仅标记取消请求 |
| 审批 | POST `/api/v1/approvals/{id}/decision` | expected_action_hash + expiry |
| 文件列表 | GET `/api/v1/workspaces/{id}/files` | server path resolver，分页 |
| 上传 | POST `/api/v1/workspaces/{id}/files` | size/digest/collision policy |
| 产物下载 | GET `/api/v1/artifacts/{id}/download` | 登录权限/内容类型 |
| 安装 Skill | POST `/api/v1/workspaces/{id}/installations` | workspace + release digest 检查 |
| 保存草稿 | PATCH `/api/v1/skills/{id}/draft` | expected_revision，409 冲突 |
| 发布 Release | POST `/api/v1/skills/{id}/releases` | 验证→不可变版本 |
| 下架 Listing | POST `/api/v1/listings/{id}/unlist` | 所有者/策略、审计 |
| Revoke Release | POST `/api/v1/admin/releases/{id}/revoke` | 独立治理权限 |

这些是设计候选，现有六份文档已定义部分路由。实现时**必须统一最终 OpenAPI**，不能把本表当成已冻结 HTTP 路径。

## 4. Run 创建契约

```json
{
  "workspace_id": "uuid",
  "conversation_id": "uuid-or-null",
  "model_alias_id": "uuid",
  "mode": "code",
  "prompt": "Check the failing test",
  "attachment_ids": ["uuid"],
  "selected_skill_ids": ["uuid"],
  "client_request_id": "uuid"
}
```

创建成功返回 `run_id, conversation_id, status, events_url`。敏感约束：payload 不接受任意 `cwd`、`host_path`、`user_id`、`api_key`、`docker_mount`；如果出现未知权限字段拒绝或忽略并审计。Tool 的最终允许范围和 Skill 具体 Release digest 在服务端 snapshot 冻结。

## 5. Run Event Envelope

```json
{
  "schema_version": "1",
  "run_id": "uuid",
  "seq": 37,
  "occurred_at": "2026-11-16T08:00:00Z",
  "type": "tool.finished",
  "payload": {
    "invocation_id": "uuid",
    "tool": "read",
    "status": "succeeded",
    "duration_ms": 35
  }
}
```

事件不传 Key、原始敏感工具结果或全量文件内容。长输出通过 Artifact/受授权详情页读取。SSE `id` 使用 run-scoped seq，服务器验证 Last-Event-ID 所属 Run 和范围，缓存断连时从数据库补事件，再订阅实时事件，防止“补事件和实时事件”竞态。

## 6. 审批与外部副作用事务

审批结构须有 `action_type`、`target_resource`、`serialized_action_hash`、`requesting_run_id`、`expires_at`、`decision_by`、`decision_at`；执行时重新核对哈希和权限。审批本身不能把已变化的操作目标默认为同意。

外部发送等操作无法靠 PostgreSQL 一笔事务与第三方服务达到真正 exactly-once；采用 outbox + idempotency key + reconcile。若回执丢失，状态标 `unknown_external_effect`，引导查询对方操作结果，不自动重复发送。

## 7. 文件/数据库一致性

写 Artifact 时先写临时文件、校验 hash、原子重命名或对象存储 finalize，最后提交 DB 元数据；崩溃后可能出现 orphan 文件或 metadata dangling，需维护 reconcile 任务。生产 “SUCCESS” 前必须确认已验证文件可读，不能只在 DB 写个状态。

Skill 包也使用 content-addressed storage；发布 Release 后关联哈希不可变。GC 只能清理由引用计数/保留策略确定无人引用的内容，不能随意删除仍被历史 Run 引用的版本。

## 8. 数据迁移策略

每一批 Schema 变动遵守：expand（加 nullable/新表）→ 双读/双写 → 回填 → 验证 → 切换 → contract（加严格约束）。Pi SDK 升级涉及 Session JSONL 格式时，需要读取旧版本样本验证；不可直接把不兼容 JSONL 当成可继续的会话。

数据库 RLS 可做第二防线，但前端请求→API→服务端文件系统的每个路径仍需对象级授权。任何“管理员能够编辑数据库记录”的权限不能被自然转化为“读取全部用户明文 Key”。

## 9. 跨模块不变量和测试

| ID | 测试场景 | 必须为真 |
|---|---|---|
| CT-01 | Run 带其他人的 Workspace ID | 拒绝，无 Run 创建 |
| CT-02 | SSE 用合法但属于另一用户的 run_id | 403/404 且无事件内容泄露 |
| CT-03 | 同一 Idempotency Key 重发 | 返回同一 Run，不重复执行 |
| CT-04 | 重复审批 | 最多一次有效，业务副作用不双发 |
| CT-05 | Run 完成前文件写失败 | 不允许 SUCCEEDED |
| CT-06 | Skill 修改/更新 | 旧 Run 的 Release digest 不变 |
| CT-07 | Listing Unlist | 已有安装不被意外删除 |
| CT-08 | DB 故障/重启 | 已确认状态与事件可恢复 |
| CT-09 | 保存草稿时他人先更新 | 409，不覆盖用户草稿 |
| CT-10 | Session 引用被伪造 | 不能通过路径读取他人 Pi JSONL |
