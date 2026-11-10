# C 模块第一阶段 P1 Bug 修复报告

> 依据：`C_MODULE_TEST_REPORT.md`（2026-11-09）
> 本阶段范围：**仅 BUG-01 / BUG-02 / BUG-03 三个 P1**
> 报告日期：2026-11-09　｜　状态：**已完成并暂停**，未继续修复 P2/P3、未开发新功能
> 凭据声明：本报告不含账号、密码、Token、密钥或真实用户个人信息；测试账号均为隔离账号，密码运行时随机生成且不落盘。

---

## 一、修改的文件

### 1.1 业务代码（唯一修改文件）

| 文件 | 变更量 | 说明 |
|---|---|---|
| `backend/app/services/counselor_service.py` | +85 / -29 行 | 唯一被修改的业务代码文件，属于 C 模块服务层 |

`git diff --stat` 实测：`1 file changed, 85 insertions(+), 29 deletions(-)`。

**未修改**：模型（`models/counselor.py`）、Schema、路由（`api/counselor/__init__.py`、`api/consultation/__init__.py`）、数据库 DDL / `sql/*.sql`、前端任何文件、`.env`、`docker-compose.yml`、其他成员负责的模块。运行时 OpenAPI 路径数修复前后均为 **106**，接口路径与响应结构未变。

> 说明：`git status` 中另有 `backend/docker-compose.yml`、`backend/sql/init.sql` 等 `M` 状态及若干 `??` 条目，均为工作区**原有**未提交状态，本次会话未读取写入、未触碰。

### 1.2 测试文件（新增，位于 `e2e_c_module/`）

| 文件 | 作用 |
|---|---|
| `e2e_c_module/regression_p1.py` | 本次新增的 P1 专项回归套件（11 例），支持 `--label before/after` |
| `e2e_c_module/regression_p1_before.json` | 修复前真实执行结果 |
| `e2e_c_module/regression_p1_after.json` | 修复后真实执行结果 |
| `e2e_c_module/run_e2e.py`、`browser_e2e.py`、`common.py`、`show_results.py` | 既有套件，本阶段**未修改**，仅重新执行 |
| `e2e_c_module/results.json`、`browser_results.json` | 本阶段重跑后的结果文件 |

---

## 二、根因复核（第一步）

| Bug | 根因（复核后确认） | 证据 |
|---|---|---|
| **BUG-01** | `get_counselor_appointments` 使用 `appt.user` 读取预约人信息，但 `backend/app/models/counselor.py:111-112` 的 `Appointment` 只定义了 `counselor` 与 `review` 两个 relationship，**没有 `user` 关系**。访问即抛 `AttributeError`，被路由 `api/counselor/__init__.py:437-442` 包装成 500。 | 修复前 `P1-01` 响应 `500 {"detail":"获取咨询师预约列表失败: 'Appointment' object has no attribute 'user'"}` |
| **BUG-02** | `submit_review` 在 `db.add(review)` 之后立即查询 `ConsultationReview` 重算统计，但 `backend/app/core/database.py:49` 的 `SessionLocal(autoflush=False)` 不会在查询前自动 flush，新评价尚未进入当前事务，统计永远滞后一条。 | 修复前第 1 次评价后 `counselors=5.0/0`、实际聚合 `4.5/1`；第 2 次后 `counselors=4.5/1`、实际聚合 `4.0/2`（恰好滞后一条） |
| **BUG-03** | `create_appointment`（原 `:569-576`）与 `get_available_slots`（原 `:150-154`）**各自重复**实现「`appointment_date == 传入时间`」的等值冲突判断，完全忽略 `Appointment.duration=60`；两处状态白名单硬编码重复；没有任何事务级并发保护。 | 修复前 `12:00` 与 `12:30` 可同时预约；`17:30` 预约后 slots 的 `17:00`/`18:00` 仍显示可用；并发 `[200,200]` 产生 2 条重叠有效预约 |

---

## 三、具体修改内容（第二步 / 第三步）

所有改动集中在 `backend/app/services/counselor_service.py`，遵循最小改动原则。

### 3.1 BUG-03：抽取统一的区间冲突判定（核心改动）

在模块顶部（所有 import 之后）新增常量与 4 个纯函数/查询函数：

| 新增符号 | 作用 |
|---|---|
| `ACTIVE_APPOINTMENT_STATUSES` | 统一「占用时段」的状态白名单 `('pending','confirmed','in_progress')`；`cancelled` / `refunded` / `completed` 统一释放时段 |
| `DEFAULT_APPOINTMENT_MINUTES = 60` | 统一默认时长，与 `Appointment.duration` 一致；创建预约写入时长时改用此常量，避免两处漂移 |
| `_MAX_APPOINTMENT_MINUTES` | 查询窗口向前回溯的预筛上界（24h），覆盖任意单条预约时长 |
| `_appointment_interval(start, duration)` | 返回半开区间 `[start, start+duration)`；`duration` 为空/非正数时回退 60 分钟 |
| `_intervals_overlap(...)` | 半开区间重叠判断 `a_start < b_end and b_start < a_end`，**首尾相接不算冲突** |
| `_active_appointments_in_window(db, ...)` | 按开始时间做与数据库方言无关的范围预筛（MySQL / SQLite 通用），避免依赖 `DATE_ADD` 等专有函数 |
| `_has_time_conflict(db, counselor_id, start, duration, appointments=None, exclude_appointment_id=None)` | 精确判断新区间与已有有效预约是否重叠；支持调用方一次性预取候选行，供 `slots` 复用 |

**两处调用方统一**：

- `CounselorService.get_available_slots`：由「每个整点各查一次 DB、等值判断」改为「当天一次性预取有效预约 + 对每个整点调用 `_has_time_conflict`」。`TimeSlot` 的 `time` / `available` / `price` 字段与取值口径不变，仅 `available` 计算更准确。
- `AppointmentService.create_appointment`：移除原等值查询，改为 `_has_time_conflict(...)`；错误消息仍为「该时段已被预约」，前端与既有测试无需改动。

**并发保护（不依赖 DDL）**：

```python
counselor = db.query(Counselor).filter(
    Counselor.id == ...,
    ...
).with_for_update().first()
```

在**同一事务内**对咨询师行加排他锁，使同一咨询师的并发创建串行化；第二个请求在第一个 `commit()` 释放锁后重新读取，能看到刚插入的预约从而被区间冲突校验拦截。冲突检查位于加锁之后、`db.commit()` 之前；若校验失败抛 `ValueError`，`core/database.py:63-66` 的 `get_db()` 会 `rollback()` 释放锁。`SQLite` 不支持 `FOR UPDATE`，SQLAlchemy 会自动忽略，本地 SQLite 调试模式不受影响。

> 按约束，**未使用数据库唯一索引代替区间校验**，也**未执行任何 DDL / 迁移**。第七节给出可选的纵深防御方案，等待确认。

### 3.2 BUG-01：显式查询用户替代未定义的关系

`get_counselor_appointments` 中把 `if appt.user: ... appt.user.xxx` 改为：

```python
from app.models.user import User
user = db.query(User).filter(User.id == appt.user_id).first()
if user:
    appt_data.user_info = {
        "id": user.id, "nickname": user.nickname,
        "email": user.email, "phone": user.phone
    }
```

- 与 `get_appointment_detail`、`get_counselor_orders` 中已有的同类写法保持一致；
- `user_info` 的字段名与结构（`id/nickname/email/phone`）**完全不变**，不改模型、不给 `Appointment` 增加 relationship，避免影响其他模块与 ORM 加载行为。

### 3.3 BUG-02：重算统计前 flush

```python
db.add(review)
db.flush()   # 新增：autoflush=False 下必须显式 flush
# 之后才查询 ConsultationReview 聚合、更新 counselor.rating / review_count
```

不改统计公式、不改响应结构、不改表字段。

### 3.4 兼容性核对

| 项 | 结果 |
|---|---|
| 接口路径 | 未变；运行时 OpenAPI 修复前后均 106 条路径 |
| 响应结构 | `AppointmentResponse` / `TimeSlot` / `ReviewResponse` 未改；`user_info` 字段保持一致；错误消息「该时段已被预约」保持不变 |
| 数据库字段 / DDL | 未改；无迁移、无回填 |
| 前端交互 | 未改；浏览器 E2E 6/6 通过 |
| 其他模块 | 未改 |

---

## 四、测试命令与真实执行结果（第四步 / 第五步）

### 4.1 环境准备（真实执行）

```
# 修复前基线：后端为原始代码
python e2e_c_module/regression_p1.py --label before

# 修改 counselor_service.py 后，重启后端加载新代码
Stop-Process <8000 端口进程> ; Start-Process python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
GET http://127.0.0.1:8000/openapi.json  -> 200 / 106 paths

python e2e_c_module/regression_p1.py --label after
python e2e_c_module/run_e2e.py
python e2e_c_module/browser_e2e.py
```

解释器：`backend/.venv/Scripts/python.exe`（Python 3.12.4）。所有命令均已实际执行，以下统计来自结果文件，未把任何未执行项标记为通过。

### 4.2 P1 专项回归（11 例，同一脚本、同一断言，修复前后各跑一次）

| 用例 | 场景 | 修复前 | 修复后 |
|---|---|---|---|
| P1-01 | BUG-01 咨询师查看自己收到的预约列表 | **FAIL** 500 | **PASS** 200 |
| P1-02 | BUG-02 首次评价后统计更新 | **FAIL** | **PASS** |
| P1-03 | BUG-02 第二条评价累计更新 | **FAIL** | **PASS** |
| P1-04 | 等值冲突仍被拒（不回归） | PASS | PASS |
| P1-05 | 半小时重叠 12:00 / 12:30 被拒 | **FAIL** | **PASS** |
| P1-06 | 首尾相接 12:00 / 13:00 不误判 | PASS | PASS |
| P1-07 | 反向重叠（已有 14:30，再约 14:00）被拒 | **FAIL** | **PASS** |
| P1-08 | `cancelled`（学生取消）释放时段 | PASS | PASS |
| P1-09 | `cancelled`（咨询师拒绝）释放时段 | PASS | PASS |
| P1-10 | slots 与 create 统一：17:30 占用 17:00 与 18:00 | **FAIL** | **PASS** |
| P1-11 | 并发创建 11:00 与 11:30 只成功一个 | **FAIL** | **PASS** |

**统计：修复前 `4 PASS / 7 FAIL` → 修复后 `11 PASS / 0 FAIL`**；两次 `cleanup.baseline_restored = true`。

### 4.3 完整接口套件重跑（`run_e2e.py`，50 例）

| | 修复前（上一轮报告） | 修复后（本轮实测） |
|---|---|---|
| PASS | 39 | **42** |
| FAIL | 10 | **7** |
| FEATURE_GAP | 1 | 1 |
| 阻塞 / 未执行 | 0 / 0 | 0 / 0 |

由 FAIL 转 PASS 的正是三个目标用例：**TC-016（BUG-02）、TC-025（BUG-03）、TC-047（BUG-01）**。其余 7 个 FAIL 与 1 个 FEATURE_GAP **逐项保持不变**，无新增失败、无状态倒退。TC-048（数据库一致性）、TC-049（隔离清理与基线恢复）均为 PASS。

### 4.4 浏览器端到端重跑（`browser_e2e.py`，6 例）

| 用例 | 修复前 | 修复后 |
|---|---|---|
| UI-01 咨询师卡片由真实接口渲染 | PASS | PASS |
| UI-02 登录页真实登录 | PASS | PASS |
| UI-03a 浏览器会话令牌创建预约 | PASS | PASS |
| UI-03b 订单页显示编号与「待确认」 | PASS | PASS |
| UI-04 点击取消 → DB `cancelled`、页面「已取消」 | PASS | PASS |
| UI-05 未登录路由守卫重定向 | PASS | PASS |

**6 PASS / 0 FAIL**，前端无回归，`page_errors=[]`。

### 4.5 数据与运行态核对

- 三套测试结束后数据库：`users=2, counselors=1`，其余 C 模块表均为 0，与交付基线完全一致；`E2E_C_%` / `E2E_UI_%` / `E2E_P1_%` 残留账号 **0 条**。
- 修复后后端错误日志中 `FOR UPDATE / Deadlock / Lock wait / OperationalError / Traceback` 匹配数 **0**，行锁未引入异常。
- 未删除、清空、重建任何数据库或 Docker 数据卷；未修改 `.env` 凭据；三个服务（3307 / 8000 / 5173）测试后仍正常监听。

---

## 五、修复前后对比（关键证据）

| 观测点 | 修复前实测 | 修复后实测 |
|---|---|---|
| `GET /api/appointment/counselor/list` | `500 {"detail":"获取咨询师预约列表失败: 'Appointment' object has no attribute 'user'"}`；`items=0` | `200`，`total=2`，`items=2`，两条均含完整 `user_info` |
| 第 1 次评价后 `counselors` vs 聚合 | `rating=5.0, review_count=0` vs `AVG=4.5, COUNT=1` | `rating=4.5, review_count=1` vs `AVG=4.5, COUNT=1` |
| 第 2 次评价后 `counselors` vs 聚合 | `rating=4.5, review_count=1` vs `AVG=4.0, COUNT=2`（滞后一条） | `rating=4.0, review_count=2` vs `AVG=4.0, COUNT=2` |
| 已有 12:00 再创建 12:30 | `200 预约创建成功`，有效重叠预约 `2` 条 | `400 {"detail":"该时段已被预约"}`，有效重叠预约 `1` 条 |
| 已有 14:30 再创建 14:00 | `200`（放行） | `400`（拦截） |
| 相邻 12:00 / 13:00 | `200` | `200`（未误判，兼容性保持） |
| 创建 17:30 后查询 slots | `17:00-18:00=true`、`18:00-19:00=true` | `17:00-18:00=false`、`18:00-19:00=false`，`09:00-10:00=true` |
| 并发创建 11:00 与 11:30 | HTTP `[200, 200]`，DB 有效预约 `2` 条 | HTTP `[200, 400]`，DB 有效预约 `1` 条 |
| 取消 / 拒绝后重新预约 | `200` | `200`（状态语义保持） |

---

## 六、仍然存在的问题

### 6.1 本阶段范围外、保持原状的 7 个失败用例（P2/P3，未修改）

| 用例 | 对应缺陷 | 当前表现 |
|---|---|---|
| TC-030 | BUG-05 | 带时区 ISO 时间（`Z`）触发 aware/naive 比较 `TypeError` → 500 |
| TC-036 | BUG-04 | 学生B 读他人预约详情，越权被拦截但返回 500（期望 403） |
| TC-040 | BUG-04 | 学生访问咨询师订单列表 → 500（期望 403） |
| TC-041 | BUG-04 | 学生处理订单 → 500（期望 403） |
| TC-042 | BUG-04 / BUG-06 | 学生访问 `/appointment/counselor/list` → 500，且该接口无角色校验 |
| TC-037 / TC-038 | BUG-07 | 越权取消 / 越权评价返回 400「预约不存在」而非 403 |

以上**权限隔离本身有效**（DB 未被越权修改、无数据泄漏），属于错误码契约问题。按要求本阶段未处理。

### 6.2 其他未处理项

- **BUG-08**：咨询师邮件通知静默失败（`'Counselor' object has no attribute 'email'`），仍存在；P2，未在本阶段范围。
- **TC-035**：预约改期仍为未实现功能（OpenAPI 无该路由，`PUT → 405`、`/reschedule → 404`），记为 `FEATURE_GAP`，不是缺陷也未新开发。
- **历史数据**：按要求**未执行任何生产数据迁移或历史回填**，因此存量 `counselors.rating / review_count` 与历史评价聚合的偏差仍然存在；修复只保证**此后新提交的评价**统计正确。回填方案需另行确认。
- **数据库纵深防御未加**：见第七节。
- **静态线索 9 项**（并发双订的其他路径、审核接口疑似无鉴权、inquiry 越权、DDL 分歧等）仍未实测，见原测试报告第七节。
- **已知设计限制（非回归）**：`get_available_slots` 仍只返回 09:00–19:00 整点时段；非整点预约只能通过 `available=false` 体现，不能展示更细的剩余可约区间。预筛常量 `_MAX_APPOINTMENT_MINUTES=24*60` 假设单条预约不超过 24 小时，若未来开放更长时长需同步调整。

---

## 七、数据库结构调整方案（仅提出，**等待确认，未执行**）

本阶段**没有做任何 DDL 变更**：BUG-03 的完整性由应用层区间校验保证，并发保护由事务内 `SELECT ... FOR UPDATE` 行锁保证，不需要新增索引即可正确工作。

若后续希望增加纵深防御，可选方案（**需先确认后再实施**）：

1. 目标：为 `appointments` 增加 `(counselor_id, appointment_date)` 唯一索引，仅用于兜住「完全等值」的并发插入，**不可替代区间冲突校验**（12:00 与 12:30 仍然不同值）。
2. 前置检查：先只读扫描存量数据 `SELECT counselor_id, appointment_date, COUNT(*) FROM appointments WHERE status IN (...) GROUP BY 1,2 HAVING COUNT(*)>1`，确认无重复；若有重复需先业务确认处置方式。
3. 迁移窗口：8.0 支持在线 DDL，但仍需评估表大小与锁等待；建议在低峰执行 `ALTER TABLE ... ADD UNIQUE KEY ...`，并准备回滚（仅 DROP INDEX，不动数据）。
4. 代码配合：捕获唯一键冲突转换为 400「该时段已被预约」，避免 500。
5. 该索引无法覆盖区间重叠，真正的并发区间保护仍依赖本阶段实现的行锁。

**当前状态：方案已提出，未执行、未改表、未回填，等待确认。**

---

## 八、结论与暂停声明

- 三个 P1（BUG-01 / BUG-02 / BUG-03）已按最小改动修复，并由 11 条 P1 专项回归、50 条接口套件、6 条浏览器 E2E 的真实执行结果验证。
- 修复前后对比明确：P1 专项 `4/7 → 11/0`，完整接口 `39 PASS/10 FAIL → 42 PASS/7 FAIL`，浏览器 `6/0 → 6/0`，**无新增回归**。
- 未修改其他模块、未改 `.env`、未做 DDL / 迁移 / 历史回填、未删除或重建数据库与 Docker 数据卷；隔离数据全部按主键清理，最终库回到基线。
- 未把任何未执行的测试标记为通过；所有数字来自 `regression_p1_before.json` / `regression_p1_after.json` / `results.json` / `browser_results.json`。

**本阶段到此暂停**：未继续修复 P2/P3（BUG-04~BUG-08），未开发改期、排班等新功能。等待下一步指令。
