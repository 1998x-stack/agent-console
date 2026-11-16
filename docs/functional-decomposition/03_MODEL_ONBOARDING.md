# 03 — 模型接入、API Key、Base URL、能力探测和模型路由

> Draft v0.4 · BYOK/Local LLM 是首发硬依赖。相关：[自托管架构](../SELF_HOSTED_WORKSPACE_ARCHITECTURE.md)、[Pi 集成](../PI_AGENT_INTEGRATION.md)、[安全](07_ROLES_ADMIN_AND_SECURITY.md)。

## 1. 为什么模型配置是产品功能，不只是系统配置

面向非技术办公用户，若强制编辑 .env，部署成功不等于“可用”；开发者则常接自定义网关、Ollama、vLLM、LM Studio 和不同 API 供应商。产品必须把 Provider Connection、Model Alias、Capability Probe 和 Run 所使用模型分开。

| 功能 | 用户需求 | 数据对象 | P0 |
|---|---|---|---|
| 新增/编辑连接 | 自带服务地址和密钥 | ModelConnection | ✓ |
| 模型发现/手填 ID | 列表 API 不完整 | ModelAlias | ✓ |
| 连通/鉴权测试 | 不想在 Agent 任务中才发现故障 | ProbeResult | ✓ |
| 功能能力测试 | 某些模型不支持工具调用 | CapabilitySnapshot | ✓ 受限 |
| 默认模型选择 | 新会话可以直接执行 | User/WorkspaceDefaultModel | ✓ |
| 运行中改模型 | 供应商失败或费用过高 | Run model snapshot | P1 |
| 供应商负载/容灾 | 多模型优选 | RoutingPolicy | P2 |
| 组织共享模型 | 管理员统一连接 | Scoped Connection | P2 |

## 2. Provider 与 Model 不能混成一行

`ModelConnection` = 某个 API 服务端点和密钥、协议、拥有者、启停状态、最后测试结果；`ModelAlias` = 一个可选模型 ID、能力证据、默认参数、用户可读名称。一个 Connection 可暴露多个 Models；同一个型号在不同代理服务下也可能表现不同。

**必填表单**：`display_name`、`protocol`、`base_url`、`model_id`（允许未知发现前手填）；`api_key` 对无认证本地端点可空。建议默认不允许将个人 Key 设为全局共享，管理员必须显式共享“调用权”。

## 3. Protocol/Provider 适配顺序

1. **OpenAI-compatible Chat Completions**：首选 P0 兼容接口；不同代理在 tool calls、streaming、usage 字段上存在差异，必须实际探测。
2. **Ollama**：建议支持本机与 LAN 端点，可通过 OpenAI-compatible 或官方接口；容器内 `localhost` 是容器不是宿主机。
3. **Pi 官方已有的原生 Provider**：按照 Pi 已锁定版本和协议实现，不能假设每个 Provider 都支持修改 Base URL。
4. **自定义 Responses/非标准供应商**：P1 以后 adapter，避免 P0 为几十种格式建巨大兼容层。

Open WebUI 的连接器界面和模型发现可作为 UX 参考；Pi 的 ModelRuntime/ModelRegistry 是底层调用实现，两个模型目录不应出现双重真相。参阅：https://docs.openwebui.com/getting-started/quick-start/connect-a-provider/ 和 https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/sdk.md。

## 4. 连接测试必须是分级诊断

```text
URL parsing + allowlist
    ↓
DNS & network (network timeout)
    ↓
TLS / proxy / endpoint reachability
    ↓
Auth (401/403)
    ↓
Model discovery or manual ID (404 expected for some adapters)
    ↓
Minimal inference request (real text tokens)
    ↓
Tool-call probe (read-only fake-tool schema, no side effects)
    ↓
Capability snapshot with observed_at
```

仅 `/models` 200 并不证明模型可生成内容；仅回复一段文本也不证明会按 JSON schema 调用工具。每次 Probe 标注 `passed/failed/unsupported/unknown`，记录错误码与延迟，不保存原始 Key；用户知道哪些能力**已测试**、哪些**尚未测试**。

### 拒绝草率的自动修复

URL 后缀 `/v1`、`/api` 差异容易导致错误。可以提示候选修正，但不在后台静默重写用户 Base URL。模型名称不一致时展示供应商返回的模型候选，而不是替用户强行换模型。

## 5. 模型能力与 Office/Code 模式匹配

- Chat-only：可做无工具问答，不能承诺读写文件；UI 应明确能力限制。
- Tool-capable：启用受控 `read` 等工具，但需依次经过 Pi、Tool Gateway 和沙箱策略。
- Long context：可以提供上下文窗口设置，但如果服务端无法真实测得，标注用户配置/未知，不能编造上下文长度。
- Vision/multimodal：按模型实际能力探测；P0 图片/PDF 处理可先使用文件工具提取，不假设模型原生支持。
- Streaming：SSE 需要处理上游分块终止/重复、推送断开。若上游不支持 streaming，允许有进展事件加最终输出，但不伪造流。

## 6. 密钥生命周期（P0 高优先级）

| 事件 | 要求 |
|---|---|
| 新增 Key | Browser → authenticated API，服务端加密后写入，前端只知道 `configured=true` |
| 编辑 Key | 空值保留旧 Key；显式 Replace 才更新；写入原子化 |
| 查看 | 永远不回显明文；不在本地存储缓存敏感数据 |
| 删除 | 立刻阻断未来新 Run；已启动 Run 的代理凭证失效策略明确 |
| 日志 | 请求头、异常堆栈、Pi Session、模型原始响应均须脱敏 |
| 备份 | Encrypted secret 和加密主密钥分离管理；恢复需正确密钥 |
| 全局模型 | 非管理员只能调用授权模型，不可获取管理员 Key |
| 失效/轮换 | 新连接测试、既有会话的下一轮明确报错，不悄悄向他人 Key 降级 |

Pi Worker 不应该持有用户长期服务商 Key。优先通过受限的 Model Gateway、一次 Run 有效的临时 token 调用；须证明此机制与 Pi SDK 的模型运行时接口可集成，若 P0 暂时无法做到，必须显式降级风险等级、只允许单用户受信本地执行，不能承诺强隔离。

## 7. Base URL 的 SSRF 悖论

本地用户有正当理由访问 `127.0.0.1`、`host.docker.internal` 和 LAN IP，但这些地址也是 SSRF 高频目标。建议：
- `deployment_admin` 可明确启用本机/LAN 模型端点；其他用户默认仅允许批准的远端域名。
- 验证 URL scheme、DNS 每次解析结果、地址类型、重定向、代理与 TLS；拒绝链接本地云元数据服务。
- 连接 Probe 与实际推理都走同一限制层，防止“测试时安全，运行时被重定向”。
- 默认不给 Skill 任意发 HTTP 的能力；模型网关的网络许可不应自动传给 Tool 的网络空间。

## 8. 路由与费用：MVP 不做复杂智能调度

选模型优先顺序：用户 Run 显式选择 > 当前 Workspace 默认 > 用户默认 > 管理员共享默认。更换模型须冻结在新 Run 的 ModelAlias 快照。失败时不静默改用其他 Key，因为用户可能有不同隐私政策与费用承担方。

成本数据取自真实 usage 或基于明确公开价格的估算；未知用量标注未知。不要把本机模型 Token 数直接映射为美元费用。

## 9. 失败矩阵与恢复动作

| 故障 | UI 错误 | 下一步 | 不应发生 |
|---|---|---|---|
| 401/403 | 密钥或权限不通过 | 修改 Key/授权 | 自动回显 Key |
| DNS/连接拒绝 | 无法访问目标主机 | 核查容器网络/端口 | 无限制后台重试 |
| TLS 失败 | 证书校验失败 | 检查代理与 CA | 默认关闭证书验证 |
| 404 model | 模型 ID 不存在或路径不匹配 | 修改 ID/协议 | 自动切到不同供应商 |
| 429 | 限流 | 按 Retry-After 和预算限额重试 | 无限排队扣费 |
| 5xx | 供应商故障 | 有界重试/手动切换 | 重放已产生副作用的 Tool |
| 不支持 Tool | 工具能力不足 | 标注 Chat-only 模式 | 假装完成文件任务 |
| Token 截断 | 输出未完整 | 降低分块或恢复上下文 | 标示 SUCCESS |
| 凭证轮换中 | 连接不可用 | 重试探测 | 强迫用户重建所有聊天 |

## 10. 验收（真实 provider + local mock 各一套）

AC-MOD-01：UI 可以完成保存、测试、删除，API/浏览器/日志无明文 Key。
AC-MOD-02：容器能访问明确配置的宿主机 Ollama；`localhost` 错误给出针对性解释。
AC-MOD-03：最小完成和 Tool Probe 分别有结果；不支持 Tool 的模型不能通过文件执行验收。
AC-MOD-04：无 `/models` 的兼容服务可手填 Model ID 成功调用。
AC-MOD-05：SSRF 探测、DNS 变化、重定向等测试不能越过部署策略。
AC-MOD-06：Key 失效/删除后，未经授权的未来 Run 被拒绝且用户得到明确修复路径。
