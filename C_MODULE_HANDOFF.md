# Mindisle / SoulStation — C 模块阶段性交接文档

> **本文档是新会话的唯一交接入口。** 开启新 CodeBuddy 会话后请先完整阅读本文件，再按第十四节的清单行动。
>
> 交接日期：2026-11-09　｜　项目根目录：`e:/大一/比赛/腾讯ai实训/代码/Mindisle`
> 交接范围：C 模块（心理咨询预约、取消预约、预约状态管理、咨询评价与反馈）的测试与 P1/P2 Bug 修复成果。
> 本轮性质：**只读检查与整理**。本轮未修改任何业务代码、数据库、配置文件或测试断言；未执行 DDL、迁移、回填；未提交代码。唯一新增文件是本文档。
> 凭据声明：本文档不含任何账号、密码、Token、密钥或真实用户个人信息；也不复述项目文档中出现的明文示例凭据。

---

## 一、结论速览（先看这一节）

| 项 | 状态 |
|---|---|
| C 模块初始真实测试 | 已完成，50 条接口 + 6 条浏览器用例全部执行，发现 BUG-01～08 与若干功能缺失 |
| 第一阶段 P1（BUG-01/02/03） | **已修复并暂停**，最小改动，P1 专项 `4 PASS/7 FAIL → 11 PASS/0 FAIL` |
| 只读边界审查 | 已完成，确认 P1 对 B 的 `get_available_slots` 存在一次已发生的跨模块修改，建议补 B 负责人确认 |
| 第二阶段 P2（BUG-04～08） | **已修复并暂停**，最小改动，P2 专项 `6 PASS/9 FAIL → 15 PASS/0 FAIL` |
| 最新完整回归 | 完整接口 `49 PASS / 0 FAIL / 1 FEATURE_GAP`；浏览器 `6 PASS / 0 FAIL`；P1 `11/11`；P2 `15/15` |
| 数据库结构 | 本轮（含 P1/P2）未改模型、Schema、SQL、索引、约束、迁移；未执行 DDL / 回填；**仅有有限保证，见第八节** |
| 数据库数据 | 只读复查回到交付基线：`users=2`、`counselors=1`，其余 C 模块核心表均为 0，隔离账号残留 0 |
| 唯一仍记录的测试缺口 | `TC-035` 预约改期 = `FEATURE_GAP`（未实现功能，不是缺陷，不视为必须开发） |
| 当前指令状态 | **P1/P2 均已结束并暂停**；未获新指令前不得继续修复、开发、提交或改库 |

---

## 二、项目与团队边界（必须遵守）

五人协作，职责划分（用户明确给出）：

| 模块 | 职责 | 本轮是否被 C 改动 |
|---|---|---|
| A | 认证与权限（`core/security.py`、`auth_service.py`、`models/user.py`、`api/auth/`） | 否；只读读取了 `User.email` |
| B | 咨询师信息与排班（`CounselorService`、咨询师列表/详情/入驻/审核、`get_available_slots`） | **P1 曾改动 `get_available_slots` 4 个 hunk（需团队确认）**；P2 未再改动 |
| C | 预约、取消、状态流转、评价反馈（本文档主体） | 是，改动集中在 `AppointmentService` 与 C 路由 |
| D | 心理测评（`api/test`、`test_service.py`） | 否；工作区原有的 `init.sql` 未提交改动属 D 表定义 |
| E | AI 心理支持（`api/ai_support`、`ai_service.py`） | 否；`INTEGRATION.md` 中存在 E 对 C 的**未实现依赖**，见第十三节 |

C 模块最小边界：`AppointmentService` 及 `api/counselor/__init__.py` / `api/consultation/__init__.py` 中的预约、取消、状态、评价、咨询订单路由。
注意：`backend/app/services/counselor_service.py` 是 **B / C / 管理端共享文件**（被 `api/counselor`、`api/consultation`、`api/admin` 引用），任何后续改动都应限定在 C 方法内，不做模块级重构。

---

## 三、四份既有报告（证据来源，按需读细节）

| 文件 | 内容 | 时间戳 |
|---|---|---|
| `C_MODULE_TEST_REPORT.md` | 初始真实测试报告：环境、50 条接口用例明细、6 条浏览器用例、BUG-01～08、功能缺失、9 项静态线索、合规声明 | 2026-11-09 16:08:34 |
| `C_MODULE_P1_FIX_REPORT.md` | P1 修复：根因、逐项改动、修复前后对比、三套回归结果、未处理项、未执行的 DDL 备选方案 | 2026-11-09 16:36:45 |
| `C_MODULE_BOUNDARY_REVIEW.md` | 只读边界审查：P1 的 12 个 hunk 逐项归属、A/B/D/E 影响、DDL 有限保证、Git 状态三分、BUG-04～08 跨模块评估 | 2026-11-09 16:51:22 |
| `C_MODULE_P2_FIX_REPORT.md` | P2 修复：约束合规、修改前后 Git 状态、完整 Diff、四套回归、邮件 Mock、未触碰其他模块证明、剩余问题 | 2026-11-09 17:27:04 |

四份文件均为**未跟踪（untracked）**，未提交。本轮交接已重新逐份阅读，下面的汇总来自这些报告与本轮只读复核，未新增测试结论。

---

## 四、C 模块已实现功能（来自运行时 OpenAPI + 真实调用，非静态推断）

| 能力 | 接口 | 结论 |
|---|---|---|
| 咨询师列表 / 详情 | `GET /api/counselor/list`、`GET /api/counselor/{id}` | 可用 |
| 可预约时段查询（B 边界） | `GET /api/counselor/{id}/slots?date=` | 可用，硬编码 09:00–19:00 共 10 个整点 |
| 咨询师评价列表 | `GET /api/counselor/{id}/reviews` | 可用 |
| 创建预约 | `POST /api/appointment/create` | 可用，真实落库；前端传无时区 `YYYY-MM-DDTHH:MM:SS` |
| 学生预约列表 / 详情 | `GET /api/appointment/user/list`、`GET /api/appointment/{id}` | 可用 |
| 取消预约 | `POST /api/appointment/{id}/cancel?reason=` | 可用，写 `cancel_reason` / `cancelled_at`，时段释放 |
| 咨询师订单列表 | `GET /api/consultation/counselor/orders` | 可用（BUG-01/06 修复后权限与列表行为正确） |
| 咨询师接受 / 拒绝 | `POST /api/consultation/order/{id}/handle` | 可用 |
| 咨询推进 | `POST /api/consultation/{id}/message`、`/end` | 可用；`confirmed → in_progress` 由首条消息隐式触发 |
| 提交评价与反馈 | `POST /api/appointment/{id}/review` | 可用；修复后评分统计同步正确 |
| 咨询师备注 / 文件上传 | `POST /api/consultation/{id}/note`、`/upload` | 代码存在，未纳入 C 模块执行范围 |
| 浏览器主链路 | `/counselor` → `/login` → 预约 → `/counselor/orders` → 取消 | 真实 Chrome 交互 6/6 通过 |

**状态流转（实测）**：

```
pending ──(咨询师 agree)──> confirmed ──(首条咨询消息，隐式)──> in_progress ──(/end)──> completed
   │                                                                                    │
   ├──(学生 cancel)──────────────────────────> cancelled                     └──(提交评价)
   └──(咨询师 reject，reason 写入 cancel_reason)──> cancelled
```

- 无独立「开始咨询」接口；无 `rejected` 状态；`refunded` 仅在枚举/文档出现、代码无写入路径。
- 取消仅学生侧；咨询师无取消接口。
- C 模块不读 JWT 的 `role`：`api/counselor` 只取 `sub`，`api/consultation` 通过 `counselors.user_id` 判定角色；归属校验按 `appointments.user_id` / `counselor_id`。

**已确认未实现功能（FEATURE_GAP，不是 Bug，未经确认不得开发）**：预约改期、咨询师排班/时段写入接口、评价修改/删除/咨询师回复、支付/退款、取消截止时间与提前预约限制、咨询师主动取消、独立「开始咨询」接口。

---

## 五、已修 Bug 清单（BUG-01 ～ BUG-08 全部完成）

### 5.1 第一阶段 P1（唯一业务文件：`backend/app/services/counselor_service.py`，+85/-29）

| Bug | 根因 | 最小修复 | 验证 |
|---|---|---|---|
| BUG-01 咨询师预约列表恒定 500 | `Appointment` 模型只有 `counselor` / `review` 关系，无 `user`；`appt.user` 抛 `AttributeError` | `get_counselor_appointments` 显式 `db.query(User).filter(User.id == appt.user_id)`，`user_info`（`id/nickname/email/phone`）结构不变 | P1-01、TC-047 转 PASS |
| BUG-02 评价后评分/评价数滞后一条 | `SessionLocal(autoflush=False)`，`db.add(review)` 后立即聚合查不到新行 | 重算统计前增加 `db.flush()`（当前 L994）；不改统计公式 | P1-02/03、TC-016 转 PASS |
| BUG-03 只判 `appointment_date` 等值，忽略 60 分钟时长与并发 | `create_appointment` 与 `get_available_slots` 各自重复等值判断，无事务级并发保护 | 新增 `ACTIVE_APPOINTMENT_STATUSES`、`DEFAULT_APPOINTMENT_MINUTES=60`、`_appointment_interval`、`_intervals_overlap`、`_active_appointments_in_window`、`_has_time_conflict`（当前 L26/L28/L58 等）；两处共用半开区间 `[start, start+duration)`；`create_appointment` 对 `Counselor` 行 `with_for_update()`（当前 L614）串行化；写入 `duration=DEFAULT_APPOINTMENT_MINUTES`（L660） | P1-05/07/10/11、TC-025 转 PASS；12:00/13:00 首尾相接不误判 |

P1 未改模型、Schema、路由、SQL、前端、`.env`；未用唯一索引代替区间校验，未执行 DDL；OpenAPI 修复前后均 106 路径，错误消息「该时段已被预约」与响应结构保持不变。

### 5.2 第二阶段 P2（3 个 C 文件，净 +45/-18）

| Bug | 最小修复 | 当前代码位置 |
|---|---|---|
| BUG-04 `HTTPException` 被 `except Exception` 吞掉，403 变 500 | 6 个 C 路由各加 `except HTTPException: raise` | `api/counselor/__init__.py` L437/485/524/567；`api/consultation/__init__.py` L107/161 |
| BUG-05 带时区 ISO 时间触发 aware/naive 比较 500 | `create_appointment` 解析后 `tzinfo is not None` → `ValueError("日期时间格式错误")` → 400；`except (ValueError, TypeError)`；**保持原日期时间格式不变** | `counselor_service.py` L623-625；前端 `AppointmentForm.vue:203`、`booking.js:71` 仍为无时区格式，未改 |
| BUG-06 `/api/appointment/counselor/list` 无角色校验 | 复用方法内已有的 `Counselor.user_id` 查询，找不到档案由 `ValueError` 改为 `HTTPException(403, "仅咨询师可访问")`；**未改 `core/security.py`** | `counselor_service.py` `get_counselor_appointments` |
| BUG-07 越权返回 400「预约不存在」 | `cancel_appointment` / `submit_review` 拆分「存在性」与「归属」，非本人 403「无权操作此预约」；不存在的预约仍 400 | `counselor_service.py` `cancel_appointment`、`submit_review` |
| BUG-08 咨询师邮件通知静默失败 | `counselors` 表无 `email` 列；改为通过 `counselor.user_id` 关联 `users.email` 取得 `counselor_email`；邮件时间格式化变量上移；未改 `email_service.py`、未加字段 | `counselor_service.py` L701-705、L916-920 |

P2 新增 `from fastapi import HTTPException, status`（项目已有依赖）与标准库 `unittest.mock`（仅测试启动器）；未引入依赖、未改前端、未改测试断言、未改 `_has_time_conflict` / `get_available_slots` / 排班规则、未改 B 路由异常分支。

---

## 六、真实测试结果（全部来自实际执行，未执行项从未标记通过）

### 6.1 三阶段对比

| 套件 | 用例数 | 初始测试 | P1 修复后 | P2 修复后（最新） |
|---|---:|---|---|---|
| 完整接口 `run_e2e.py` | 50 | 39 PASS / 10 FAIL / 1 FEATURE_GAP | 42 PASS / 7 FAIL / 1 FEATURE_GAP | **49 PASS / 0 FAIL / 1 FEATURE_GAP** |
| 浏览器 E2E `browser_e2e.py` | 6 | 6 PASS / 0 FAIL | 6 PASS / 0 FAIL | **6 PASS / 0 FAIL** |
| P1 专项 `regression_p1.py` | 11 | 4 PASS / 7 FAIL | **11 PASS / 0 FAIL** | **11 PASS / 0 FAIL**（保持） |
| P2 专项 `regression_p2.py` | 15 | 6 PASS / 9 FAIL | — | **15 PASS / 0 FAIL** |

- 初始断言型通过率 `45 / 55 = 81.8%`；合计 56 条用例全部执行完毕，0 阻塞、0 未执行（计划内）。
- P2 后由 FAIL 转 PASS 的 7 条：`TC-030`(400)、`TC-036`/`TC-037`/`TC-038`/`TC-040`/`TC-041`/`TC-042`(403)。`TC-048`（数据库一致性）、`TC-049`（隔离清理与基线恢复）均 PASS。
- **`TC-035` 预约改期始终保持 `FEATURE_GAP`**：运行时 OpenAPI 无改期路由，`PUT → 405`、`/reschedule → 404`、前端无入口。
- 运行时 OpenAPI 路径数在初始 / P1 / P2 各阶段均为 **106**，接口路径、参数、成功响应格式未变；仅错误码由 500 纠正为 400/403。
- 既有测试断言未修改：`run_e2e.py`、`browser_e2e.py`、`regression_p1.py`、`common.py` 的时间戳均早于 P2 阶段；P2 只新增 `regression_p2.py` 与 `run_backend_mail_mock.py`。
- 部分重跑命令曾因未设 `$env:PYTHONIOENCODING='utf-8'` 导致控制台中文乱码；JSON 结果与统计正确，已通过读取结果文件复核。

### 6.2 测试数据隔离与邮件隔离

- 账号/实体前缀：`E2E_C_`、`E2E_UI_`、`E2E_P1_`、`E2E_P2_`；密码运行时随机生成且不落盘；邮箱使用 RFC 2606 保留域；认证全部通过真实 `POST /api/auth/login`。
- 造数只 `INSERT` 新增行，不 UPDATE/DELETE 既有行；清理按本次记录主键精确 `DELETE`，顺序：消息 → 评价 → 预约 → 通知 → 咨询师 → 用户；末尾校验 `cleanup.baseline_restored=true`。
- 邮件测试隔离：`e2e_c_module/run_backend_mail_mock.py` 用 `unittest.mock.patch.object` 替换 `EmailService.create_smtp_connection` 与 3 个发信函数，只写脱敏事件到 `mail_mock_events.jsonl`；**测试期间未连接真实 SMTP、未向任何真实用户发信**。测试结束后已停止 Mock 后端并恢复按原项目配置启动的 `uvicorn app.main:app`。
- P2 修复前/后的邮件证据：修复前 `confirmation_counselor` 事件 0、日志含 `'Counselor' object has no attribute 'email'`；修复后确认邮件事件 1、取消邮件事件 2（用户 + 咨询师）、日志无该 AttributeError。
- **后续注意**：BUG-08 修复后，正式配置下咨询师邮件会真实发出（这是原项目功能恢复，非新增机制）。跑完整接口/浏览器套件时若后端为原配置，创建/取消预约会触发发信尝试；只要坚持隔离账号前缀与保留域，就不会触达真实用户；若需完全隔离，务必先启动 Mock 后端。

### 6.3 结果产物

`e2e_c_module/` 下：`results.json`、`browser_results.json`、`regression_p1_before.json` / `regression_p1_after.json`、`regression_p2_before.json` / `regression_p2_after.json`、`mail_mock_events.jsonl`、`show_results.py`、若干 `backend.*.log` / `frontend.*.log`、隔离安装的 `_pwlib/`。重跑测试会覆盖同名结果文件。

---

## 七、Git 状态与改动分类（本轮交接只读复核）

**HEAD**：`78951af | 2026-11-09 10:25:02 +0800 | Merge remote-tracking branch 'origin/main'`（未提交任何新 commit）。

### 7.1 已跟踪的修改（`git diff --numstat` 实测）

| 文件 | +/- | 归属 |
|---|---:|---|
| `backend/app/services/counselor_service.py` | 118 / 47 | 本方 P1（+85/-29）+ P2（+33/-18），**B/C/管理端共享文件** |
| `backend/app/api/counselor/__init__.py` | 8 / 0 | 本方 P2，仅 4 个 C 预约路由新增 `except HTTPException: raise` |
| `backend/app/api/consultation/__init__.py` | 4 / 0 | 本方 P2，仅 2 个 C 订单路由新增 `except HTTPException: raise` |
| `backend/docker-compose.yml` | 1 / 1 | **工作区原有**，MySQL 主机端口 `3306 → 3307`；非 P1/P2 改动 |
| `backend/sql/init.sql` | 1 / 1 | **工作区原有**，`test_progress.answers` JSON 默认值写法修正（D 模块表，13:15:31）；非 P1/P2 改动，且当前库已按修正后的 DDL 初始化 |

> `backend/docker-compose.yml` 与 `backend/README.md` 含明文示例凭据，`README.md` 含默认测试账号密码；本文档一律不复述，后续任何文档/日志也不要复制。

### 7.2 未跟踪（`??`）条目分类

| 类别 | 条目 |
|---|---|
| 本协作会话的 C 模块产物 | 四份 `C_MODULE_*.md`；`e2e_c_module/`（测试脚本、结果、日志、Mock 启动器、`_pwlib/`） |
| 其他成员 / 工作区原有遗留 | `backend/seeds/_demo_articles.py`、`backend/seeds/_fix_admin_table.py`、`dev-start.sh`、`frontend/scripts/screenshot.mjs`、`screenshots/` |

- `docs/` 被 `.gitignore:90` 忽略，因此 `docs/PROJECT_AUDIT.md`、`docs/PROJECT_AUDIT_SUMMARY.md`、`docs/.~TEST_REPORT.md`、`docs/TEST_REPORT.md` 不出现在普通 `git status` 中；它们是 2026-11-08/09 的**静态审查文档，无业务实测结论**，且新克隆仓库可能没有这些文件。
- `backend/seeds/_fix_admin_table.py` 文件名暗示涉及管理端表结构，工作区原有；本轮未打开、未执行。若团队要严格追查数据库结构来源，需单独确认该脚本是否被运行过。

---

## 八、数据库结构核查与「有限保证」

### 8.1 本轮（交接阶段）只读复查（真实执行 `common.probe()`，仅 SELECT / SHOW / information_schema）

| 观测 | 结果 |
|---|---|
| 连接 | `localhost:3307/soulstation`，MySQL `8.0.46`（凭据未打印） |
| 基线行数 | `users=2`、`counselors=1`；`appointments / consultation_reviews / consultation_messages / counselor_inquiries / inquiry_messages / notifications` 全部 0 |
| 隔离残留 | `users E2E_C_: 0`、`counselors E2E_C_: 0` |
| 列 | `users=23`、`counselors=30`（**无 `email` 列**，与 BUG-08 根因一致）、`appointments=22`、`consultation_reviews=12`、`consultation_messages` 含 `sender_type` 等 |
| `appointments` 索引 | `PRIMARY`、`appointment_no`(UNIQUE)、`idx_user_id`、`idx_counselor_id`、`idx_status`、`idx_appointment_date`，共 6；**无 `(counselor_id, appointment_date)` 唯一索引** |
| `consultation_reviews` 索引 | `PRIMARY`、`uk_appointment_review`(UNIQUE, `appointment_id`)、`user_id`、`idx_counselor_id`、`idx_rating`，共 5 |

`C_MODULE_BOUNDARY_REVIEW.md` 另记录：C 模块 7 张表 `CREATE_TIME` 均为 2026-11-09 13:16:45/46（早于 P1 代码修改 16:32:37），排班表 `counselor_schedules` / `availability` / `time_slots` 不存在，索引/约束与 `init.sql` 一致，索引总数 15。本轮未重新导出全量 DDL，这些数值引自既有报告而非本轮新测。

### 8.2 版本化文件核对

`git diff --name-only` 中与结构相关的输出只有工作区原有的 `backend/sql/init.sql`；`backend/app/models/*`、`schemas/*`、`core/*`、`api/*`（业务路由除外）、`backend/sql/migrate.sql`、`migrate_e_ai_support.sql`、`.env` 均未被本方修改。P1/P2 代码与测试脚本中不含 `CREATE / ALTER / DROP INDEX / ADD CONSTRAINT` 语句，未执行迁移、未做历史回填；隔离数据仅 `INSERT` / `DELETE`。

### 8.3 必须保留的诚实声明

**缺少 P1/P2 修复前的完整数据库结构快照**（没有全量 `SHOW CREATE TABLE` 或 `information_schema` 导出），且 InnoDB 的 `UPDATE_TIME` 为 `NULL`、无法排除会话外其他协作者对同一 MySQL 实例执行 DDL。因此：

> 准确表述是「**未发现本轮引入的 DDL 变更；当前结构与版本化定义及部分修复前观测一致**」，**不得声称已严格证明数据库结构完全未变更**。

若后续需要严格证明，应在任何变更前导出 `mysqldump --no-data` + `information_schema` 全量快照作为基线（见第十三节 T4）。

---

## 九、跨模块边界与未完成的团队确认

| 事项 | 事实 | 状态 |
|---|---|---|
| P1 对 B 的 `get_available_slots` 改动 | 边界审查列出 12 个 hunk：7 个纯 C、4 个属 B（`get_available_slots`）、1 个 C/B 共用的模块级工具；`TimeSlot` 字段不变，但 `available` 语义更严格（17:30 预约会使 17:00/18:00 置为不可用，P1-10 实测）；前端 3 处按 `item.available` 过滤，无需改动但展示结果变化 | **建议补 B 负责人确认，尚未确认** |
| B 后续排班规则 | 团队已明确：**保持 P1 修复成果，不再调整 `_has_time_conflict` 或 B 的 `get_available_slots`**；C 管预约/取消/状态/评价，B 管排班与开放时段；暂定 09:00–19:00、60 分钟、整点预约，但**不实施新限制** | 已约定，未落地为新代码 |
| A 权限层 | P2 明确不改 `core/security.py`，BUG-06 采用服务层已有查询的 C 内方案；未新建统一权限系统 | 已遵守 |
| D / E | `api/test`、`api/ai_support`、`services/ai_service.py` 对 C 服务零引用；工作区原有 `init.sql` 改动属 D；E 的 `INTEGRATION.md` 对 C 有未实现依赖（见第十三节 T6） | 无代码影响 |
| 共享文件 | `counselor_service.py` 仍被 B/C/管理端共用；长期按职责拆分需团队另行决定，本阶段不重构 | 未处理 |
| 工作区原有未提交改动 | `docker-compose.yml`、`init.sql`、`dev-start.sh`、seeds、screenshot 脚本等归属未确认 | 需对应负责人确认后再提交，避免与 C 模块提交混淆 |

---

## 十、剩余问题与风险清单（按性质分类，均未在 P1/P2 处理）

### 10.1 已确认的功能缺失（不是 Bug，未经确认不得开发）

1. `TC-035` 预约改期：`FEATURE_GAP`，OpenAPI 无路由、前端无入口。
2. 咨询师排班/可预约时间写入接口：无排班表、无模型、无写入路由，09:00–19:00 硬编码。
3. 评价修改/删除/咨询师回复：`counselor_reply`、`replied_at` 字段存在但无写入代码。
4. 支付/退款：`paid_amount` 恒为 0，`refunded` 无写入路径。
5. 取消截止时间 / 提前预约限制：仅邮件模板有「提前 24 小时」文案，无服务端校验。
6. 咨询师主动取消、独立「开始咨询」接口：无对应实现。

### 10.2 未实测的静态线索（9 项，见 `C_MODULE_TEST_REPORT.md` 第七节，不作为测试结论）

并发双订的其他路径；咨询师入驻审核接口疑似无鉴权且硬编码审核人 ID；预约前沟通发送消息疑似无会话归属校验；`DELETE /api/consultation/{id}/signals` 疑似无归属/角色校验；审核通过后未更新 `users.role`；`init.sql` 与 `migrate.sql` 的索引/类型定义分歧；`CounselorRegisterRequest` 中 Pydantic v1 写法 `min_items`；CORS `allow_origins=["*"]` 与 `allow_credentials=True` 并用；`INTEGRATION.md` 提示 `backend/.env` 曾被提交到公开仓库。

> 注：`docs/PROJECT_AUDIT_SUMMARY.md`（gitignored，静态审查）也把「预约先查后插无锁」列为 P1 风险；该条已由 P1 的区间冲突 + `with_for_update()` 处理并有实测回归，其余审计结论与本模块实测结论需区分，**静态审查 ≠ 实测通过**。

### 10.3 数据 / 结构 / 运行风险

1. **存量数据偏差**：按要求未执行历史回填，历史 `counselors.rating / review_count` 与评价聚合的偏差仍在；P1 修复只保证此后新评价统计正确。
2. **DDL 快照缺口**：见第八节；`init.sql` 与 `migrate.sql` 对评价表唯一键、消息类型、`replied_at` 类型定义不一致。
3. **邮件可观测性**：BUG-08 根因已修，但按最小修改原则保留原 `logger.error` 静默兜底，未增强告警；正式环境按原配置会真实发信。
4. **时间规则**：创建侧不校验营业时段与整点对齐，属已知设计限制；B 负责人确认前不得引入新限制。
5. **安全治理（非 C 范围，未处理）**：`INTEGRATION.md` 与静态审计均提示 `backend/.env` 被 Git 跟踪并推到公开仓库，需移除跟踪、加 `.gitignore`、轮换密钥；`backend/README.md` 也含明文示例凭据。
6. **环境排除项**：RAG 预热 NumPy 兼容问题由用户明确排除，不在 C 模块范围；Redis 按用户说明为内存回退模式，未重新探测。

---

## 十一、当前项目运行方式（实测环境）

| 组件 | 配置 | 探活 |
|---|---|---|
| OS / Shell | Windows / PowerShell | — |
| Docker | Desktop 29.1.3 | `docker info` 正常 |
| MySQL | 8.0.46，容器 `soulstation-mysql`，主机端口 **3307**，库 `soulstation`，数据卷 `backend_mysql-data` 保留 | `docker ps` + `SELECT VERSION()` |
| FastAPI | `http://127.0.0.1:8000` | `GET /openapi.json` → 200 / **106 paths** |
| Vue / Vite | `http://127.0.0.1:5173`，`/api` 代理到 8000 | `GET /`、`GET /counselor` → 200 |
| Python | `backend/.venv/Scripts/python.exe`（Python 3.12.4，项目自带依赖） | 用于全部测试脚本 |
| 浏览器自动化 | Playwright 1.64.1 隔离安装在 `e2e_c_module/_pwlib/`，`channel="chrome"` 复用系统 Chrome；项目本身无前端测试框架 | 6/6 浏览器用例通过 |

启动命令（在仓库根目录执行；以下为文档记录的既有方式，本轮未重启服务、未执行初始化）：

```powershell
# 数据库（docker-compose.yml 当前把 MySQL 映射到主机 3307）
cd backend
docker-compose up -d mysql

# 后端（backend 目录）
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
# 或按 README：python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 前端（frontend 目录）
npm run dev
```

测试命令（仓库根目录，建议先设 UTF-8 避免控制台乱码）：

```powershell
$env:PYTHONIOENCODING = 'utf-8'
backend\.venv\Scripts\python.exe e2e_c_module\run_e2e.py            # 完整接口 50 例
backend\.venv\Scripts\python.exe e2e_c_module\browser_e2e.py        # 浏览器 6 例
backend\.venv\Scripts\python.exe e2e_c_module\regression_p1.py --label after   # P1 11 例
backend\.venv\Scripts\python.exe e2e_c_module\regression_p2.py --label after   # P2 15 例
backend\.venv\Scripts\python.exe e2e_c_module\show_results.py        # 汇总结果
```

- 跑 P2 / 涉及邮件的用例前，先用 `e2e_c_module\run_backend_mail_mock.py` 启动 Mock 后端（日志出现 `MAIL_MOCK_ENABLED`）；测试结束后停止并恢复 `uvicorn app.main:app` 原配置后端。
- **不要未经确认执行**：`python -m app.core.init_db`（README 记录，会建表/写测试数据）、`dev-start.sh`（SQLite 另一套环境，会执行 `create_all` 与多个 seeds，写库/装依赖）、`send_appointment_reminders.py`（会真实发信）、任何 `sql/*.sql` 迁移脚本。这些都不是本次实测环境。
- 数据库连接凭据只从 `backend/.env` 的 `DATABASE_URL` 在内存中读取，不输出、不写入任何报告或日志。

---

## 十二、需求 / PRD 依据说明（重要事实）

- 全仓按 `*PRD*` 搜索：**未发现任何 PRD 需求文档**（唯一文件名命中是 `backend/.venv/.../sympy/integrals/prde.py` 等第三方库文件，不是 PRD）。
- 因此**不能把「PRD 已核读」写进任何结论**。下一阶段任务只能依据以下现有材料：
  - `README.md`（项目背景、技术栈、模块说明、数据库表、快速开始、默认账号）；
  - `backend/README.md`（后端启动、配置说明、邮件功能说明；含明文示例凭据，勿复制）；
  - `INTEGRATION.md`（E 线集成说明，含对其他模块的依赖清单；提示 `.env` 泄露）；
  - `docs/PROJECT_AUDIT.md` / `PROJECT_AUDIT_SUMMARY.md`（被 `.gitignore` 忽略的静态审查，无实测结论）；
  - `prototype/mindisle-home.html`、`prototype/mindisle.html`（原型页面，未作为需求基线核读）；
  - 现有后端/前端代码、运行时 OpenAPI（106 路径）与四份 C 模块报告。
- README 中提到的 `database/docs/ER图.md`、`database/docs/表结构.md` 在当前工作区**不存在**；`database/` 下仅有 `Psychology-10K-ZH.json`。

---

## 十三、下一阶段真正需要完成的任务（不扩大范围，均需先确认/授权）

> 以下按「依据 → 动作 → 是否需要改代码/数据库」列出。**P1/P2 已暂停，没有用户的明确新指令，以下任何一项都不得自行实施。**

| # | 任务 | 依据 | 性质 | 是否需要改代码 / DB |
|---|---|---|---|---|
| T1 | 向 B 负责人补确认 P1 已发生的 `get_available_slots` 区间冲突改动；约定后续 B 排班能力若落地，冲突判定唯一入口仍是 `_has_time_conflict`，避免前端显示与实际预约不一致 | `C_MODULE_BOUNDARY_REVIEW.md` 第 2/6 节 | 团队确认，**不改代码** | 否 |
| T2 | 由产品/团队确认「预约改期」是否在需求范围；当前 `TC-035` 为 `FEATURE_GAP`，未确认前不开发、不改测试断言 | `C_MODULE_TEST_REPORT.md` 第 6 节 | 需求确认 | 否（若确认要开发，需另出方案并授权） |
| T3 | 对第十节 10.2 的 9 项静态线索做真实调用验证，形成独立测试结论；只读 + 测试，不先修代码 | `C_MODULE_TEST_REPORT.md` 第 7 节 | 只读测试，可新增用例 | 不改业务代码 / DB（测试产物除外，需授权） |
| T4 | 导出全量结构快照 `mysqldump --no-data` + `information_schema`，弥补 DDL 快照缺口；同时核对 `init.sql` 与 `migrate.sql` 分歧 | `C_MODULE_BOUNDARY_REVIEW.md` 第 4.3 / 7 节 | 只读 | 否（只读导出，不执行迁移） |
| T5 | 评估存量 `counselors.rating / review_count` 与历史评价聚合偏差的回填方案 | `C_MODULE_P1_FIX_REPORT.md` 第 6.2 节 | **涉及数据变更** | 需单独授权，当前红线禁止 |
| T6 | 处理 `INTEGRATION.md:165` 中 E 线对 C 的依赖：深链 `/counselor/{id}?from=ai&risk=2` 与预约 `source` 字段；`source` 需新增列，属 DDL + 跨模块 | `INTEGRATION.md` 第 6 节 | 需求/跨模块确认 | 需产品 + A/B/E 确认、DDL 方案与授权；当前禁止 |
| T7 | 与对应负责人确认工作区原有未提交改动的归属与提交计划，C 模块提交时避免混入 | 第七节 | 团队确认 | 否（不代为提交） |
| T8 | 安全治理：`backend/.env` 移除 Git 跟踪、加 `.gitignore`、轮换密钥（由 A/仓库负责人处理，非 C 范围） | `INTEGRATION.md` 开头、`docs/PROJECT_AUDIT_SUMMARY.md` | 跨模块，仅登记 | 否（C 不处理，勿复述凭据） |
| T9 | 邮件失败可观测性增强与「正式环境咨询师邮件真实发出」的验收确认 | `C_MODULE_P2_FIX_REPORT.md` 第 7 节 | 需授权的小改动 + 验收 | 若实施需改 C 服务层，当前未授权 |
| T10 | 测试基建：把 `e2e_c_module/` 四套回归固化（当前仓库无前端测试框架，Playwright 为隔离安装） | `C_MODULE_TEST_REPORT.md` 第 8 节 | 需授权的工程化 | 不改业务代码；新增 CI/配置需确认 |
| T11 | 创建预约侧营业时段 / 整点对齐校验：需与 B 排班规则统一后再定，团队已暂定但不实施 | 第九节 | 需求确认 | 当前不实施 |

**明确不建议在下一阶段做的事**：不重构 `counselor_service.py` 共享文件、不加 `(counselor_id, appointment_date)` 唯一索引、不改 `core/security.py`、不改 B 咨询师信息/排班/审核逻辑、不改前端、不新增依赖、不做支付/退款/排班/改期等新功能、不执行 DDL / 迁移 / 历史回填、不提交代码。

---

## 十四、红线、约束与新会话启动清单

### 14.1 用户多次明确的红线

1. **最小修改、保留原项目**；不重构系统、不扩大功能范围。
2. 不修改其他成员模块；不改数据库结构（模型 / SQL / 迁移 / 索引 / 约束）；不执行 DDL / 回填；不改 `.env` 凭据。
3. 不修改 `core/security.py`，不改 B 模块咨询师信息/排班/审核逻辑；保持 P1 成果与排班规则不变。
4. 不改前端、不引入依赖、不修改既有测试断言、不把未实现功能当作必须开发。
5. **未经确认不得修改代码或数据库**；任何阶段先输出计划、等待确认再实施。
6. 每次修复后必须真实执行回归测试，未执行项不得标记通过。
7. 测试邮件必须 Mock/隔离，禁止真实发信；测试数据必须隔离并按主键清理、校验基线恢复。
8. 修改前后核对 Git 状态与 Diff；不提交代码（除非明确要求）。

### 14.2 新会话建议步骤

1. 先完整阅读 `C_MODULE_HANDOFF.md`（本文件），再按需读第三节列出的四份报告对应章节。
2. 只读执行 `git status --short` 与 `git diff --numstat`，与第七节对照，确认工作区未被其他人改动。
3. 如需验证当前运行态，只读探活 `GET /openapi.json`（应为 106 paths）与本机 3307 / 8000 / 5173 端口；必要时用 `common.py` 的只读探针复查基线。
4. 收到新指令后，先输出「修改文件 / 范围 / 是否跨模块 / 是否需要 DB 变更 / 回归方案」的计划并等待确认。
5. 获准实施后：改前留基线 → 最小修改 → 重启服务加载新代码 → 跑四套回归 → 核对 Git Diff、数据库基线与隔离残留 → 输出报告并暂停。

---

## 十五、附录：关键文件索引

| 用途 | 路径 |
|---|---|
| 唯一交接入口 | `C_MODULE_HANDOFF.md`（本文件） |
| C 服务层（B/C/管理端共享） | `backend/app/services/counselor_service.py`：`ACTIVE_APPOINTMENT_STATUSES` L26、`DEFAULT_APPOINTMENT_MINUTES` L28、`_has_time_conflict` L58、`get_available_slots` 调用 L209、`with_for_update()` L614、时区拒绝 L623-625、冲突校验 L632-634、咨询师邮箱 L701-705 / L916-920、`db.flush()` L994 |
| C 预约路由 | `backend/app/api/counselor/__init__.py`（L437/485/524/567 的 `except HTTPException: raise`） |
| C 咨询订单路由 | `backend/app/api/consultation/__init__.py`（L107/161） |
| 模型根因证据（未修改） | `backend/app/models/counselor.py`（`Appointment` 无 `user` 关系；`counselors` 无 `email`）、`backend/app/core/database.py`（`autoflush=False`） |
| 邮件服务（未修改） | `backend/app/services/email_service.py`（Mock 点：`create_smtp_connection` 等） |
| 前端日期格式（只读核对，未修改） | `frontend/src/views/counselor/AppointmentForm.vue:203`、`frontend/src/views/mindisle/viewScripts/booking.js:71`、`frontend/src/views/mindisle/views/BookingView.vue` |
| 测试脚本 | `e2e_c_module/run_e2e.py`、`browser_e2e.py`、`regression_p1.py`、`regression_p2.py`、`run_backend_mail_mock.py`、`common.py`、`show_results.py` |
| 需求/项目文档 | `README.md`、`backend/README.md`、`INTEGRATION.md`、`docs/PROJECT_AUDIT*.md`（gitignored）、`prototype/*.html` |

**交接到此结束**：本次仅完成只读检查与信息整理并生成本文档；未继续开发、未修复、未提交代码，未修改任何业务代码、数据库、配置或测试断言。
