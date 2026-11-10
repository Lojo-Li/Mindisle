# Mindisle（SoulStation）C 模块端到端测试报告

> 模块范围：心理咨询预约、取消预约、预约状态管理、咨询评价与反馈
> 报告日期：2026-11-09　｜　执行角色：高级软件测试工程师
> 测试性质：**真实接口调用 + 真实浏览器交互 + 数据库断言**，非静态代码分析
> 凭据声明：本报告不包含任何账号、密码、Token、密钥或真实用户个人信息；测试账号为临时隔离账号，密码运行时随机生成且未落盘，令牌仅存内存。

---

## 一、测试环境

### 1.1 实际探活结果

| 组件 | 配置 | 探活方式 | 结果 |
|---|---|---|---|
| OS / Shell | Windows / PowerShell | — | 正常 |
| Docker | Desktop 29.1.3 | `docker info` | 正常 |
| MySQL | 8.0.46，容器 `soulstation-mysql`，主机端口 `3307`，库 `soulstation` | `docker ps` + 直连查询 `SELECT VERSION()` | healthy，连接成功 |
| 数据卷 | `backend_mysql-data` | `docker volume ls` | 存在且保留 |
| FastAPI | `http://127.0.0.1:8000` | `GET /openapi.json` | 200，共 106 条路径 |
| Vue | `http://127.0.0.1:5173` | `GET /`、`GET /counselor` | 200，Vite dev server |
| 前端代理 | `/api` → 8000 | `GET http://127.0.0.1:5173/api/counselor/list?page=1&page_size=1` | 200，返回真实业务 JSON |
| Redis | 用户说明为内存回退模式 | 未重新探测，按用户提供的环境信息记录 | 不影响 C 模块结论 |
| RAG 预热 | 存在 NumPy 兼容问题 | 用户明确排除 | 不在本次范围 |
| 浏览器自动化 | 系统 Chrome/Edge 存在；项目本身**无** Playwright/Cypress/Vitest | 隔离目录安装 Playwright 1.64.1，以 `channel="chrome"` 复用系统 Chrome | 可用，已执行 |

数据库连接凭据只从 `backend/.env` 的 `DATABASE_URL` 在内存中读取，**未输出、未写入任何文件**。测试脚本使用后端自带 `.venv`（Python 3.12.4 / requests / pymysql / SQLAlchemy / bcrypt）。

### 1.2 环境异常与无损恢复（真实记录）

开始执行前发现：Docker Desktop 未运行、3307 / 8000 / 5173 全部无监听，`docker` 命令报 daemon 不可达，前端后端均不可访问。恢复动作：

1. 启动 Docker Desktop（GUI 最小化启动），等待 daemon 就绪；
2. 现有容器 `soulstation-mysql` 因 `restart: always` 自动恢复，数据卷 `backend_mysql-data` 原样保留；
3. 在 `backend/` 目录后台启动 `uvicorn app.main:app --host 127.0.0.1 --port 8000`；
4. 在 `frontend/` 目录后台启动 `npm run dev`。

**未删除、清空、重建任何数据库或 Docker 数据卷，未修改任何业务代码或配置。** 恢复后再次核对库内基线：`users=2、counselors=1、appointments=0、consultation_reviews=0`，与用户交付时的状态一致。

### 1.3 测试数据与隔离策略

| 项 | 说明 |
|---|---|
| 标识前缀 | 接口测试 `E2E_C_`，浏览器测试 `E2E_UI_`（账号、咨询师档案、预约人姓名均带前缀） |
| 账号 | 接口测试 4 个（学生A、学生B、咨询师甲、咨询师乙）；浏览器测试 2 个（UI 学生、UI 咨询师） |
| 邮箱域 | RFC 2606 保留域，不触达任何真实用户 |
| 造数方式 | 只执行 `INSERT` 新增行；**未 UPDATE / DELETE 任何既有行** |
| 认证 | 全部通过真实 `POST /api/auth/login` 取得 token（浏览器链路通过登录页 UI 取得） |
| 清理 | 按本次记录的主键精确 `DELETE`，依赖顺序：消息 → 评价 → 预约 → 通知 → 咨询师 → 用户 |
| 副作用说明 | 项目邮件服务配置可用且 SMTP 可达，创建/取消预约会向保留域地址发起发信尝试；未向任何真实用户发信 |
| 最终校验 | `TC-049` 通过；浏览器测试后复查：所有 C 模块表行数与基线完全一致，`E2E_C_%` / `E2E_UI_%` 残留账号 0 条 |

---

## 二、实际功能清单（来自运行时 OpenAPI + 源码 + 实测）

### 2.1 已实现且实测可用

| 能力 | 接口 | 实测结论 |
|---|---|---|
| 咨询师列表 / 详情 | `GET /api/counselor/list`、`GET /api/counselor/{id}` | 可用，与 `counselors` 表一致（TC-001/002） |
| 可预约时段查询 | `GET /api/counselor/{id}/slots?date=` | 可用，硬编码 09:00–19:00 共 10 个整点（TC-003） |
| 咨询师评价列表 | `GET /api/counselor/{id}/reviews` | 可用（TC-017） |
| 创建预约 | `POST /api/appointment/create` | 可用，真实落库（TC-005/006） |
| 学生预约列表 / 详情 | `GET /api/appointment/user/list`、`GET /api/appointment/{id}` | 可用（TC-007/008/011） |
| 取消预约 | `POST /api/appointment/{id}/cancel?reason=` | 可用，写入 `cancel_reason` / `cancelled_at`，时段释放（TC-020/021/022） |
| 咨询师订单列表 | `GET /api/consultation/counselor/orders` | 可用（TC-009） |
| 咨询师接受 / 拒绝 | `POST /api/consultation/order/{id}/handle`（`agree`/`reject`） | 可用（TC-010/023） |
| 咨询推进 | `POST /api/consultation/{id}/message` → `in_progress`；`POST /api/consultation/{id}/end` → `completed` | 可用（TC-013/014） |
| 提交评价与反馈 | `POST /api/appointment/{id}/review` | 可用，真实落库（TC-015） |
| 咨询师备注 / 文件上传 | `POST /api/consultation/{id}/note`、`POST /api/consultation/upload` | 代码存在，本次未纳入执行范围 |
| 浏览器端链路 | `/counselor`、`/login`、`/counselor/orders` | 真实 Chrome 渲染与交互验证通过（UI-01~05） |

### 2.2 状态流转（实测确认）

```
pending ──(咨询师 agree)──> confirmed ──(首条咨询消息，隐式)──> in_progress ──(/end)──> completed
   │                                                                                    │
   ├──(学生 cancel)──────────────────────────────> cancelled                     └──(提交评价)
   └──(咨询师 reject，reason 写入 cancel_reason)──> cancelled
```

- 无独立「开始咨询」接口，`confirmed → in_progress` 由首条消息隐式触发（TC-013）。
- 无 `rejected` 状态，拒绝与用户取消共用 `cancelled`（TC-023）。
- `refunded` 仅在枚举/文档出现，代码中无任何写入路径。
- 取消仅学生侧；咨询师无取消接口（TC-043 验证咨询师取消被拒）。

### 2.3 角色权限实现（实测）

- 认证：`POST /api/auth/login` → `data.token`；`Authorization: Bearer <token>`。
- C 模块**不读 JWT 的 `role`**：`api/counselor/__init__.py:25-40` 只取 `sub`；`api/consultation/__init__.py:43-59` 通过 `counselors` 表是否存在 `user_id` 记录判定 `counselor/user`。
- 归属校验：预约详情、取消、评价、消息、结束咨询均按 `appointments.user_id` / `counselor_id` 比对。
- 实测结论：**越权数据隔离有效**（10 个权限用例中，所有越权请求均未改动数据库、未泄漏他人订单），但**错误码契约不符合预期**（见 BUG-04 / BUG-07）。

### 2.4 关键表结构（运行时实测）

`counselors`、`appointments`、`consultation_reviews`、`consultation_messages`、`counselor_inquiries`、`inquiry_messages`、`notifications`，关联 `users`。

- `appointments.status` 枚举 6 值；`appointment_no` 唯一索引；**无 `(counselor_id, appointment_date)` 唯一索引**。
- `consultation_reviews` 运行时存在唯一索引 `uk_appointment_review (appointment_id)`（与 `sql/init.sql:286` 一致；`sql/migrate.sql:205-226` 版本缺少该唯一键，存在 DDL 分歧）。
- **无排班表**：可预约时段完全由代码生成，占用情况由 `appointments.appointment_date` 等值查询推导。

---

## 三、测试用例与执行结果

### 3.1 接口自动化测试（50 例，脚本 `e2e_c_module/run_e2e.py`）

| 用例 | 场景 | 预期 | 实际 HTTP | 结果 |
|---|---|---|---|---|
| TC-000 | 隔离账号创建并真实登录（4 角色） | 全部 200 取得 token | 200 | PASS |
| TC-001 | 学生查看咨询师列表 | 200，含隔离咨询师且与 DB 一致 | 200 | PASS |
| TC-002 | 学生查看咨询师详情与定价 | 200，字段与 `counselors` 一致 | 200 | PASS |
| TC-003 | 学生查看可预约时间 | 10 个整点时段初始全可用 | 200 | PASS |
| TC-004 | 非法参数：slots 日期格式错误 | 400 日期格式错误 | 400 | PASS |
| TC-005 | 学生创建预约并写入数据库 | 200，`pending`、价格/外键正确 | 200 | PASS |
| TC-006 | 接口响应与 DB 行一致 | `appointment_no/status/user_id/price` 一致 | 200 | PASS |
| TC-007 | 学生查询预约状态（pending） | 列表含该单，状态与 DB 一致 | 200 | PASS |
| TC-008 | 学生查询预约详情 | 200，含咨询师信息 | 200 | PASS |
| TC-009 | 咨询师查看待处理订单 | 200，含该单 | 200 | PASS |
| TC-010 | 咨询师接受预约 | `confirmed` + `confirmed_at` | 200 | PASS |
| TC-011 | 学生查询预约状态（confirmed） | 筛选结果与 DB 一致 | 200 | PASS |
| TC-012 | 重复处理同一订单 | 400，状态不变 | 400 | PASS |
| TC-013 | 首条消息推进 `in_progress` | 200，状态与消息落库 | 200 | PASS |
| TC-014 | 结束咨询 `completed` | 200，`completed_at` 非空 | 200 | PASS |
| TC-015 | 咨询完成后提交评价与反馈 | 200，`consultation_reviews` 落库 | 200 | PASS |
| **TC-016** | **评价后咨询师评分统计一致性** | `rating/review_count` 与聚合一致 | — | **FAIL（BUG-02）** |
| TC-017 | 咨询师评价列表可查询 | 200，含本次评价 | 200 | PASS |
| TC-018 | 重复评价 | 400，仍只有 1 条评价 | 400 | PASS |
| TC-019 | 取消已完成预约 | 400，状态不变 | 400 | PASS |
| TC-020 | 学生取消预约 | `cancelled` + 原因 + 时间戳 | 200 | PASS |
| TC-021 | 取消后时段释放 | 10:00 重新可用 | 200 | PASS |
| TC-022 | 已取消时段可再次预约 | 200，允许重订 | 200 | PASS |
| TC-023 | 咨询师拒绝预约 | `cancelled` + 拒绝原因 | 200 | PASS |
| TC-024 | 同一咨询师同一时刻重复预约 | 400「该时段已被预约」，不新增行 | 400 | PASS |
| **TC-025** | **相邻半小时重叠时段** | 应拒绝（每单 60 分钟） | **200** | **FAIL（BUG-03）** |
| TC-026 | 非法咨询方式 `chat` | 422 | 422 | PASS |
| TC-027 | 预约时间为过去 | 400 | 400 | PASS |
| TC-028 | 预约时间格式错误 | 400 | 400 | PASS |
| TC-029 | 不存在的咨询师 | 400 | 400 | PASS |
| **TC-030** | **带时区 ISO 时间（`Z`）** | 4xx 客户端错误 | **500** | **FAIL（BUG-05）** |
| TC-031 | 分页 `page=0` | 422 | 422 | PASS |
| TC-032 | 评分 `rating=6` | 422 | 422 | PASS |
| TC-033 | 评分 `rating=0` | 422 | 422 | PASS |
| TC-034 | 未完成预约提交评价 | 400 | 400 | PASS |
| TC-035 | 预约改期（功能存在性验证） | 确认是否实现 | 405 / 404 | **FEATURE_GAP** |
| **TC-036** | **学生B 读取学生A 预约详情** | 403，DB 不变 | **500** | **FAIL（BUG-04）** |
| **TC-037** | **学生B 取消学生A 预约** | 403，DB 不变 | **400** | **FAIL（BUG-07）** |
| **TC-038** | **学生B 替学生A 提交评价** | 403，DB 不变 | **400** | **FAIL（BUG-07）** |
| TC-039 | 未携带 token 访问预约详情 | 403 | 403 | PASS |
| **TC-040** | **学生访问咨询师订单列表** | 403，无数据泄漏 | **500** | **FAIL（BUG-04）** |
| **TC-041** | **学生接受/拒绝预约** | 403，DB 不变 | **500** | **FAIL（BUG-04）** |
| **TC-042** | **学生访问 `/appointment/counselor/list`** | 403，无数据泄漏 | **500** | **FAIL（BUG-04 / BUG-06）** |
| TC-043 | 咨询师取消学生预约 | 拒绝，DB 不变 | 400 | PASS |
| TC-044 | 学生B 读取学生A 咨询消息 | 拒绝，无内容 | 400 | PASS |
| TC-045 | 咨询师乙处理咨询师甲订单 | 拒绝，状态保持 `pending` | 400 | PASS |
| TC-046 | 咨询师乙订单列表不含甲的订单 | 200 且不含 | 200 | PASS |
| **TC-047** | **咨询师查看自己收到的预约列表** | 200，返回名下订单 | **500** | **FAIL（BUG-01）** |
| TC-048 | 数据库一致性总检 | 无孤儿/重复/非法状态 | — | PASS |
| TC-049 | 隔离数据清理与基线恢复 | 全部表回到基线 | — | PASS |

> 完整请求/响应（脱敏）与每一步 DB 快照保存在 `e2e_c_module/results.json`。

### 3.2 浏览器端到端测试（6 例，Playwright + 系统 Chrome，脚本 `e2e_c_module/browser_e2e.py`）

| 用例 | 场景 | 实测结果 | 结果 |
|---|---|---|---|
| UI-01 | 打开 `/counselor`，验证咨询师卡片由真实接口数据渲染 | DOM 出现隔离测试咨询师名称，无 `pageerror` | PASS |
| UI-02 | 登录页 `#account` / `#pwd` / `#submitBtn` 真实登录 | `sessionStorage` 写入 token，跳转 `/workspace/home` | PASS |
| UI-03a | 用浏览器会话令牌创建预约 | 200，返回 `appointment_no` | PASS |
| UI-03b | 打开 `/counselor/orders` 查看预约状态 | DOM 显示预约编号与「待确认」 | PASS |
| UI-04 | 点击「取消预约」并在确认框确认 | DB `status=cancelled`，页面出现「已取消」 | PASS |
| UI-05 | 全新上下文未登录访问 `/counselor/orders` | 重定向 `/login` | PASS |

> 结论：学生端「浏览咨询师 → 登录 → 预约 → 查看状态 → 取消」主链路在真实浏览器中闭环可用；前端未暴露后端接口层的缺陷。

### 3.3 执行统计

| 类别 | 用例数 | 通过 | 失败 | 功能缺失确认 | 阻塞 | 未执行（已计划） |
|---|---:|---:|---:|---:|---:|---:|
| 接口自动化测试 | 50 | 39 | 10 | 1 | 0 | 0 |
| 浏览器端到端测试 | 6 | 6 | 0 | 0 | 0 | 0 |
| **合计** | **56** | **45** | **10** | **1** | **0** | **0** |

- 断言型用例通过率 = 45 / (45+10) = **81.8%**；含功能缺失确认的总体完成率 = 56/56 已执行。
- 「未执行」口径说明：上表指**已列入测试计划的用例**，全部执行完毕。另有「计划外未验证项」见第七节（静态线索 9 项）、以及用户明确排除的 RAG 预热 1 项；这些不计入通过率，也未被记为通过。
- 无阻塞用例：环境中断已通过无损恢复解决，未导致任何用例跳过。

---

## 四、Bug 清单与优先级

> 优先级口径：**P1** 影响核心业务正确性/主接口不可用；**P2** 影响错误契约、异常输入或辅助功能；**P3** 语义/体验问题，不影响安全与数据。

### BUG-01〔P1〕咨询师查看自己预约列表接口恒定 500

- **关联用例**：TC-047
- **复现步骤**：以咨询师甲账号 → `GET /api/appointment/counselor/list?page=1&page_size=50`
- **请求**：`GET /api/appointment/counselor/list`（Bearer，已脱敏）
- **响应**：`500 {"detail":"获取咨询师预约列表失败: 'Appointment' object has no attribute 'user'"}`，耗时 26ms
- **数据库变化**：该咨询师名下已有 8 条预约，数据正常；接口未改动任何行
- **错误原因**：`backend/app/services/counselor_service.py:785-792` 访问 `appt.user`，但 `backend/app/models/counselor.py:111-112` 的 `Appointment` 只定义 `counselor`、`review` 两个关系，没有 `user` 关系。路由 `api/counselor/__init__.py:437-442` 把异常包装为 500。后端运行日志同样记录该错误。
- **修复建议**：给 `Appointment` 增加 `user = relationship("User")`（或在服务层显式 join `users` 取昵称/邮箱），并为该列表接口补回归测试。需注意 `/api/consultation/counselor/orders` 是可用替代路径，前端当前使用后者，故线上页面暂未暴露该问题。

### BUG-02〔P1〕提交评价后咨询师评分与评价数不更新（数据不一致）

- **关联用例**：TC-016
- **复现步骤**：完成一次咨询 → `POST /api/appointment/{id}/review`，`{"rating":4.5,"tags":["专业","耐心"],"content":"...","is_anonymous":true}` → 查询 `counselors` 与 `consultation_reviews`
- **请求/响应**：评价接口 `200 {"code":200,"message":"评价提交成功","data":{...}}`
- **数据库变化**：`consultation_reviews` 新增 1 行（`rating=4.5`），但 `counselors.rating=5.0`、`review_count=0`；实际聚合应为 `AVG=4.5`、`COUNT=1`
- **错误原因**：`counselor_service.py:923` `db.add(review)` 后，`:931-936` 立即查询全部评价重算统计；会话工厂 `core/database.py:49` 为 `autoflush=False`，新评价尚未进入数据库，统计永远基于旧数据（首条评价时 `all_reviews` 为空，连默认 5.0 都不更新）。
- **修复建议**：重算前 `db.flush()`；或改用聚合 SQL 并在提交后刷新；同步修正历史数据（一次性回填脚本）。补充「提交评价 → 咨询师详情/列表评分」的集成断言。

### BUG-03〔P1〕时间冲突只判「完全相等」，允许时长重叠的重复占用

- **关联用例**：TC-025（TC-024 的等值冲突判定正常）
- **复现步骤**：同一咨询师先创建 `2026-11-12 12:00:00`，再创建 `2026-11-12 12:30:00`
- **请求**：`POST /api/appointment/create`，`{"counselor_id":<测试咨询师>,"consultation_type":"video","appointment_date":"2026-11-12 12:30:00",...}`
- **响应**：`200 {"code":200,"message":"预约创建成功","data":{"id":14,"duration":60,"status":"pending",...}}`
- **数据库变化**：两条 `pending` 预约同时存在，区间 `12:00–13:00` 与 `12:30–13:30` 重叠 30 分钟；`overlapping_active_rows=2`
- **错误原因**：`counselor_service.py:569-576` 与 `:122-169` 仅以 `Appointment.appointment_date == 传入时间` 判冲突，完全忽略 `duration=60`；`sql/init.sql:261-264` 也没有 `(counselor_id, appointment_date)` 唯一索引，连等值并发都无 DB 保障。
- **修复建议**：改为区间重叠判断 `[start, start+duration)`；或在 schema 层强制整点对齐并配合 DB 唯一索引 + 事务/行锁；同时让 `slots` 与 `create` 共用同一套冲突判定函数，避免两处逻辑漂移。

### BUG-04〔P2〕路由内 `HTTPException` 被 `except Exception` 吞掉，权限拒绝返回 500

- **关联用例**：TC-036 / TC-040 / TC-041 / TC-042
- **复现步骤与实测响应**：

| 用例 | 请求 | 期望 | 实际响应 |
|---|---|---|---|
| TC-036 | 学生B `GET /api/appointment/{A的id}` | 403 | `500 {"detail":"获取预约详情失败: 403: 无权访问此订单"}` |
| TC-040 | 学生A `GET /api/consultation/counselor/orders` | 403 | `500 {"detail":"获取订单列表失败: 403: 仅咨询师可访问"}` |
| TC-041 | 学生A `POST /api/consultation/order/{id}/handle {"action":"agree"}` | 403 | `500 {"detail":"处理订单失败: 403: 仅咨询师可操作"}` |
| TC-042 | 学生A `GET /api/appointment/counselor/list` | 403 | `500 {"detail":"获取咨询师预约列表失败: 咨询师档案不存在"}` |

- **数据库变化**：全部越权请求的 `status_before=status_after=pending`，**未发生越权修改、未泄漏他人数据**
- **错误原因**：`api/counselor/__init__.py:456-488`、`:407-442` 与 `api/consultation/__init__.py:82-112`、`:131-165` 的 `try` 块内 `raise HTTPException(403)` / `raise ValueError(...)` 被紧随其后的 `except Exception as e` 捕获并重抛 500。
- **影响**：前端 axios 拦截器按状态码分支提示，会把「无权限」误显示为「服务器错误」；监控/告警产生 5xx 误报；自动化与第三方集成无法依赖标准状态码。
- **修复建议**：在每个路由的 `except Exception` **之前**加 `except HTTPException: raise`；把 `ValueError` 显式映射为 400/404/403。建议抽成统一异常处理器，避免逐路由修补。

### BUG-05〔P2〕带时区的 ISO 时间触发 500

- **关联用例**：TC-030
- **复现步骤**：`POST /api/appointment/create`，`appointment_date = "2026-11-12T09:00:00Z"`
- **响应**：`500 {"detail":"创建预约失败: can't compare offset-naive and offset-aware datetimes"}`
- **数据库变化**：事务回滚，`appointments` 无新增行
- **错误原因**：`counselor_service.py:561` 将 `Z` 替换为 `+00:00` 后 `fromisoformat` 生成 aware datetime，`:566` 与 naive `datetime.now()` 比较抛 `TypeError`；`api/counselor/__init__.py:360-366` 兜成 500。`AppointmentCreate.appointment_date` 只是 `str`，无格式校验（`schemas/counselor.py:118`）。
- **修复建议**：统一转换为 naive 本地时间（或全程 aware 比较）；捕获 `TypeError/ValueError` 返回 400；schema 增加日期格式约束与营业时段（09:00–19:00）白名单。

### BUG-06〔P2〕`/api/appointment/counselor/list` 缺少角色校验

- **关联用例**：TC-042
- **复现步骤**：普通学生 token 调用该接口
- **响应**：500（见 BUG-04），数据未泄漏
- **错误原因**：`api/counselor/__init__.py:407-442` 仅依赖 `get_current_user_id`（只解 token、不查 `users`）；服务层 `counselor_service.py:759` 只用 `counselors.user_id` 是否存在档案来判断，未校验档案 `status/application_status`，也未校验 JWT `role`。
- **修复建议**：增加显式角色依赖（JWT `role` + 有效咨询师档案），非咨询师直接 403；与 `api/consultation/__init__.py:43-59` 的判定逻辑统一。

### BUG-07〔P3〕越权操作返回 400「预约不存在」而非 403

- **关联用例**：TC-037、TC-038（TC-043/045 同类但按既有契约判为通过）
- **复现步骤**：学生B `POST /api/appointment/{A的id}/cancel`；学生B `POST /api/appointment/{A的id}/review`
- **响应**：均为 `400 {"detail":"预约不存在"}`；DB 状态前后均为 `pending`，无变化
- **错误原因**：`counselor_service.py:808-814`、`:894-900` 把「记录存在」与「归属校验」合并进同一条 `WHERE id=? AND user_id=?` 查询，越权与不存在返回同一错误。
- **评价**：**权限隔离有效，不存在安全绕过**；仅 API 语义不符合 REST 契约，优先级低。
- **修复建议**：先按 `id` 查存在，再比对归属，越权返回 403（或统一 404 以避免探测订单存在性）。

### BUG-08〔P2〕咨询师邮件通知永远失败（后端运行日志实证）

- **关联用例**：附加发现（TC-005 / TC-020 等创建、取消用例期间从后端日志观测）
- **复现步骤**：任意一次创建或取消预约，查看后端错误日志
- **接口响应**：仍返回 `200`（异常被内层 `try/except` 静默吞掉），业务主流程不受影响
- **日志证据**：多次出现 `发送预约邮件时出错: 'Counselor' object has no attribute 'email'` 与 `发送取消邮件时出错: 'Counselor' object has no attribute 'email'`
- **数据库变化**：无
- **错误原因**：`counselor_service.py:641`、`:850` 读取 `counselor.email`，但 `models/counselor.py:9-65` 与 `sql/init.sql:51-103` 中 `counselors` 表均无 `email` 列（邮箱在 `users` 表）。
- **修复建议**：通过 `counselor.user_id` 关联 `users.email` 取地址，或为 `counselors` 增加联系邮箱列；同时把邮件失败改为可观测（结构化日志/告警），不要静默吞异常。

### 4.1 Bug 汇总表

| 编号 | 优先级 | 标题 | 关联用例 | 类型 |
|---|---|---|---|---|
| BUG-01 | P1 | 咨询师预约列表接口 500（`Appointment.user` 缺失） | TC-047 | 功能不可用 |
| BUG-02 | P1 | 评价后咨询师评分/评价数不更新 | TC-016 | 数据一致性 |
| BUG-03 | P1 | 只判等值冲突，允许重叠预约 | TC-025 | 业务正确性 |
| BUG-04 | P2 | `HTTPException` 被吞，403 变 500 | TC-036/040/041/042 | 错误契约 |
| BUG-05 | P2 | 带时区时间导致 500 | TC-030 | 异常处理 |
| BUG-06 | P2 | 咨询师列表接口无角色校验 | TC-042 | 权限设计 |
| BUG-07 | P3 | 越权返回 400 而非 403 | TC-037/038 | API 语义 |
| BUG-08 | P2 | 咨询师邮件通知静默失败 | 日志实证 | 辅助功能失效 |

---

## 五、数据库一致性检查

### 5.1 写入正确性（TC-048，通过）

| 检查项 | 结果 |
|---|---|
| 本次新增预约数 | 8 |
| `user_id` 孤儿外键 | 0 |
| `counselor_id` 孤儿外键 | 0 |
| 重复 `appointment_no` | 0 |
| 非法 `status` 枚举值 | 0 |
| 孤儿评价（评价指向不存在预约） | 0 |
| `consultation_reviews` 唯一索引 | `uk_appointment_review (appointment_id)` 存在 |
| 状态时间戳 | `confirmed_at`（TC-010）、`completed_at`（TC-014）、`cancelled_at`（TC-020/023）均在对应流转后正确写入 |
| 评价内容 | 1 条评价：`rating=4.5`、标签与内容正确、`is_anonymous=1`；重复评价被拒后仍为 1 条 |
| **唯一不一致** | `counselors.rating / review_count` 与评价聚合值不符 → BUG-02 |

### 5.2 隔离性与基线恢复（TC-049 + 浏览器测试后复查，通过）

清理明细（接口测试轮）：`consultation_messages -4`、`consultation_reviews -1`、`appointments -8`、`notifications -14`、`counselors -2`、`users -4`。

| 表 | 测试前基线 | 全部测试结束后 |
|---|---:|---:|
| users | 2 | 2 |
| counselors | 1 | 1 |
| appointments | 0 | 0 |
| consultation_reviews | 0 | 0 |
| consultation_messages | 0 | 0 |
| counselor_inquiries / inquiry_messages / notifications | 0 | 0 |

`E2E_C_%` / `E2E_UI_%` 残留账号 **0 条**；既有 2 个用户、1 个咨询师档案与全部原有数据未被修改或覆盖。

### 5.3 并发与 DDL 风险（未实测，见第七节）

`appointments` 无 `(counselor_id, appointment_date)` 唯一索引；`init.sql` 与 `migrate.sql` 对 `consultation_reviews`、`consultation_messages` 的索引/类型定义不一致。若生产库按 `migrate.sql` 建立，「一预约一评价」将失去数据库层保障。

---

## 六、未实现功能 与 现有缺陷 的区分

### 6.1 未实现功能（Feature Gap，**不计为 Bug**）

| 功能 | 判定依据 |
|---|---|
| **预约改期** | TC-035 实测：运行时 OpenAPI 106 条路径中 `reschedule`/改期相关路径为 0，`/api/appointment/*` 无 PUT/PATCH；`PUT /api/appointment/{id}` → 405，`POST /api/appointment/{id}/reschedule` → 404；前端全仓无改期入口。属于需求未做，不是缺陷。 |
| 咨询师排班 / 可预约时间写入接口 | 无排班表、无模型、无 POST/PUT 写入路由；`09:00–19:00` 时段硬编码在 `counselor_service.py:143-147` |
| 评价修改 / 删除 / 咨询师回复 | `counselor_reply`、`replied_at` 字段存在，但全仓无任何写入代码 |
| 支付 / 退款 | `paid_amount` 恒为 0，`refunded` 状态无任何写入路径 |
| 取消截止时间 / 提前预约限制 | 仅邮件模板中有「请提前 24 小时」文案，无服务端校验 |
| 咨询师主动取消预约 | 无对应接口（TC-043 验证咨询师调用学生取消接口被拒） |
| 独立「开始咨询」接口 | 由首条消息隐式推进（设计取舍，非缺陷） |

### 6.2 现有缺陷（代码已实现但行为错误）

即第四节 BUG-01 ~ BUG-08。特别强调：**BUG-03 不是「未做时间冲突校验」**——等值冲突校验已实现且 TC-024 通过，缺陷在于校验算法不完整导致重叠时段被放行；**BUG-01/02/04/05/08 都是已实现代码中的运行时错误**，均来自真实响应或运行日志。

### 6.3 判定口径说明

- 「未实现」= 运行时 OpenAPI 无该路由 / 代码中无该写入路径 → 记为 `FEATURE_GAP`，不参与通过率与 Bug 统计。
- 「缺陷」= 接口存在、调用后实际行为与预期不符（含 500、数据不一致、错误码错误）→ 记为 `FAIL` 并进入 Bug 清单。

---

## 七、计划外未验证项（静态代码分析线索，**未实际调用，不作为测试结论**）

以下为阅读代码时发现的疑点，本次**未执行**真实调用验证，仅登记为后续测试候选，不计入通过率、不计入 Bug 清单：

1. 并发创建预约「先查后插」且无唯一索引 → 理论可双订（`counselor_service.py:569-576`、`sql/init.sql:261-264`）。
2. 咨询师入驻审核接口疑似无鉴权且硬编码审核人 ID（`api/counselor/__init__.py:645-718` 的 `TODO` 与 `reviewer_id=1`）。
3. 预约前沟通发送消息疑似无会话归属校验（`api/counselor/__init__.py:282-323`）。
4. `DELETE /api/consultation/{id}/signals` 疑似无归属/角色校验（`api/consultation/__init__.py:412-426`）。
5. 审核通过后未更新 `users.role`，可能导致 `auth_service.py:313` 的咨询师跳转分支不可达。
6. `init.sql` 与 `migrate.sql` 关于评价表唯一键、消息类型（VARCHAR vs ENUM）、`replied_at` 类型定义不一致。
7. `CounselorRegisterRequest` 中 `min_items` 为 Pydantic v1 写法（项目为 2.5.3），空列表校验可能失效。
8. CORS `allow_origins=["*"]` 与 `allow_credentials=True` 并用（`main.py:45-51`）。
9. `INTEGRATION.md` 提示 `backend/.env` 曾被提交到公开仓库，建议轮换密钥（安全治理，非本次测试范围）。

另：RAG 预热 NumPy 兼容问题按用户要求明确排除，未执行。

---

## 八、后续开发建议（修改方案，**等待确认后实施**）

> 本次严格遵守「以测试为主」约束：**未修改任何业务代码**。以下为建议方案，实施前请确认。

**第一批（P1，建议优先）**

1. **BUG-01**：在 `models/counselor.py` 的 `Appointment` 增加 `user = relationship("User")`，或让 `get_counselor_appointments` 显式 join `users`；补一条「咨询师列表接口返回 200」回归用例。
2. **BUG-02**：`counselor_service.submit_review` 在 `db.add(review)` 后、重算统计前执行 `db.flush()`；对历史数据写一次性回填；补「评价 → 咨询师详情评分」端到端断言。
3. **BUG-03**：抽取统一的 `has_time_conflict(db, counselor_id, start, duration)`，供 `create_appointment` 与 `get_available_slots` 共用；按区间重叠判断；为 `appointments` 增加 `(counselor_id, appointment_date)` 唯一索引并在事务内处理并发冲突（返回 409/400 而非 500）。

**第二批（P2）**

4. **BUG-04**：为 C 模块所有路由统一加 `except HTTPException: raise`（建议改用 FastAPI 全局异常处理器），并把 `ValueError` 映射到 400/404；补状态码契约测试。
5. **BUG-05**：统一 naive/aware 时间处理，schema 增加格式与营业时段校验；`TypeError` 归为 400。
6. **BUG-06**：引入统一的 `require_counselor` 依赖，校验 JWT `role`、咨询师档案 `status/application_status/is_deleted`；`/api/appointment/counselor/list` 接入该依赖。
7. **BUG-08**：咨询师邮箱改从 `users` 关联获取；邮件失败写入可观测日志/告警而非静默吞掉。

**第三批（P3 / 功能补齐）**

8. **BUG-07**：拆分「存在性」与「归属」判断，越权返回 403 或统一 404。
9. **改期功能**：若需要，新增 `POST /api/appointment/{id}/reschedule`，复用 BUG-03 的冲突判定，限定 `pending/confirmed` 可改期、记录改期历史，并在前端 `/counselor/orders` 增加入口。
10. **排班能力**：建立 `counselor_schedules` 表与写入接口，替换硬编码时段。
11. **测试基建**：把 `e2e_c_module/` 纳入 CI（当前仓库无任何前端测试框架），至少固化 C 模块 50 条接口用例 + 6 条浏览器用例；补充并发、DDL 一致性、第七节 9 项静态线索的真实用例。

---

## 九、合规声明与测试产物

- 未删除、清空或重建任何数据库与 Docker 数据卷；仅对本次新增的、带明确前缀的行做精确删除。
- 未覆盖、未修改任何真实用户数据；所有断言基于隔离数据。
- 未修改任何业务代码、配置或 `.env`；仅新增测试脚本与测试报告。
- 报告不含账号、密码、Token、密钥与敏感个人信息；`results.json` 中请求/响应已对认证头、令牌、邮箱、联系方式脱敏。
- 所有结论来自真实执行：50 条接口用例、6 条浏览器用例、数据库前后快照、OpenAPI 运行时枚举与后端运行日志。未虚构通过率。

| 产物 | 路径 |
|---|---|
| 测试报告 | `C_MODULE_TEST_REPORT.md` |
| 接口测试脚本 | `e2e_c_module/run_e2e.py` |
| 浏览器测试脚本 | `e2e_c_module/browser_e2e.py` |
| 公共工具 / 环境探针 | `e2e_c_module/common.py` |
| 结果汇总脚本 | `e2e_c_module/show_results.py` |
| 接口原始结果（脱敏） | `e2e_c_module/results.json` |
| 浏览器原始结果 | `e2e_c_module/browser_results.json` |
| 后端/前端运行日志 | `e2e_c_module/backend.*.log`、`e2e_c_module/frontend.*.log` |
| 浏览器测试依赖（隔离安装） | `e2e_c_module/_pwlib/` |
