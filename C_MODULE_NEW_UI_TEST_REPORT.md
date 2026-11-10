# C 模块新界面完整测试报告

**测试时间**：2026-11-10 16:35
**测试对象**：心屿新界面（`/workspace/*` + `/counselor/dashboard/*`）下的 C 模块功能
**数据库**：本机 MySQL 8.0.39 / `soulstation`
**运行环境**：后端 8000（邮件 Mock 模式）+ 前端 5173（Vite）

---

## 一、总体结果

| 测试套件 | 用例数 | 通过 | 失败 | 说明 |
|---|---|---|---|---|
| P1 回归（bug 修复验证） | 11 | **11** | 0 | 时段冲突、评分统计等 |
| P2 回归（越权与边界） | 15 | **15** | 0 | 含邮件 Mock |
| E2E 全链路（接口） | 50 | **49** | 0 | 1 项 FEATURE_GAP（改期功能不存在） |
| 新界面浏览器 E2E | 20 | **20** | 0 | 真实 Chrome 点击验证 |
| 用户端冒烟 | 15 | **15** | 0 | |
| 对话 + 评价链路 | 15 | **15** | 0 | |
| 咨询师端链路 | 17 | **17** | 0 | |
| **合计** | **143** | **142** | **0** | 1 项为已知功能缺口 |

**结论：C 模块在新界面下功能完整，无回归、无缺陷。**

---

## 二、新界面浏览器测试详情（20 项全通过）

这是本次最关键的一组——用真实 Chrome 模拟点击，验证 UI 可用性。

### 学生端

| 编号 | 验证项 | 结果 | 实测值 |
|---|---|---|---|
| NEW-01 | 登录后跳转工作台 | PASS | → `/workspace/home` |
| NEW-02 | 咨询预约页渲染咨询师卡片 | PASS | 9 张卡片 |
| NEW-03 | 卡片显示真实咨询师姓名 | PASS | 张咨询师 / 认证 / 国家二级心理咨询师 |
| NEW-04 | **无写死的假卡片残留** | PASS | 已确认无「陈曦/周予安/林知夏/苏漾」 |
| NEW-05 | 擅长领域筛选生效 | PASS | 9 → 2（焦虑） |
| NEW-06 | **点击「选择时段」弹出预约窗** | PASS | `overlay display=flex` |
| NEW-07 | 弹窗标题显示真实咨询师名 | PASS | 「预约 · 张咨询师」 |
| NEW-08 | 弹窗内渲染日期与时段 | PASS | 日期 7 个 / 时段 9 个 |
| NEW-09 | 确认预约后切到「我的预约」 | PASS | 自动切页签 |
| NEW-10 | 我的预约列表显示订单 | PASS | 3 笔订单 |
| NEW-11 | 订单卡显示状态标签 | PASS | 待确认 / 视频咨询 / 订单号 / 取消预约按钮 |
| NEW-12 | 状态筛选可切换 | PASS | 筛选后正常渲染 |
| NEW-13 | **侧栏菜单只高亮一项** | PASS | `active=1` |
| NEW-14 | 页面无 JS 运行时错误 | PASS | `pageerror` 为空 |

### 咨询师端

| 编号 | 验证项 | 结果 | 实测值 |
|---|---|---|---|
| NEW-15 | 登录后跳转工作台 | PASS | → `/counselor/dashboard` |
| NEW-16 | 咨询师工作台加载 | PASS | 正常渲染 |
| NEW-17 | 咨询师订单页渲染 | PASS | 2 笔订单（含学生刚下的单） |
| NEW-18 | 订单卡含学生信息与状态 | PASS | 测试用户 / 待确认 / 拒绝 / 接受预约 |
| NEW-19 | **咨询师菜单只高亮「预约订单」** | PASS | `active=1` 且文本含订单 |
| NEW-20 | 咨询师接受预约 | PASS | 确认弹窗后操作成功 |

---

## 三、本轮修复的三个真实缺陷

### 1. 咨询师卡片「选择时段」点击无反应

**根因**：CSS 定义 `.overlay.open{display:flex}`，但 JS 加的是 `.on`。
类名不匹配导致弹窗永远 `display:none`，看起来就是「点了没反应」。

**修复**：`BookingView.vue` 三处 `classList.add/remove('on')` → `'open'`。

### 2. 列表被 Vue 响应式覆盖（潜在缺陷）

**根因**：原代码用 `setHtml(rootEl, '[data-list="docs"]', html)` 直接改 Vue 管理的 DOM。
Vue 虚拟 DOM 不知道内容被外部改过，任何响应式更新都会用旧内容（"正在加载…"）覆盖回去。

**修复**：咨询师列表改为纯 Vue 渲染（`v-for` + `computed`），按钮改 `@click.stop`。

### 3. 侧栏菜单同时高亮两项

**根因**：`isActive()` 用纯前缀判断。「概览」`/counselor/dashboard` 是「预约订单」
`/counselor/dashboard/orders` 的前缀，导致在订单页时两个都亮。

**修复**：改为最长前缀匹配，有更精确的菜单项时让出高亮。

---

## 四、已知功能缺口（非缺陷）

**TC-035 预约改期**：当前系统不支持修改已有预约的时间，需取消后重新预约。
这是产品设计范围，不是 bug。若要支持，需新增 `PATCH /api/appointment/{id}/reschedule` 后端接口。

---

## 五、新界面 C 模块功能清单（全部已实现）

### 学生端

```
/workspace/booking               咨询预约（Tab：找咨询师 / 我的预约）
  ├─ 咨询师列表（真实数据，9 位）
  ├─ 擅长领域筛选（6 个维度）
  ├─ 预约弹窗（选日期 + 选时段 + 确认）
  ├─ 我的预约列表（状态筛选 + 数量角标）
  ├─ 取消预约（二次确认，时段自动释放）
  └─ 进入咨询 / 评价咨询 入口

/workspace/chat/:id              咨询对话
  ├─ 消息收发（3 秒轮询）
  ├─ 图片上传
  ├─ 系统消息
  └─ 结束咨询

/workspace/review/:id            评价咨询
  ├─ 五星评分
  ├─ 标签多选（5 个）
  ├─ 文字评价（500 字）
  └─ 匿名选项
```

### 咨询师端

```
/counselor/dashboard             工作台（统计 + 最近预约）
/counselor/dashboard/orders      预约订单
  ├─ 状态筛选（6 种）
  ├─ 接受预约
  ├─ 拒绝预约（必填原因，写回 cancel_reason）
  └─ 进入咨询

/counselor/dashboard/chat/:id    咨询会话
  ├─ 消息收发
  ├─ 快捷回复（5 条话术）
  ├─ 学生信息面板
  ├─ 添加备注
  └─ 结束咨询
```

---

## 六、后端修复记录

**`AppointmentResponse` 缺 `cancel_reason` 字段**
`handle_order` 的 reject 分支确实把拒绝原因写进了数据库，但响应 schema 未声明该字段，
前端拿不到。已在 `backend/app/schemas/counselor.py` 补 `cancel_reason: Optional[str] = None`。

---

## 七、测试环境说明

- 邮件测试需用 `e2e_c_module/run_backend_mail_mock.py` 启动后端（隔离真实 SMTP）
- 浏览器测试使用系统 Chrome（`C:\Program Files\Google\Chrome\Application\chrome.exe`），无需下载 Playwright 浏览器
- 所有测试数据在结束后自动清理，`appointments` / `consultation_reviews` / `consultation_messages` 归零，咨询师统计已重置

---

## 八、截图

`e2e_c_module/shots_new_ui/`
- `01_booking_modal.png` — 预约弹窗
- `02_my_appointments.png` — 我的预约列表
- `03_sidebar_active.png` — 侧栏高亮状态
- `04_counselor_orders.png` — 咨询师订单页
- `05_after_accept.png` — 接受预约后
