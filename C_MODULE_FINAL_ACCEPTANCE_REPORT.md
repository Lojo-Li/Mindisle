# C 模块最终回归验收报告

> 验收日期：2026-11-09　｜　执行时段：18:37–18:39（四套回归），18:36 前置检查，18:4x 恢复与复核
> 依据：`C_MODULE_HANDOFF.md` 及其中引用的四份 C 模块报告
> 范围：C 模块（心理咨询预约、取消、状态管理、评价反馈）**最终回归验收**
> 性质：**只执行现有测试**。未修改业务代码、前端、数据库结构、配置文件或测试断言；未执行 DDL / 迁移 / 回填；未执行 Git commit / push / merge；未清理工作区未跟踪文件。
> 凭据声明：本报告不含账号、密码、Token、密钥或真实用户个人信息；测试账号均为隔离账号，密码运行时随机生成且不落盘。

---

## 一、验收结论

| 项 | 结果 |
|---|---|
| 四套回归 | **全部实际执行完成，0 FAIL** |
| 用例执行记录合计 | 82 条：`81 PASS / 0 FAIL / 1 FEATURE_GAP` |
| 断言型通过率 | **81 / 81 = 100.0%**（初始测试为 45/55 = 81.8%） |
| 含功能缺口的 PASS 占比 | 81 / 82 = 98.8% |
| 唯一非 PASS 用例 | `TC-035` 预约改期 = `FEATURE_GAP`（未实现功能，不是缺陷） |
| 数据合规 | 每套测试后及验收结束时，数据库均回到验收前基线；原有业务数据摘要前后完全一致；隔离残留 0 |
| 邮件合规 | 全程 Mock，未向任何真实邮箱发信 |
| 运行态 | 原配置后端已恢复，OpenAPI 106 路径；前端 200；MySQL healthy |
| Git | 验收前后状态与 Diff 完全一致；未提交、未清理 |

> 82 是四套套件的**执行记录数**，套件之间存在同一场景的交叉覆盖，不是 82 个独立业务场景。

---

## 二、约束逐条合规对照

| # | 要求 | 落实情况 |
|---|---|---|
| 1 | 只执行现有测试，不改业务代码/前端/DB 结构/配置/测试断言 | 仅运行 `e2e_c_module/` 下既有 4 个脚本；Git Diff 验收前后完全一致；未触碰 `.env`、`docker-compose.yml`、`init.sql`、模型、Schema、前端文件 |
| 2 | 允许创建/清理隔离数据，不得改动原有业务数据 | 脚本按 `E2E_C_ / E2E_UI_ / E2E_P1_ / E2E_P2_` 前缀造数、按主键精确清理；前后对比原有 `users`(ID 1/2) 与 `counselors`(ID 1) 的角色、状态、删除标记完全一致 |
| 3 | 邮件必须 Mock，不得真实发信 | 测试期间 8000 端口由 `run_backend_mail_mock.py` 独占；见第六节证据 |
| 4 | 依次执行完整 API → 浏览器 → P1 → P2 | 严格按此顺序执行，见第四节 |
| 5 | 测试前后记录 Git 状态与数据库基线并确保恢复 | 验收前、每套后、验收结束共 6 次基线核对，全部 `BASELINE_OK True`；见第三、七、九节 |
| 6 | 环境或基线不符立即停止、不重建数据库 | 前置检查全部符合预期（见第三节）；未发生中止，未执行任何建库/初始化/迁移脚本 |
| 7 | 恢复原后端运行状态 | 已恢复为原配置 `uvicorn app.main:app`，命令行与验收前一致；见第八节 |
| 8 | 输出最终验收报告，记录真实通过率、失败原因、剩余功能缺口 | 本文件；见第一、五、十节 |
| 9 | 不 commit / push / merge，不自动清理未跟踪文件 | 未执行任何 Git 写操作；未删除任何未跟踪文件 |

---

## 三、验收前前置检查与基线（全部符合预期）

| 检查项 | 验收前实测 |
|---|---|
| Git 状态 | `M` 5 项、`??` 11 项（与交接文档第七节一致）；`HEAD = 78951af \| 2026-11-09 10:25:02 +0800` |
| `git diff --numstat` | `4/0`、`8/0`、`118/47`（3 个 C 业务文件）；`1/1`、`1/1`（工作区原有的 `docker-compose.yml`、`init.sql`） |
| 后端 | `http://127.0.0.1:8000`，`GET /openapi.json` → 200 / **106 paths**；进程为**原配置** `-m uvicorn app.main:app --host 127.0.0.1 --port 8000`（PID 424616） |
| 前端 | `http://127.0.0.1:5173/` → 200（Vite） |
| MySQL | 容器 `soulstation-mysql` healthy，主机 3307 → 3306 |
| 数据库行数 | `users=2, counselors=1`；`appointments / consultation_reviews / consultation_messages / counselor_inquiries / inquiry_messages / notifications` 全部 0 |
| 原有业务数据摘要 | `users`: `[[1, counselor, active, 未删除], [2, user, active, 未删除]]`；`counselors`: `[[1, user_id=1, active, approved, 未删除]]` |
| 隔离残留 | `E2E_%` 前缀 users / counselors / appointments 均 0 |

Redis 未启动而回退内存存储、RAG 预热 NumPy 兼容告警，均为已知环境项（RAG 问题已由用户明确排除），不影响 C 模块用例，不视为环境不符合预期。

---

## 四、执行顺序、命令与时间戳

测试期间后端由 `e2e_c_module/run_backend_mail_mock.py` 启动（日志 `MAIL_MOCK_ENABLED: SMTP + 3 senders patched, no real mail`），启动后 OpenAPI 复核仍为 106 路径。

| 顺序 | 套件 | 命令 | 运行标识 |
|---|---|---|---|
| 1 | 完整 API（50 例） | `backend\.venv\Scripts\python.exe e2e_c_module\run_e2e.py` | `run_tag=20261109183723` |
| 2 | 浏览器 E2E（6 例） | `backend\.venv\Scripts\python.exe e2e_c_module\browser_e2e.py` | `run_tag=E2E_UI_20261109183747` |
| 3 | P1 专项（11 例） | `backend\.venv\Scripts\python.exe e2e_c_module\regression_p1.py --label after` | `run_at=2026-11-09 18:38:42` |
| 4 | P2 专项（15 例） | `backend\.venv\Scripts\python.exe e2e_c_module\regression_p2.py --label after` | `run_at=2026-11-09 18:38:58` |

解释器：`backend/.venv/Scripts/python.exe`（Python 3.12.4），执行前设置 `$env:PYTHONIOENCODING='utf-8'`。四套 `LASTEXITCODE` 均为 `0`。

---

## 五、真实结果与通过率

| 套件 | 用例数 | PASS | FAIL | FEATURE_GAP | 断言型通过率 | 退出码 |
|---|---:|---:|---:|---:|---:|---:|
| 完整 API `run_e2e.py` | 50 | 49 | **0** | 1（TC-035） | 49/49 = 100% | 0 |
| 浏览器 `browser_e2e.py` | 6 | 6 | **0** | 0 | 6/6 = 100% | 0 |
| P1 `regression_p1.py` | 11 | 11 | **0** | 0 | 11/11 = 100% | 0 |
| P2 `regression_p2.py` | 15 | 15 | **0** | 0 | 15/15 = 100% | 0 |
| **合计** | **82** | **81** | **0** | **1** | **81/81 = 100%** | — |

结果文件统计复核：`results.json` `{"PASS":49,"FEATURE_GAP":1}`、`browser_results.json` `{"PASS":6,"FAIL":0}`、`regression_p1_after.json` `{"PASS":11,"FAIL":0}`、`regression_p2_after.json` `{"PASS":15,"FAIL":0}`；P1/P2 的 `cleanup.baseline_restored` 均为 `True`。

**关键用例**：`TC-048`（数据库一致性）PASS；`TC-049`（隔离清理与基线恢复）PASS；`P1-11`（并发重叠时段只成功一个）PASS；`P2-03`（前端原日期格式无回归）PASS；`P2-13`（B 模块列表/slots 无回归）PASS；`P2-15`（咨询师邮件 Mock 事件）PASS。

### 5.1 失败原因

**本次验收 0 个 FAIL，因此没有失败原因需要归因。** 需要说明的非 PASS 与非致命项：

1. `TC-035` 预约改期记为 `FEATURE_GAP`：运行时 OpenAPI 改期路径为 0、`PUT/PATCH` 路径为 0，实测 `PUT → 405`、`POST /api/appointment/{id}/reschedule → 404`，前端无入口。属于**需求未实现**，按既定口径不计为 Bug、不参与通过率分母。
2. 后端启动日志中的 `Redis连接失败 → 回退内存存储模式`、`[RAG预热] 失败（不影响服务启动）: np.float_ ...`：均为已知环境项，服务启动完成、OpenAPI 106 路径，未导致任何用例失败或被跳过。
3. 恢复后端时首次尝试用 base Python 直启报 `ModuleNotFoundError: No module named 'fastapi'`，改用项目 `.venv` 解释器后成功（见第八节）。该插曲只涉及进程启动方式，未改动任何文件、数据或断言。

### 5.2 与初始测试对比

| | 初始测试 | 最终验收 |
|---|---|---|
| 完整接口 | 39 PASS / 10 FAIL / 1 FEATURE_GAP | **49 PASS / 0 FAIL / 1 FEATURE_GAP** |
| 断言型通过率（整体） | 45/55 = 81.8% | **81/81 = 100%** |
| 浏览器 | 6/6 | 6/6 |
| OpenAPI 路径数 | 106 | 106（未变） |

---

## 六、邮件 Mock 隔离证据

| 证据 | 结果 |
|---|---|
| Mock 启动器 | `run_backend_mail_mock.py`，用标准库 `unittest.mock.patch.object` 替换 `EmailService.create_smtp_connection` 及 3 个发信入口；日志 `[E2E] MAIL_MOCK_ENABLED: SMTP + 3 senders patched, no real mail` |
| 8000 端口归属 | 测试期间监听进程命令行即 `run_backend_mail_mock.py`；四套测试全程在该后端下执行 |
| Mock 事件 | `mail_mock_events.jsonl` 累计 118 条：`confirmation_user=50`、`confirmation_counselor=46`、`cancelled=22` |
| 收件域名 | 全部事件域名统计为 **`example.com` 118 条**，无其他域名、无真实邮箱；事件记录仅含事件名、是否带地址、域名，不含邮箱明文 |
| P2-15 断言 | `confirmation_counselor` 1 条且带地址、`cancelled` 2 条（用户 + 咨询师）、后端新增日志无 `'Counselor' object has no attribute 'email'` |
| 后端日志扫描 | SMTP 相关唯一命中行为 Mock 提示本身；无 SMTP 连接、发信失败或 5xx 异常 |

**结论：测试期间未调用真实 SMTP，未向任何真实邮箱发送测试邮件。** 测试结束后 Mock 后端已停止，正式环境恢复原邮件配置（BUG-08 修复后按原配置真实发信的行为保持不变）。

---

## 七、数据库数据基线：前后对比与逐套核对

| 表 | 验收前 | 套件1后 | 套件2后 | 套件3后 | 套件4后 / 验收结束 |
|---|---:|---:|---:|---:|---:|
| users | 2 | 2 | 2 | 2 | **2** |
| counselors | 1 | 1 | 1 | 1 | **1** |
| appointments | 0 | 0 | 0 | 0 | **0** |
| consultation_reviews | 0 | 0 | 0 | 0 | **0** |
| consultation_messages | 0 | 0 | 0 | 0 | **0** |
| counselor_inquiries | 0 | 0 | 0 | 0 | **0** |
| inquiry_messages | 0 | 0 | 0 | 0 | **0** |
| notifications | 0 | 0 | 0 | 0 | **0** |

- 每次核对均输出 `BASELINE_OK True`；`E2E_%` 隔离残留（users / counselors / appointments）全程为 0。
- 原有业务数据摘要验收前后完全一致：`users [[1,counselor,active,0],[2,user,active,0]]`、`counselors [[1,1,active,approved,0]]`，未被修改或删除。
- `browser_results.json` 的 `db_after` 与基线一致，清理明细为按主键删除隔离数据（`appointments:-1`、`notifications:-3`、`counselors:-1`、`users:-2`）。
- 本轮**未执行任何 DDL、迁移、历史回填或结构变更**；`C_MODULE_HANDOFF.md` 第八节关于「缺少修复前完整 DDL 快照、只有有限保证」的声明仍然适用，本轮不新增结构层面的绝对性结论。

---

## 八、后端运行状态恢复

| 阶段 | 状态 |
|---|---|
| 验收前 | 原配置 `uvicorn app.main:app --host 127.0.0.1 --port 8000`（PID 424616，命令行显示 base Python） |
| 测试期间 | 邮件 Mock 后端（launcher PID 463308 / 监听 PID 458064）独占 8000 |
| 恢复过程 | 停止 Mock 进程（两个 PID 均已退出）；首次用 base Python 直启因缺少 `fastapi` 失败；改用 `backend\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000`（工作目录 `backend`）成功 |
| 验收结束 | 监听 PID 468428，命令行与验收前**完全一致**：`"D:\dev\python\python.3.12.4\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000`；`GET /openapi.json` → 200 / **106 paths** |
| 其他服务 | 前端 5173 → 200；MySQL 3307 healthy；Mock 进程已全部退出；`mail_mock_events.jsonl` 不再增长 |

即：**后端已回到「原配置、非 Mock、原命令、原端口」的运行状态**，邮件行为恢复为项目原有逻辑。

---

## 九、Git 状态前后对比

验收前后 `git status --short` 输出**完全一致**：

```
 M backend/app/api/consultation/__init__.py
 M backend/app/api/counselor/__init__.py
 M backend/app/services/counselor_service.py
 M backend/docker-compose.yml            <- 工作区原有，非本轮
 M backend/sql/init.sql                  <- 工作区原有，非本轮
?? C_MODULE_BOUNDARY_REVIEW.md / C_MODULE_HANDOFF.md
?? C_MODULE_P1_FIX_REPORT.md / C_MODULE_P2_FIX_REPORT.md / C_MODULE_TEST_REPORT.md
?? backend/seeds/_demo_articles.py / backend/seeds/_fix_admin_table.py
?? dev-start.sh / e2e_c_module/ / frontend/scripts/screenshot.mjs / screenshots/
```

`git diff --numstat` 前后完全一致（`4/0`、`8/0`、`118/47`、`1/1`、`1/1`）；`HEAD` 仍为 `78951af`。未执行任何 commit / push / merge，未清理任何未跟踪文件。

本次验收产生的文件变更全部位于测试产物与报告：覆盖 `e2e_c_module/results.json`、`browser_results.json`、`regression_p1_after.json`、`regression_p2_after.json`、`backend.p2.err.log`、`backend.restored.*.log`；追加 `mail_mock_events.jsonl`；新增 `backend.final.out.log` 与本报告。

---

## 十、剩余功能缺口与未处理问题

### 10.1 本次实测确认的功能缺口

| 缺口 | 证据 | 判定 |
|---|---|---|
| **预约改期** | `TC-035` = `FEATURE_GAP`；OpenAPI 无改期路径，`PUT → 405`、`/reschedule → 404`，前端无入口 | 未实现功能，不是缺陷；未经确认不开发 |

### 10.2 依据既有报告登记、本次未重新验证的功能缺失（保持原状）

咨询师排班/可预约时间写入接口、评价修改/删除/咨询师回复、支付/退款、取消截止时间与提前预约限制、咨询师主动取消、独立「开始咨询」接口。详见 `C_MODULE_TEST_REPORT.md` 第 6 节与 `C_MODULE_HANDOFF.md` 第 10.1 节。

### 10.3 仍待处理的验证/确认类问题（本次验收范围外，未改动）

1. 9 项静态代码线索仍未实测（并发双订其他路径、审核接口疑似无鉴权、inquiry / `signals` 越权、`init.sql` 与 `migrate.sql` DDL 分歧等）。
2. B 负责人对 P1 已发生的 `get_available_slots` 跨模块改动尚未正式确认。
3. 历史 `counselors.rating / review_count` 存量偏差未回填（涉及数据变更，需单独授权）。
4. 缺少修复前完整 DDL 快照，数据库结构只有有限保证。
5. 正式配置下「咨询师邮件真实发出」尚未做独立验收（本次为 Mock 环境验收）。
6. 创建侧不校验营业时段/整点对齐、邮件失败静默兜底无告警，均为已知设计限制，按约定暂不实施。
7. 工作区原有未提交改动（`docker-compose.yml`、`init.sql`、`dev-start.sh`、seeds、`screenshots/` 等）归属未确认；C 模块成果尚未提交。
8. 项目无 PRD 文档；需求基线依据为 `README.md`、`backend/README.md`、`INTEGRATION.md`、原型页面与现有代码/报告。

**本次验收没有发现新的功能性 Bug，也没有产生新的跨模块或数据库结构改动。**

---

## 十一、验收产物

| 产物 | 路径 |
|---|---|
| 最终验收报告 | `C_MODULE_FINAL_ACCEPTANCE_REPORT.md`（本文件） |
| 完整 API 结果 | `e2e_c_module/results.json` |
| 浏览器结果 | `e2e_c_module/browser_results.json` |
| P1 回归结果 | `e2e_c_module/regression_p1_after.json` |
| P2 回归结果 | `e2e_c_module/regression_p2_after.json` |
| 邮件 Mock 事件 | `e2e_c_module/mail_mock_events.jsonl` |
| 后端日志 | `e2e_c_module/backend.final.out.log`、`backend.p2.err.log`、`backend.restored.out.log`、`backend.restored.err.log` |

---

## 十二、暂停声明

- 四套回归全部真实执行完成：`81 PASS / 0 FAIL / 1 FEATURE_GAP`，断言型通过率 **100%**；唯一 `FEATURE_GAP` 为预约改期。
- 数据库数据基线、原有业务数据、Git 状态与 Diff、后端运行态均已恢复/保持一致；邮件全程 Mock，无真实发信。
- 未修改业务代码、前端、数据库结构、配置或测试断言；未执行 DDL / 迁移 / 回填；未 commit / push / merge；未清理工作区未跟踪文件。
- **验收到此暂停，等待你确认提交范围后再进行任何提交或后续开发。**
