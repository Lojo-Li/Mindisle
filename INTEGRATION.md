# E 线（AI 心理支持）集成说明

本分支 `feature/e-ai-support` 在 `e230651` 基础上追加了 3 个提交。
目标是补齐 E 的三条链路：**回答有依据可查证、风险有记录可处置、知识可运营**。

> 合并前请先处理一件与本功能无关但更要紧的事：
> `backend/.env` 目前被 git 跟踪并已推到公开仓库，请先 `git rm --cached backend/.env`、
> 加进 `.gitignore`、轮换其中所有密钥。否则后面所有工作都建立在一个已泄露的环境上。

---

## 一、提交结构

| # | 提交 | 内容 | 冲突面 |
|---|---|---|---|
| 1 | `feat(ai): 新增风险事件表、引用溯源表与对应服务` | 3 个新模型、`risk_service`、`api/ai_support` 路由、SQL 迁移、测试 | **零**（全是新文件） |
| 2 | `refactor(ai): 流式接口按事件下发风险与引用…` | 改 `chat/router.py`、`chat_service.py`、`crisis_service.py`、`rag_service.py`、`ai_service.py`、`config.py`、`main.py`、`models/__init__.py`、`requirements.txt` | 中（`chat/router.py` 最可能需要手工合） |
| 3 | `feat(ai): 新增风险提示组件、引用来源组件与后台风险工单页` | 4 个新组件、`RiskManage.vue`、`api/aiSupport.js`、`router/index.js`、`AdminLayout.vue` | 低（路由与菜单各 1-7 行） |
| — | **聊天页集成（暂缺）** | 原计划改 `ChatIndex.vue`，因该页面正在被改造为新结构，此部分暂缓 | 待定 |

**推荐合并顺序：1 → 3 里的新文件 → 2 → 3 里的改动文件 → 跑迁移。**
也就是先把"纯新增"全部落进去（谁都不会冲突），再处理对既有文件的修改。

---

## 二、合并方式

### 方式 A：分支已在远端（推荐）

> 前提：`feature/e-ai-support` 必须**先被 push 到远端**，否则 `git fetch` 会报
> `couldn't find remote ref`。下面的命令都在**仓库根目录**（有 `.git` 的那一层，不是 `backend/`）执行。

第一次推送（只需做一次）：

```bash
cd <仓库根目录>
git push -u origin feature/e-ai-support
```

之后在 GitHub 上开 PR，组员 review 后合并；或者命令行直接合：

```bash
git checkout main
git pull                          # 先拿别人的提交，避免推送被拒
git merge feature/e-ai-support
git push origin main
```

### 方式 B：按提交打补丁（推荐给其他组员，或不想动远端时）

适用场景：同事的仓库已经有别人的改动，或者不想为了合并而先 push 一个分支。
补丁不依赖远端，拷过去就能用。

```bash
cd <你的仓库根目录>
git am /path/to/patches/0001-*.patch    # 新文件，先合
git am /path/to/patches/0002-*.patch    # 后端改造
git am /path/to/patches/0003-*.patch    # 前端
git am /path/to/patches/0004-*.patch    # 集成说明
```

如果某个 patch 冲突：

```bash
git am --show-current-patch=diff   # 看冲突内容
# 手工解决后
git add <files> && git am --continue
# 或者放弃这一笔，手动改
git am --abort
```

`0002` 里最可能冲突的是 `backend/app/api/chat/router.py` 的 `send_message_stream`。
如果冲突太多，直接**用本分支的这一整个函数替换**即可，它与其他代码无耦合。

---

## 三、数据库迁移

```bash
mysql -u root -p soulstation < backend/sql/migrate_e_ai_support.sql
```

新增三张表，全部 `CREATE TABLE IF NOT EXISTS`，可重复执行：

- `risk_events` —— 风险事件（谁、哪次对话、几级、命中了什么、处置到哪一步）
- `ai_message_sources` —— 每条 AI 回答引用了哪些知识条目
- `ai_feedback` —— 回答有没有用

**注意**：不要在已用 `init.sql` 建库的环境上跑 `Base.metadata.create_all` 来建这三张表。
`init.sql` 的主键是 `BIGINT UNSIGNED`，SQLAlchemy 的 `BigInteger` 是有符号的，
混用会报 `Foreign key constraint is incorrectly formed`。所以模型里刻意没写 `ForeignKey`，
外键统一由 SQL 文件维护。

---

## 四、配置项

`backend/.env` 可选新增（不配也有默认值）：

```ini
AI_ASSISTANT_NAME=小屿
# 是否校验 AI 服务端证书，默认 true。仅本地证书链异常时临时关，线上禁止关
AI_VERIFY_SSL=true
# RAG 相关度阈值。归一化向量下 L2 距离 = 2-2cos，1.2 约等于 cos>=0.4
RAG_DISTANCE_THRESHOLD=1.2
# 热线（JSON 数组）。上线前请核对号码有效性，各地号码不同
CRISIS_HOTLINES_JSON=[{"name":"全国心理援助热线","number":"12356","description":"24 小时"}]
```

> **热线号码请自行核实后再用于演示。** 代码里给的是常见号码，但心理援助热线
> 会随地区与年份调整，硬编码在代码里是错的，所以做成了配置项。

---

## 五、接口契约变化

### 1. 流式接口（唯一一个破坏性变更，但对前端是兼容的）

`POST /api/chat/{dialogue_id}/message/stream` 的事件序列变了：

```
data: {"type":"risk","risk":{"level":2,"label":"L2 警示","keywords":["绝望"],
        "actions":["banner","hotline_card","appointment_cta","notify_counselor"],
        "hotlines":[{"name":"…","number":"…","description":"…"}]}}

data: {"type":"sources","sources":[{"vector_id":"psych_123","title":"…",
        "snippet":"…","score":0.83}]}

data: {"content":"我","done":false}
data: {"content":"能感受到","done":false}
...

data: {"content":"","done":true,"message_id":1024,"crisis_detected":true,
       "crisis_level":2,"crisis_keywords":["绝望"],"source_count":2}

data: {"type":"title_update","dialogue_title":"睡眠与焦虑"}
```

- `content` / `done` / `message_id` 的字段名和语义**没变**，老的解析逻辑不会崩。
- 新增 `risk` 与 `sources` 两个事件，用 `type` 区分。
  前端如果不处理它们，行为与改造前一致（只是看不到提示）。
- 为什么把 risk 拆出来：旧实现把危机字段塞在 `done` 里，
  前端收到 `done` 只做"结束"处理就 `continue` 了，风险提示等于没发出。

### 2. 新增接口

| 方法 | 路径 | 权限 | 说明 |
|---|---|---|---|
| GET | `/api/ai/sources/{message_id}` | 登录用户（仅本人消息） | 某条回答的引用详情 |
| POST | `/api/ai/feedback` | 登录用户 | 提交有用/没用 |
| GET | `/api/ai/risk/events` | 管理员 | 风险工单列表（可按 level / handled_status 筛） |
| PUT | `/api/ai/risk/events/{id}` | 管理员 | 处置：contacted / closed / pending |
| GET | `/api/ai/risk/stats` | 管理员 | 总量、待处理、分级分布、近 7 天 |

---

## 六、需要其他组员配合的点

这些不是"顺便提一下"，缺了会导致对应能力无法闭环：

| 依赖 | 具体需要 | 用来做什么 | 现在缺会怎样 |
|---|---|---|---|
| **A 用户权限** | JWT 里带 `role`；撤回授权后 token 立即失效；管理员查看会话内容写一条审计日志 | AI 会话仅本人可见；管理员看风险工单属于敏感操作 | "如何保护不同角色的数据"答不上来 |
| **B 咨询师** | `GET /api/counselor/recommend?tags=焦虑,睡眠&limit=3` | L2/L3 时在横幅里推荐匹配咨询师 | 分流只能停在"打电话"，进不了平台内 |
| **C 预约** | 深链 `/counselor/{id}?from=ai&risk=2`，预约记录加 `source` 字段 | 统计"AI 转介 → 预约"转化率 | 展示时没有"分流有效"的数字 |
| **D 量表** | `GET /api/test/history/latest` 返回最近一次各量表得分 | AI 回答可引用"你上周 SDS 62 分" | 回答千人一面，个性化无从体现 |

目前 `RiskNotice.vue` 的"预约咨询师"按钮只做了 `router.push('/counselor')`，
等 B/C 的接口就绪后换成带参数的深链即可，改动点只有 `goToCounselor()` 一个函数。

---

## 七、自测步骤

```bash
# 1. 后端
cd backend
pip install -r requirements.txt        # 需要 Python 3.10/3.11，见第八节
mysql -u root -p soulstation < sql/migrate_e_ai_support.sql
pytest tests/test_crisis_detection.py -v
uvicorn app.main:app --reload

# 2. 前端
cd frontend
npm install
npm run dev
```

### 验收清单

**引用可查证**
- [ ] 问一个知识库覆盖的问题 → 回答下方出现"参考 N 条知识"，展开能看到片段与相似度
- [ ] 问一个知识库没有的问题 → AI 明确说明"知识库无相关条目"，且不显示参考来源
- [ ] 刷新页面重新打开该会话 → 引用来源仍可通过点开展示（走后端按需拉取）
- [ ] `SELECT * FROM ai_message_sources WHERE message_id = <id>;` 有对应记录

**风险可处置**
- [ ] 输入"我对未来没有希望" → L1 轻提示，`risk_events` 无记录
- [ ] 输入"我真的很绝望，撑不住了" → 顶部黄条 + 热线卡 + 预约按钮，生成 level=2 记录
- [ ] 输入"我想自杀" → 阻塞弹层，未勾选时无法关闭；关闭后顶部红条常驻，生成 level=3 记录
- [ ] 输入"我没有想自杀，只是问问" → **不触发**（否定窗口生效）
- [ ] 输入"我快笑死了" → **不触发**（口语误报剥离）
- [ ] 后台 `/admin/risks` 能看到上述记录，可标记"已联系"并写备注
- [ ] 用户关闭"保存对话历史"后再触发 L3 → 消息不落库，但 `risk_events` 仍有记录

**回归**
- [ ] 普通对话照常流式输出，标题仍会自动生成
- [ ] 会话列表、标签、导出、语音输入未受影响

---

## 八、环境注意（会直接卡住演示）

1. **Python 版本**：`chromadb==0.4.22` + `sentence-transformers==2.6.1` 在 **Python 3.13 上装不上**，请用 3.10 / 3.11。
2. **embedding 模型缺失**：`backend/models/` 被 `.gitignore` 排除了，但 `chroma_db/` 里的向量是本地模型建的。
   新克隆后第一次检索会去 HuggingFace 下载 `paraphrase-multilingual-MiniLM-L12-v2`（约 470MB）。
   **离线演示会直接失败**，请提前把模型文件随包分发，或在演示环境预热一次。
3. **`.env` 泄露**：见开头。这是当前最高优先级。
4. RAG 阈值从 3.0 改到 1.2 后，命中数量会变少。这是**预期行为**——
   原来的 3.0 等于不过滤，低相关案例被硬塞进 prompt，正是"答得泛"的根因。
   如果发现命中太少，可在 `.env` 里逐档调到 1.4 / 1.6 观察效果。

---

## 九、已知限制 / 建议下一步

| 项 | 说明 |
|---|---|
| 知识库运营后台未做 | 目前 RAG 语料仍靠 `seeds/load_psychology_rag.py` 离线灌入。要做"上传文档 → 切片 → 入库 → 重建索引"，需要新建 `kb_documents` / `kb_chunks` 两张表和上传接口，工程量约等于本轮的一半 |
| 无自助工具模块 | 情绪支持目前只有对话。呼吸练习、情绪日记、CBT 三栏表还缺数据模型与页面 |
| 风险判定仍是关键词 | 已加否定窗口与误报剥离，但正式产品应叠加模型判定做二次确认，并统计误报率 |
| 后台知识列表的旧 bug 未修 | `knowledge_service.py:31` 硬编码 `status == 'published'`，导致后台看不到草稿文章（注释却写着"包含所有状态"）。属于知识库运营范畴，建议与上一行一起做 |
| `api/chat.js` 里的 `sendMessageStream` | 该函数收到 `done` 就 `return`，会吞掉后续 `title_update`。目前 `ChatIndex.vue` 用的是自己内联的解析逻辑，所以没暴露，但这是个隐藏的坑，建议删除该函数或修正 |

---

## 十、改动文件清单

**新增（12 个）**

```
backend/app/models/risk.py
backend/app/schemas/risk.py
backend/app/services/risk_service.py
backend/app/api/ai_support/__init__.py
backend/sql/migrate_e_ai_support.sql
backend/tests/test_crisis_detection.py
frontend/src/api/aiSupport.js
frontend/src/components/ai/RiskNotice.vue
frontend/src/components/ai/RiskDialog.vue
frontend/src/components/ai/SourceList.vue
frontend/src/components/ai/AnswerFeedback.vue
frontend/src/views/admin/RiskManage.vue
```

**修改（9 个）**

```
backend/app/api/chat/router.py       流式事件序列
backend/app/services/chat_service.py 非流式路径同步用新判定
backend/app/services/crisis_service.py 分级、否定窗口、动作矩阵
backend/app/services/rag_service.py  结构化引用 + 阈值
backend/app/services/ai_service.py   品牌与边界、TLS 校验
backend/app/core/config.py           新增配置项
backend/app/main.py                  注册路由（+2 行）
backend/app/models/__init__.py       注册新模型（+2 行）
backend/requirements.txt             删除 langchain
frontend/src/router/index.js         （+7 行）
frontend/src/layouts/AdminLayout.vue （+5 行）
```

**暂缺：聊天页集成**

原计划在 `frontend/src/views/chat/ChatIndex.vue` 中消费 `risk` / `sources` 事件，
但该页面正在被改造为新结构，改动待其定稿后单独提交。

在集成完成之前，风险与引用功能的表现是：

- 后端照常判定、落库、下发事件 —— 数据齐全，后台工单页可用
- 前端**看不到**风险横幅与引用来源（`ChatIndex.vue` 不认识这两个新事件，会忽略）
- 一旦新页面定稿，只需在它的 SSE 处理里加两个分支：
  - `type === 'risk'` → L2/L3 展示提示，L3 弹阻塞层
  - `type === 'sources'` → 在回答下方渲染参考来源

参考实现见 `patches/待重做-ChatIndex集成.patch`（旧版 Vue 页面的集成写法，
结构可借鉴，模板部分大概率要按新页面重写）。
