# C 模块第二阶段（BUG-04 ～ BUG-08）修复报告

> 依据：`C_MODULE_TEST_REPORT.md`、`C_MODULE_BOUNDARY_REVIEW.md`、`C_MODULE_P1_FIX_REPORT.md`
> 本阶段范围：BUG-04 / BUG-05 / BUG-06 / BUG-07 / BUG-08，遵循「最小修改、保留原项目」
> 报告日期：2026-11-09　｜　状态：**已完成并暂停**
> 凭据声明：报告不含账号、密码、Token、密钥或真实用户个人信息；测试账号为隔离账号，密码运行时随机生成且不落盘。
> **测试邮件已 Mock，本阶段未向任何真实用户发送邮件。**

---

## 一、约束合规声明

| 约束 | 落实情况 |
|---|---|
| 保留 P1 修复，不改 `_has_time_conflict` / `get_available_slots` / 排班规则 | 已保留；P1 回归 11/11 通过 |
| 保留 09:00–19:00 / 整点 / 60 分钟规则，不引入可配置排班、多时长 | 未改动；BUG-05 仅为输入格式规范化，不是时间限制 |
| 不修改 DB 结构、模型、SQL、迁移、索引、约束，不执行 DDL / 回填 | 未改动；见第六节只读核查 |
| 不修改 A/B/D/E 业务代码；共享文件只改 C 函数/路由 | 已落实；见第五节证明 |
| 不引入新依赖、框架、公共权限系统、复杂抽象 | 仅 `from fastapi import HTTPException, status`（项目已有依赖）、标准库 `unittest.mock` |
| 不修改前端页面 | 未改动；浏览器 E2E 6/6 通过 |
| 保持 API 路径、参数、成功响应格式、前端交互 | OpenAPI 修复前后均 106 路径；仅错误状态码由 500 纠正为 403/400 |
| 不修改测试断言、不把未实现功能视为必须开发 | 既有测试脚本时间戳均早于本轮；TC-035 仍为 FEATURE_GAP |
| 修改前确认 Git 状态、修改后列出实际 Git Diff | 见第二、三节 |
| 每次修改后运行回归测试 | 四套全部实际执行，见第四节 |

---

## 二、修改前 Git 状态（实测）

```
$ git --no-pager status --short
 M backend/app/services/counselor_service.py      <- P1 阶段本方修改
 M backend/docker-compose.yml                     <- 工作区原有（非本轮）
 M backend/sql/init.sql                           <- 工作区原有（非本轮）
?? C_MODULE_BOUNDARY_REVIEW.md / C_MODULE_P1_FIX_REPORT.md / C_MODULE_TEST_REPORT.md
?? backend/seeds/_demo_articles.py / _fix_admin_table.py / dev-start.sh
?? e2e_c_module/ / frontend/scripts/screenshot.mjs / screenshots/

$ git --no-pager diff --numstat
85  29  backend/app/services/counselor_service.py
1   1   backend/docker-compose.yml
1   1   backend/sql/init.sql

HEAD = 78951af  2026-11-09 10:25:02 +0800  Merge remote-tracking branch 'origin/main'
```

`docker-compose.yml`（端口映射）与 `init.sql`（`test_progress.answers` 的 JSON 默认值语法，属 D 模块）两处差异为**工作区原有**，时间戳分别为 13:07:34 / 13:15:31，早于本轮；本轮未触碰。

---

## 三、实际修改文件与 Git Diff

### 3.1 修改后差异概览（实测）

```
$ git --no-pager diff --name-only
backend/app/api/consultation/__init__.py
backend/app/api/counselor/__init__.py
backend/app/services/counselor_service.py
backend/docker-compose.yml          <- 工作区原有，非本轮
backend/sql/init.sql                <- 工作区原有，非本轮

$ git --no-pager diff --numstat
4    0    backend/app/api/consultation/__init__.py
8    0    backend/app/api/counselor/__init__.py
118  47   backend/app/services/counselor_service.py   (含 P1 的 85/29)
1    1    backend/docker-compose.yml                  (工作区原有)
1    1    backend/sql/init.sql                        (工作区原有)
```

**本轮 P2 净增量**：3 个 C 模块文件，`+45 / -18`。其中 `counselor_service.py` 相对 P1 结束状态为 `+33 / -18`。

### 3.2 `backend/app/api/counselor/__init__.py`（+8，完整 Diff）

4 个 C 路由各新增 2 行，且**全部位于 `router_appointment` 的预约路由函数内**：

```diff
@@ -434,6 +434,8 @@ async def get_counselor_appointments(
+    except HTTPException:
+        raise
     except Exception as e:
@@ -480,6 +482,8 @@ async def get_appointment_detail(
+    except HTTPException:
+        raise
@@ -517,6 +521,8 @@ async def cancel_appointment(
+    except HTTPException:
+        raise
@@ -558,6 +564,8 @@ async def submit_review(
+    except HTTPException:
+        raise
```

当前行号：`get_counselor_appointments` L437、`get_appointment_detail` L485、`cancel_appointment` L524、`submit_review` L567。
该文件中 B 的咨询师列表/详情/slots/评价/申请/审核路由的异常分支（L90/120/156/192/637/664/707 等）**一行未改**。

### 3.3 `backend/app/api/consultation/__init__.py`（+4，完整 Diff）

```diff
@@ -104,6 +104,8 @@ async def get_counselor_orders(
+    except HTTPException:
+        raise
@@ -156,6 +158,8 @@ async def handle_order(
+    except HTTPException:
+        raise
```

当前行号 L107、L161。文件内的 `get_current_user_info` / `get_current_user_role` helper 与其他 C 路由均未改。

### 3.4 `backend/app/services/counselor_service.py`（+33 / -18，逐项）

| # | 函数 / 位置 | 改动 | Bug |
|---|---|---|---|
| 1 | 模块顶部 L11 | 新增 `from fastapi import HTTPException, status`（项目已有依赖） | 使能 |
| 2 | `create_appointment` L618-625 | 解析后判断 `tzinfo is not None` → `raise ValueError("日期时间格式错误")`；`except ValueError` 扩为 `except (ValueError, TypeError)` | BUG-05 |
| 3 | `create_appointment` L678-680 | `appointment_date_str` / `appointment_time_str` 提到邮件 `try` 块开头无条件定义 | BUG-08 |
| 4 | `create_appointment` L699-705 | `counselor.email` → 通过 `counselor.user_id` 查 `users.email` 得到 `counselor_email` | BUG-08 |
| 5 | `get_counselor_appointments` L822 | 复用方法内**已有**的 `Counselor.user_id` 查询，找不到档案时由 `ValueError("咨询师档案不存在")` 改为 `HTTPException(403, "仅咨询师可访问")` | BUG-06 |
| 6 | `cancel_appointment` L869-875 | `WHERE id=? AND user_id=?` 拆为「先按 id 查存在 → 再比 `user_id`」；非本人 `HTTPException(403, "无权操作此预约")` | BUG-07 |
| 7 | `cancel_appointment` L910-920 | `appointment.counselor.email` → 通过 `appointment.counselor.user_id` 查 `users.email` | BUG-08 |
| 8 | `submit_review` L962-968 | 同 #6，拆分存在性与归属 | BUG-07 |

未改动：`CounselorService`（含 `get_available_slots`）、`ConsultationService`、`_has_time_conflict`、`_appointment_interval`、`_intervals_overlap`、`_active_appointments_in_window`、`ACTIVE_APPOINTMENT_STATUSES`、`DEFAULT_APPOINTMENT_MINUTES`、`with_for_update()`、P1 的 `db.flush()` 与 `user_info` 查询。

### 3.5 新增测试文件（非业务代码）

| 文件 | 作用 |
|---|---|
| `e2e_c_module/run_backend_mail_mock.py` | 测试专用后端启动器，用标准库 `unittest.mock` 隔离 SMTP |
| `e2e_c_module/regression_p2.py` | P2 专项回归 15 例，支持 `--label before/after` |
| `e2e_c_module/regression_p2_before.json` / `regression_p2_after.json` | 修复前后真实结果 |
| `e2e_c_module/mail_mock_events.jsonl` | 邮件 Mock 事件记录（仅事件名、是否带地址、域名，不含邮箱明文） |

---

## 四、测试命令与真实执行结果

### 4.1 邮件隔离方案（满足确认项 3）

后端在**测试期间**由 `run_backend_mail_mock.py` 启动，用标准库 `unittest.mock.patch.object` 替换：

- `EmailService.create_smtp_connection` → 返回 `MagicMock` 上下文管理器（`send_email` 的 `with ... as server` 正常走完，但不连接 SMTP）；
- `EmailService.send_appointment_confirmation_user` / `send_appointment_confirmation_counselor` / `send_appointment_cancelled` → 只写一条脱敏事件到 `mail_mock_events.jsonl` 并返回 `True`。

**业务代码零改动、`.env` 零改动、未引入新依赖、未调用真实 SMTP、未向任何真实用户发信。**
测试结束后已停止 Mock 后端并**恢复按原项目配置启动**的后端（`uvicorn app.main:app`），实测 `GET /openapi.json` → 200 / 106 路径，3307 / 8000 / 5173 均正常。正式环境邮件行为保持原状。

### 4.2 执行命令

```
# 1) 前置只读检查：Git 基线、前端日期格式、邮件服务结构、路由异常分支
# 2) 启动 Mock 后端（日志出现 MAIL_MOCK_ENABLED），确认 openapi 200 / 106 paths
python e2e_c_module/run_backend_mail_mock.py

# 3) 修复前基线
python e2e_c_module/regression_p2.py --label before

# 4) 实施最小修改 → 重启 Mock 后端加载新代码 → 确认 openapi 仍 106 paths

# 5) 修复后四套回归
python e2e_c_module/regression_p2.py --label after
python e2e_c_module/regression_p1.py --label after
python e2e_c_module/run_e2e.py
python e2e_c_module/browser_e2e.py

# 6) 恢复原配置后端、核对 Git Diff 与数据库基线
```

解释器：`backend/.venv/Scripts/python.exe`（Python 3.12.4）。全部命令均已实际执行。

### 4.3 四套回归真实统计

| 套件 | 用例数 | 修复前 | 修复后 |
|---|---:|---|---|
| P2 专项 `regression_p2.py` | 15 | **6 PASS / 9 FAIL** | **15 PASS / 0 FAIL** |
| P1 专项 `regression_p1.py` | 11 | 11 PASS / 0 FAIL | **11 PASS / 0 FAIL** |
| 完整接口 `run_e2e.py` | 50 | 42 PASS / 7 FAIL / 1 FEATURE_GAP | **49 PASS / 0 FAIL / 1 FEATURE_GAP** |
| 浏览器 E2E `browser_e2e.py` | 6 | 6 PASS / 0 FAIL | **6 PASS / 0 FAIL** |

`run_e2e.py` 中原 7 个 FAIL 全部实测转 PASS：`TC-030`(400)、`TC-036`(403)、`TC-037`(403)、`TC-038`(403)、`TC-040`(403)、`TC-041`(403)、`TC-042`(403)。`TC-048`（数据库一致性）、`TC-049`（隔离清理与基线恢复）均 PASS。`TC-035`（预约改期）保持 `FEATURE_GAP`——属未实现功能，按约束不视为必须开发。

**既有测试断言未被修改**：`run_e2e.py`(15:49)、`browser_e2e.py`(16:04)、`regression_p1.py`(16:30)、`common.py`(15:03) 的时间戳均早于本轮（17:14 起）；本轮只新增 `regression_p2.py` 与 Mock 启动器。

---

## 五、修复前后对比（关键证据）

| 用例 | 修复前实测 | 修复后实测 |
|---|---|---|
| BUG-05 `Z` / `+08:00` 输入 | `500 {"detail":"创建预约失败: can't compare offset-naive and offset-aware datetimes"}` | `400 {"detail":"日期时间格式错误"}`，DB 无新增 |
| BUG-04 学生B 读他人详情 | 500（403 被吞） | `403 {"detail":"无权访问此订单"}` |
| BUG-04 学生访问咨询师订单列表 / 处理订单 | 500 / 500 | `403` / `403` |
| BUG-06 学生访问 `/appointment/counselor/list` | `500 {"detail":"获取咨询师预约列表失败: 咨询师档案不存在"}` | `403 {"detail":"仅咨询师可访问"}` |
| BUG-07 学生B 取消 / 评价他人预约 | `400 {"detail":"预约不存在"}` ×2 | `403 {"detail":"无权操作此预约"}` ×2 |
| BUG-07 不存在的预约 | `400 预约不存在` | `400 预约不存在`（区分性保持） |
| 前端既有格式 `YYYY-MM-DDTHH:MM:SS` | 200 | 200（无回归） |
| 过去时间 / 格式错误 | 400 / 400 | 400 / 400（无回归） |
| 咨询师查看自己预约列表（P1 BUG-01） | 200 + `user_info` | 200 + `user_info`（保持） |
| 本人取消 / 完成 / 评价 / 评分统计（P1） | 200 + 统计一致 | 200 + 统计一致（保持） |
| B 模块咨询师列表 / slots | 200 / 10 个整点 | 200 / 10 个整点（保持） |

**BUG-08 的 Mock 事件证据（P2-15，真实运行而非静态分析）**：

| 观测 | 修复前 | 修复后 |
|---|---|---|
| `confirmation_counselor` 事件 | 0 | 1（带收件地址） |
| `cancelled` 事件 | 1（仅用户） | 2（用户 + 咨询师） |
| 后端日志新增内容含 `'Counselor' object has no attribute 'email'` | true | **false** |
| 创建 / 取消接口 | 200 / 200 | 200 / 200 |

---

## 六、数据库与「未触碰其他成员代码」证明

### 6.1 未触碰其他成员业务代码（实测）

```
$ git --no-pager diff --name-only -- \
    backend/app/core/security.py backend/app/services/auth_service.py \
    backend/app/models backend/app/schemas backend/app/api/auth \
    backend/app/api/test backend/app/api/ai_support backend/app/services/ai_service.py \
    backend/app/services/email_service.py frontend/src backend/.env
=> EMPTY_CONFIRMED（无输出）
```

- **A**：`core/security.py`、`auth_service.py`、`api/auth`、`models/user.py` 未改（仅只读读取 `User.email`）。
- **B**：`CounselorService` 全部方法（咨询师信息、`get_available_slots` 排班时段、申请/审核/启停）、`api/counselor/__init__.py` 中 B 路由异常分支、前端排班页面均未改；P2-13 实测 B 两个接口行为不变。
- **D / E**：`api/test`、`api/ai_support`、`services/ai_service.py` 等零改动。
- **共享文件**只改 C 路由函数体与 `AppointmentService` 的 3 个方法；`api/counselor/__init__.py` 与 `api/consultation/__init__.py` 的完整 Diff 已在 3.2 / 3.3 逐行列出，可核对未触及 B 路由与权限 helper。

### 6.2 数据库只读核查

- 本轮**未修改** `backend/app/models/*`、`backend/app/schemas/*`、`backend/sql/*`（含 `init.sql`、`migrate.sql`、`migrate_e_ai_support.sql`）、索引、约束；未执行 DDL、迁移或历史数据回填。
- 测试代码与修复代码中无任何 `CREATE/ALTER/DROP INDEX/ADD CONSTRAINT` 语句；隔离数据仅 `INSERT` / `DELETE`。
- 四套测试结束后只读核查：`users=2`、`counselors=1`，`appointments / consultation_reviews / consultation_messages / counselor_inquiries / inquiry_messages / notifications` 全部为 0，与交付基线一致；`E2E_C_% / E2E_UI_% / E2E_P2_%` 残留账号 **0 条**；`TC-049` 与 P2 脚本的 `baseline_restored=true` 均通过。
- 唯一版本化 SQL 差异为工作区原有的 `init.sql` 中 `test_progress.answers` JSON 默认值语法修正（D 模块、13:15:31），**非本轮**。

> 沿用边界审查的诚实声明：缺少本轮开始前的完整 DDL 快照，故不声称「严格证明数据库结构完全未变更」；可确认的是本轮未通过任何版本化文件或语句引入 DDL，且表创建时间、索引/约束清单与既有定义一致。

---

## 七、仍然存在的问题

1. **TC-035 预约改期**：未实现功能（`FEATURE_GAP`），按约束不开发、不计为 Bug。
2. **9 项静态代码线索**（并发双订的其他路径、审核接口疑似无鉴权、inquiry / signals 越权、`init.sql` 与 `migrate.sql` DDL 分歧等）：见 `C_MODULE_TEST_REPORT.md` 第七节，**本次仍未实测**，不作为测试结论。
3. **存量数据偏差**：按要求未执行历史回填；咨询师历史评分统计的历史偏差仍在（本阶段未涉及该问题，P1 修复只保证此后新评价正确）。
4. **邮件服务「静默吞异常」的可观测性**：本阶段按最小修改原则保留原有 `logger.error` 兜底，未增强告警；BUG-08 的根因（取错邮箱属性）已修。
5. **咨询师邮件修复后会真实发出**（正式环境按原配置）：这是原项目功能恢复，非新增发送机制；已在确认项 3 中获准。测试期间由 Mock 完全隔离。
6. **时间规则**：仍是 09:00–19:00 整点 / 60 分钟硬编码；创建侧不校验营业时段与整点对齐，属已知设计限制（B 负责人确认前不引入新限制）。
7. **`counselor_service.py` 仍是 B/C/管理端共享文件**：本阶段只改 C 方法；长期按职责拆分需团队另行决定，本阶段不重构。

---

## 八、结论与暂停声明

- BUG-04/05/06/07/08 均以最小修改修复，全部复用原项目已有逻辑：路由内**已有**的 `HTTPException(403)` 通过新增 `except HTTPException: raise` 正常返回；BUG-06 复用服务层**已有**的 `Counselor.user_id` 查询；BUG-08 复用**已有**邮件函数与 `users` 表；未新建权限系统、未加字段、未改公共邮件服务、未改前端。
- 四套回归全部实际执行：P2 `6/9 → 15/0`、P1 `11/11`、完整 API `42 PASS/7 FAIL → 49 PASS/0 FAIL/1 FEATURE_GAP`、浏览器 `6/6`，**无新增失败**，P1 成果保持。
- 修改前后 Git 状态与完整 Diff 已列出；A/B/D/E 业务代码差异为空；数据库结构、模型、SQL、索引、约束、迁移均未改动，未执行 DDL/回填；隔离数据全部清理，库回到基线。
- 测试邮件全程 Mock，后端已恢复原项目邮件配置；三个服务（3307 / 8000 / 5173）正常。
- 未把任何未执行的测试标记为通过，未修改既有测试断言，未把未实现功能当作必须开发。

**本阶段到此暂停，等待下一步指令。**
