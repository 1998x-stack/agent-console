# 13 — 全量功能清单、端侧归属、阶段及验收追踪矩阵

> Draft v0.4 · 功能层面的设计清单，不表示已实现。优先级：P0=首次真实自托管闭环；P1=个人生产/创作能力；P2=多人/公共生态；P3=高级功能。所有标记均为 TARGET / NOT IMPLEMENTED，除非后续 PR 提供运行证据。

## 1. 功能归属编码

- **C**：普通用户 Client（也包含 Creator Studio）。
- **A**：本地 Deployment Admin。
- **O**：未来组织管理员。
- **G**：公共 Registry Governance。
- **S**：自动执行的服务/Worker，不是独立页面。
- **V**：需要后台策略控制但 UI 也可显示。

数据域：`User/Workspace`、`Conversation/Run`、`ModelConnection`、`Skill/Release/Listing/Installation`、`Artifact`、`Policy/Approval/Audit`。字段和事件详见 [08](08_DATA_API_CONTRACTS.md)。

## 2. 首次部署与模型（15 项）

| ID | 功能 | 端 | Phase | 验收入口 |
|---|---|---|---|---|
| F-001 | Docker Compose 冷启动/健康检查 | A/S | P0 | AC-OPS-01 |
| F-002 | 首次管理员单次初始化 | C/A | P0 | AC-SEC-07 |
| F-003 | 本机端口/网络配置指引 | A | P0 | AC-OPS-01 |
| F-004 | 基础账户登录与会话恢复 | C | P0 | AC-J01 |
| F-005 | 新增 OpenAI-compatible 模型连接 | C | P0 | AC-MOD-01 |
| F-006 | API Key 加密与遮罩 | C/S | P0 | AC-MOD-01 |
| F-007 | Base URL 联通/鉴权测试 | C/S | P0 | AC-MOD-02 |
| F-008 | Model ID 手动添加/列表发现 | C/S | P0 | AC-MOD-04 |
| F-009 | 最小真实模型生成探测 | C/S | P0 | AC-MOD-03 |
| F-010 | Tool Calling 能力探测 | C/S | P0 | AC-MOD-03 |
| F-011 | 模型默认选择/别名 | C | P0 | AC-MOD-03 |
| F-012 | 本机 Ollama/宿主机连接引导 | C/A | P0 | AC-MOD-02 |
| F-013 | Key 轮换/删除/失效状态 | C | P1 | AC-MOD-06 |
| F-014 | 组织共享模型权限 | O/A | P2 | AC-SEC-01 |
| F-015 | 多模型自动路由/容灾 | C/S | P3 | 单独实验 |

## 3. Agent UI、Pi 任务与会话（15 项）

| ID | 功能 | 端 | Phase | 验收入口 |
|---|---|---|---|---|
| F-101 | New Task/历史记录/继续聊天 | C | P0 | AC-PI-03 |
| F-102 | Office/Code/General 执行配置 | C | P0 | AC-J02/J03 |
| F-103 | 实时正文流与步骤状态 | C/S | P0 | AC-UX-02 |
| F-104 | Pi SDK Worker 真实执行 | S | P0 | AC-PI-01/02 |
| F-105 | Server-signed RunSpec | S | P0 | CT-01 |
| F-106 | Run/Step/Event 数据持久化 | S | P0 | CT-08 |
| F-107 | SSE Last-Event-ID 重连 | C/S | P0 | AC-PI-05 |
| F-108 | 请求幂等/重复点击保护 | C/S | P0 | CT-03 |
| F-109 | 取消、失败、超时、错误分类 | C/S | P0 | AC-PI-04/06 |
| F-110 | Pi 会话持久化/冷重启恢复 | C/S | P0 | AC-PI-03 |
| F-111 | 模型/Tool/Skill Snapshot | S | P0 | AC-PI-07 |
| F-112 | 工具调用可见与确认 | C/S | P0 | AC-UX-03 |
| F-113 | 受控文件写入与差异审查 | C/S | P1 | AC-WS-05 |
| F-114 | 高风险命令审批/受限 Bash | C/S | P1 | AC-SEC-02 |
| F-115 | 外部系统执行/PR/邮件操作 | C/S | P2 | CT-04 |

## 4. Workspace、文件和产物（14 项）

| ID | 功能 | 端 | Phase | 验收入口 |
|---|---|---|---|---|
| F-201 | 为当前用户安全创建 Workspace | S | P0 | AC-WS-01 |
| F-202 | `/{user-id}/workspace` 逻辑映射 | S | P0 | AC-WS-02 |
| F-203 | 文件树、路径导航和预览 | C | P0 | AC-UX-04 |
| F-204 | 上传文件/类型检查 | C/S | P0 | AC-J02 |
| F-205 | 下载真实已生成 Artifact | C | P0 | AC-WS-04 |
| F-206 | 文件/Artifact 哈希与版本归属 | S | P0 | CT-05 |
| F-207 | 任务只读挂载与用户隔离 | S | P0 | ADV-01/02 |
| F-208 | Office CSV/Markdown 文件加工 | C/S | P0 | Office-O1 |
| F-209 | Code 仓库只读问答 | C/S | P0 | Code-C1 |
| F-210 | Docker 重启后文件持久 | S | P0 | AC-WS-01 |
| F-211 | Git Worktree/Review Changes | C/S | P1 | Code-C2 |
| F-212 | 文件冲突解决/原子写回 | C/S | P1 | AC-WS-03 |
| F-213 | PDF/XLSX 更多格式转换 | C/S | P1 | Office-O1/O2 |
| F-214 | 组织共享文件/配额与策略 | O/S | P2 | AC-SEC-01 |

## 5. Skill Store 与创作者（18 项）

| ID | 功能 | 端 | Phase | 验收入口 |
|---|---|---|---|---|
| F-301 | 离线内置 Skill 列表 | C | P0 | AC-SK-01 |
| F-302 | 分类/搜索/详情/来源显示 | C | P0 | AC-SK-01 |
| F-303 | 查看版本与权限声明 | C | P0 | AC-SK-02 |
| F-304 | 安装固定 Release | C/S | P0 | AC-SK-02 |
| F-305 | Installed 启用/禁用/卸载 | C | P0 | AC-SK-05 |
| F-306 | Pi ResourceLoader 只加载授权 Skill | S | P0 | AC-PI-07 |
| F-307 | 运行记录显示 Skill digest | C/S | P0 | AC-SK-02 |
| F-308 | Skill Draft 创建/自然语言生成 | C | P1 | AC-J04 |
| F-309 | Skill 编辑器/支持文件 | C | P1 | AC-SK-04 |
| F-310 | 安全 ZIP/.skill 导入 | C/S | P1 | AC-SK-03 |
| F-311 | 静态校验/敏感信息扫描 | C/S | P1 | AC-SK-07 |
| F-312 | 沙箱测试和正负例 Trigger Eval | C/S | P1 | AC-SK-08 |
| F-313 | 私人 Release 与版本历史 | C | P1 | AC-SK-04 |
| F-314 | 从成功任务保存为 Skill | C | P1 | AC-J04 |
| F-315 | Fork/导出/来源追踪 | C | P1 | AC-SK-07 |
| F-316 | 远程社区 Registry 访问/导入 | C/S | P2 | ADV-12 |
| F-317 | 团队/公共 Listing 与审核 | C/O/G | P2 | AC-SK-05 |
| F-318 | 创作者 Unlist/安全 Revoke/恢复 | C/G | P2 | AC-SK-06 |

## 6. 管理、安全与运维（17 项）

| ID | 功能 | 端 | Phase | 验收入口 |
|---|---|---|---|---|
| F-401 | 实例健康与错误状态 | A | P0 | AC-OPS-05 |
| F-402 | Provider SSRF 防护/LAN 例外 | A/S | P0 | AC-MOD-05 |
| F-403 | API/Auth/Workspace 对象级校验 | S | P0 | ADV-01/07 |
| F-404 | Key 不能在 Trace/工具/Session 中泄露 | S | P0 | ADV-10 |
| F-405 | 禁用任意未可信 Pi Extensions | A/S | P0 | ADV-05 |
| F-406 | 阻断越权读写和非法脚本 | A/S | P0 | ADV-09 |
| F-407 | 审批对象级授权与过期 | C/S | P0 | ADV-08 |
| F-408 | 用户私密数据默认本地存储 | C/S | P0 | AC-OPS-02 |
| F-409 | 运行日志与敏感信息脱敏 | A/S | P0 | AC-OPS-03 |
| F-410 | 数据备份与恢复演练 | A | P1 | AC-OPS-04 |
| F-411 | 运行容量与磁盘空间诊断 | A | P1 | AC-OPS-05 |
| F-412 | 新的沙箱写入/网络安全门禁 | A/S | P1 | ADV-09 |
| F-413 | 多用户注册/成员/Workspace ACL | O/A | P2 | AC-SEC-01 |
| F-414 | 组织 Model/Skill Policy | O | P2 | AC-SEC-01 |
| F-415 | 公共市场审核/举报/申诉 | G | P2 | AC-SEC-06 |
| F-416 | 安全紧急 Revoke/通知 | G/A | P2 | AC-SEC-06 |
| F-417 | 用量/模型成本/治理看板 | A/O | P3 | Eval Metrics |

## 7. 排序注意事项

- 上述 **79 项**（15 + 15 + 14 + 18 + 17）是设计库存，不是 79 个独立开发工单；同一能力可能由一个 PR 完成多个 F ID。
- P0 的文件/密钥/权限保护为 **gate**，不是因为“用户看不到”就可延后。
- P1 的脚本执行与高危写入即使功能完成，也必须有相应安全负测才能启用。
- P2 的公共治理只有远程 Registry 真正开放时才需要；没有公共服务时不必造虚拟审核员后台。
- 某个功能如果“简单”但必须在所有新 Run 上生效（例如禁用 Skill），优先验证缓存失效和版本 Snapshot，而不是只改按钮。
- 功能最终状态由测试结果与真实运行证据更新，不得以“文档已写”标 DONE。

## 8. 启动阶段看板建议

每项 F ID 跟踪：`status = NOT_STARTED / IN_PROGRESS / BLOCKED / IMPLEMENTED_UNVERIFIED / VERIFIED`，`owner`、`PR`、`test_ids`、`evidence_link`、`last_verified_sha`。验收应绑定到具体 Commit 与环境镜像摘要，避免修改后沿用陈旧的“测试通过”记录。
