# 02 — Web Client 信息架构、页面状态与交互推演

> Draft v0.4 · 产品参考 Open WebUI 的侧栏、模型选择和 Workspace/Skills；不复制其内部数据模型或 UI 代码。参考：[用户旅程](01_USERS_AND_JOURNEYS.md)、[模型设置](03_MODEL_ONBOARDING.md)、[Skill](06_SKILL_CREATOR_AND_STORE.md)。

## 1. Information Architecture：以“任务”为中心而不是“聊天气泡”

```text
App Shell
├── New Task                         # Agent 执行的统一入口
├── History                          # Conversation/Run 历史与恢复
├── Workspace                        # 文件树/上传/预览/产物
├── Skill Store                      # Explore / Installed
├── My Skills                        # Create / Drafts / Versions / Tests
├── Models                           # Provider / Model / Test / Defaults
├── Settings                         # Profile / Data / Backup / Privacy
└── Administration                   # 仅具有部署管理员权限者显示
```

**页面不要以 Office/Code 严格分割**：一个 Workspace 在同一任务中可能先阅读 README、然后写 Markdown 周报或生成报告。提供模式切换（General/Office/Code）作为“工具与呈现配置”，不是新建另一套账户/数据体系。

## 2. 任务主界面（桌面 Web）

- 左侧（可折叠）：Workspace 切换、历史会话、Skill Store、我的 Skill、Models。
- 顶部：当前 Workspace、模式、模型别名、模型连接健康/是否支持 Tool、任务运行状态；切换模型时说明是否影响当前会话。
- 中央：自然语言输入、附件、用户消息、Agent 输出、步骤卡片、审批请求；应把“正在读文件/等待工具/正在验证”与“模型在思考”区分。
- 右侧（可隐藏/全屏）：文件树、文件预览、Git Diff、终端输出、产物、失败诊断；小屏窄宽时改为选项卡或抽屉。
- 下方：取消、继续、重试、查看 Trace、下载结果；高风险操作的审批提示不得隐藏在折叠区。

**交互约束**：用户点击取消只表示“请求取消”，要等服务端回应才显示“已取消”。网络断线只影响画面订阅，不默认中断后台执行。持久 Run 状态由后端决定。

## 3. 首次使用向导

| Step | 画面内容 | 用户动作 | 错误状态 | 退出条件 |
|---|---|---|---|---|
| Setup | 本地数据目录/单机模式、创建管理员 | 创建账号 | 多标签页同时初始化 | 初始化被一次性保护 |
| Provider | 模型协议与 Base URL/Key | Save & Test | DNS、401、404、timeout | 至少一个通过最小生成 |
| Model | 可用模型/手填 Model ID、Tool 能力 | Choose Default | 不支持 Function Call | 标注能力，不假装支持 |
| Workspace | 推荐样本任务、示例文件 | Run Sample | runner 尚未就绪 | 第一条真实 Pi Run |
| Skill | 内置技能列表、权限说明 | Install sample | 离线包损坏 | Installation 固定版本 |

没有模型时可以浏览 Skill Store、查看已有文档，但 Agent 输入框需要明确的“添加模型才能执行”操作，不应返回含糊的 500。

## 4. Agent 对话的交互状态表

| 后端状态 | UI 显示 | 可操作 | 不可操作 |
|---|---|---|---|
| CREATED/QUEUED | 已接收/队列等待、可取消 | Cancel | 假装执行 |
| PLANNING/RUNNING | 模型输出与步骤实时进展 | 查看细节、申请取消 | 隐式重发 |
| WAITING_APPROVAL | 具体拟执行动作、目标、影响、有效期 | Approve/Deny | 无范围一键允许 |
| WAITING_TOOL | 工具运行、超时/进度 | Cancel | 无限转圈无诊断 |
| VALIDATING | 正在校验产物，附检查项 | 查看日志 | 把未验证当成功 |
| SUCCEEDED | 实际产物、校验证据、重新复用 | 下载/保存 Skill | 误导性“一定正确” |
| FAILED | 失败分类、已完成副作用、保留产物 | 重试安全部分/查看日志 | 静默清空上下文 |
| CANCELED | 已取消，列出现有文件/副作用 | 新任务或继续聊 | 声称完全回滚 |

注意状态机中的 `WAITING_TOOL`、`VALIDATING` 有额外的 heartbeat/超时保护；UI 的任务阶段必须来自业务事件，不仅是最后一个 token。

## 5. Skill Store 入口及 Creator 体验

**Explore**：搜索框、分类（Office/Code/General）、来源（内置/本地/社区）、安装兼容性、风险标识。详情页至少展示：名称、解决问题、示例、来源作者、可信级别、最近版本、需要工具/网络/文件权限、安装按钮、风险说明。

**Installed**：固定版本、是否启用、是否有更新、是否可用于当前模式、使用次数与失败（若用户授权收集）。禁用不是卸载；卸载不是全局下架。

**My Skills**：草稿、已发布私人 Release、版本历史、Diff、测试结果、导入/导出、Fork。用户编辑的是自身 Skill，不需要申请平台管理员资格。

任务结果页加入 **Save as Skill**；若一段对话涉及敏感文件，保存前必须提供信息脱敏预览与“禁止包含此文件/消息”选项。

## 6. 模型设置页面细节

表单分四块：身份（名称/用途）、接口（协议/Base URL）、凭证（API Key 密码框/保存后只显示遮罩）、能力（Model ID/工具调用/上下文窗口显式或未知）。连接测试输出分步骤结果，不要只显示绿色“已连接”。

两个按钮语义不同：**Save** 保存配置但可以处于未验证状态；**Test** 发起真实网络请求并显示诊断。删除 Connection 前先展示正在依赖的会话/预设模型影响；保存新 Key 应原子替换，不泄漏旧值。

## 7. 文件与 Diff 的界面

- 文件树以 Workspace 根为界，禁止显示宿主机绝对路径；支持复制相对路径/预览/下载、上传进度、目录过滤。
- 多文件编辑结果进入 Review Changes，逐文件 Diff、冲突标记、保留/拒绝变更。禁止“已运行模型”就自动写回主分支。
- 大文件需分页/懒加载；二进制文件显示类型/大小/下载，不尝试当纯文本解码。
- 办公文件展示“生成中、已生成待校验、校验通过、校验失败”，将文件存在与语义正确区分。

## 8. 移动端/无障碍/性能

P0 以桌面 Web 为主，但必须：键盘导航、aria 语义（实现时）、聚焦不被流式内容抢走、屏幕阅读器能感知审批、长输出虚拟列表、防止 10k 事件导致主线程卡顿。窄屏隐藏右侧面板但保留“查看结果”。避免大面积动画充当任务进展。

## 9. UX 负例与防误导

- 点击两次“运行”造成双 Run：使用 idempotency key / 禁用重复提交 + 可恢复查询。
- “审批弹窗”过期后仍可点击：后端 409/expired，UI 刷新动作。
- 切换 Workspace 后继续渲染前一个用户任务：清除订阅与校验事件上下文。
- Skill 已更新但正在运行旧版本：显示“本次运行固定版本 A；下次运行使用 B”。
- Provider Key 已过期却仍显示绿色：状态标注最后检查时间，失败后降级。
- 删除模型后老会话打不开：历史可以查看；再发起时要求选择替代模型。
- 同名文件上传两次：显示覆盖、重命名、新版本三种策略，默认为重命名或拒绝，不静默覆盖。

## 10. 客观 UX 验收

AC-UX-01 从空数据卷到首个成功 Run，可完整通过浏览器操作，无人工修改配置文件。
AC-UX-02 网络断线后重连，同一 Run 不重复显示工具副作用、不丢关键终态事件。
AC-UX-03 审批必须明确动作/目标/风险，过期审批不能重复执行。
AC-UX-04 文件预览和终端输出即使很大也不会使浏览器失去响应（在指定性能测试 fixture 上评测）。
AC-UX-05 Skill 禁用后新 Run 不选择，已完成历史仍显示原 Skill 与版本。
AC-UX-06 Office/Code 模式切换后 Workspace 归属保持一致，工具策略按新 Run 快照应用。
