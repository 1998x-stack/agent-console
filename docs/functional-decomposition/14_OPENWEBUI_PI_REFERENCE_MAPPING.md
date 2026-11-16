# 14 — Open WebUI × Pi Agent 参考实现差异与取舍清单

> Draft v0.4 · 研究的是**应借鉴哪些交互和机制**，不是复制 Open WebUI 代码或声称二者天然兼容。事实依据为 2026-11-16 可访问的 Open WebUI / Pi 官方文档；下文标注 FACT（来源已核实）与 DESIGN（本项目建议）。

## 1. 产品定位的根本差异

**Open WebUI（FACT）**：以聊天作为统一入口，提供多模型连接、Knowledge、Prompts、Tools、Skills、模型预设以及分层权限。Workspace 是可组合资源空间；Skills 是通过 Markdown 定义的、可按需加载的指导内容。详见 https://docs.openwebui.com/features/workspace/ 和 https://docs.openwebui.com/features/workspace/skills/ 。

**Pi（FACT）**：核心是编码 Agent 的会话、模型/工具循环、文件工具、Skills/Extensions 与 SDK/RPC 接口。它可以嵌入自定义 Web 产品，且 ResourceLoader 允许宿主定制资源发现。详见 https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/sdk.md 。

**Agent Console（DESIGN）**：以真实的 Office/Code 任务为入口，采用 Open WebUI 风格的多模型 Web 体验，使用 Pi 进行 Agent 执行；并增加每用户可持久的 `/{user-id}/workspace`、执行沙箱、产物验证及 Skill Registry 版本/安装/分发。

## 2. 功能借鉴与差异矩阵

| 领域 | Open WebUI 官方能力（FACT） | Pi 官方能力（FACT） | Agent Console 目标设计（DESIGN） | Phase |
|---|---|---|---|---|
| First Run | Docker UI、首建管理员、模型连接 | CLI/SDK 独立启动 | Docker 首启后 Web 配模型，自动创建 Pi Worker Run | P0 |
| Model Connections | 管理 API Key、OpenAI-compatible/Ollama | ModelRuntime/模型选择 | Web BYOK+独立能力探测+短期代理凭证 | P0 |
| Chat | 多轮模型对话、历史、不同模型 | AgentSession、事件与会话持久 | Conversation 与 Run 分离，进展可回放 | P0 |
| Workspace | Models/Knowledge/Prompts/Tools/Skills 组合 | `cwd` + project resources | 真实 OS 工作目录和文件 ACL，用户可预览 | P0 |
| Tool Calling | 依赖模型/工具配置 | 内置 read/write/edit/bash 等 | 受 Tool Gateway + 沙箱 + 审批约束 | P0/P1 |
| Skills | Markdown/支持文件、版本历史、分享 | `SKILL.md` 与 ResourceLoader | 私有 Skill + digest 安装 + Store + Pi 有界加载 | P0/P1 |
| Skill Creator | 通过编辑或聊天创建技能 | 可从文件发现/编辑 | “Save as Skill”、安全清洗、回归测试 | P1 |
| Skill Import/Export | ZIP、`.skill`、JSON 等 | 文件系统资源 | 受限解析、来源、许可与内容摘要校验 | P1 |
| User Access | Roles/Groups/资源权限 | 不提供同等 Web ACL | RBAC+ABAC+Capability Grants | P0/P2 |
| Knowledge | 文件/RAG/知识库 | 工具读取文件 | P0 Workspace 文件，知识库/RAG 延后 | P2 |
| Prompt Presets | Prompt Template/模型预设 | Prompt templates/自定义资源 | 任务模板与 Skill 共享，独立资源类型 | P1 |
| Public Community | 技能社区发现与分享 | 本地项目扩展为主 | Remote Registry 作为独立可关闭后端 | P2 |
| Admin | 模型/用户/权限与安全设置 | 无独立 Web 管理台 | 本地实例治理、组织和公共治理分层 | P0/P2 |

官方来源：
- Open WebUI Quick Start：https://docs.openwebui.com/getting-started/quick-start/
- Open WebUI Skills：https://docs.openwebui.com/features/workspace/skills/
- Open WebUI Knowledge：https://docs.openwebui.com/features/workspace/knowledge/
- Open WebUI Chat：https://docs.openwebui.com/features/chat-conversations/
- Open WebUI Hardening：https://docs.openwebui.com/getting-started/advanced-topics/hardening/
- Pi SDK：https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/sdk.md

## 3. 借鉴的交互与保持独立的实现

### 建议借鉴

1. 单一 Web 工作台 + 左侧历史/Workspace/Skills 导航，用户无需切换产品完成模型、任务和技能操作。
2. 从 Web 管理 Provider，允许本地模型与远端兼容 API 并存。
3. Skill Markdown 编辑、文件树、版本历史、导入/导出、按需加载；普通用户拥有创作和分享能力。
4. 模型能力/工具/Skill 作为可组合的配置，但每次执行仍有清晰的当前资源快照。
5. 管理侧的系统设置和资源级 ACL 分离，不把“所有管理员都能查看每个人的资料”当默认。

### 刻意不照搬

1. **不把聊天历史当作文件执行状态源**：Pi Run/Step/Event 需要独立状态机和可恢复审计。
2. **不把 Skill Markdown 当作代码执行器**：代码需要实际 Tool、沙箱和权限。
3. **不在默认 Web 主进程执行未知 bash/Extension**：Pi 的原生工具/JS 扩展能触达运行进程的 OS 权限。
4. **不在 P0 直接复制 Open WebUI 的全部 Knowledge/RAG/语音/图像等功能**：先验证 Office/Code 最短闭环；过多模块会使调试成本指数上升。
5. **不把 Open WebUI 服务端 API 当成稳定的 Pi SDK 替代品**：本项目保持自有 Run/Skill/Workspace API 契约。
6. **不假定实际许可证授权任意复制 UI 代码**：如要直接复用 Open WebUI 源码/设计资源，必须单独审查许可证和商标；本文只作功能研究。

## 4. Open WebUI Skill 机制最值得借鉴的细节

其官方 Skills 文档明确：Skills 可在 Workspace 创建、编辑、Import/Export、共享，支持版本历史、按需加载及模型绑定；模型可访问某 Skill 仍受该用户资源访问权限约束。也明确了冲突保存的版本处理。**这个细节比“有个 Skill Store”更重要**。

我们的目标实现应考虑：
- UI 中提供版本差异、编辑冲突和可选恢复；下载回退和重新发布 Release 分开。
- Pi 只看到当前用户当前 Workspace 已被允许的技能；即使某个模型默认附带 Skill，权限不足时也要过滤。
- 对一份 Skill 的编辑保存必须和已安装 Release 分离，避免自动覆盖正在运行的资源。
- Skill 访问范围由业务 ACL 检查，Pi 的默认目录发现逻辑不是安全边界。

## 5. 哪些 Open WebUI 高级功能应该延后？

| 功能 | 延后原因 | 启动条件 |
|---|---|---|
| 企业级知识库/RAG | 索引质量、数据治理和权限复杂 | Office 文件读写使用数据表明需求 |
| 语音/实时音视频 | 与首发 Office/Code 任务完成率关系较弱 | 明确真实用户需求 |
| 图像生成 | 需要独立 Provider/生成资产生命周期 | Agent 文件工作流稳定 |
| 高级搜索引擎 | 与 Skill 搜索不完全同类 | Skill 数量/召回失败证据 |
| Agent 自动外部动作 | 高风险 Tool 审批和副作用恢复要求高 | Sandbox + Permission Gate |
| 复杂组织分享和公共市场 | 需要安全、审核、运营基础 | 首发本地/私有 Skill 复用有效 |

这不是否定相关能力，而是防止从一开始做一个“功能上看起来和 Open WebUI 一样多，但任何任务都无法可靠完成”的产品。

## 6. 验收式对照

AC-REF-01：模型配置、聊天、Workspace 和 Skill 在 Web 中可连贯使用，无需用户亲自操作 Pi CLI。
AC-REF-02：Pi 会话与 Run 事件有独立状态与持久化，刷新/重启后可恢复必要内容。
AC-REF-03：没有访问权限的 Skill 不因“模型绑定”而出现在 Pi 可用资源中。
AC-REF-04：Skill 更新/共享/版本回滚与安装版本的语义清晰，符合自身的不可变 Release 契约。
AC-REF-05：不为了追求功能表全面而开放不可信 Pi Extensions 和危险工具。
