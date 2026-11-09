# 本地运行手册（E 线 / 屿灯）

目标：在一台干净机器上把**后端 + 前端 + 向量库**跑起来，并验证 E 的能力。
不需要 MySQL，不需要 Docker，不需要联网（模型和依赖装好之后）。

---

## 0. 前置：两个已知坑

**坑一：Python 版本。**
`chromadb==0.4.22` + `sentence-transformers==2.6.1` 在 **Python 3.13 上装不上**（NumPy 2 / torch 兼容问题）。
必须用 **3.10 或 3.11**。下面用 `uv` 装一个独立 3.11，不影响系统里的 3.13。

**坑二：向量库不能放在中文路径下。**
Windows 上 hnswlib 打不开非 ASCII 路径的索引文件，表现为服务重启后报
`Cannot open header file`，而同一个进程里写入后立刻查询却是好的——非常容易误判成数据损坏。
本仓库路径含「腾讯实训营」，所以向量库**必须放到纯英文路径**，例如 `C:/mindisle_chroma`。

---

## 1. 一次性准备

```bash
# 1.1 装 uv 与 Python 3.11（无需管理员权限）
cd backend
python -m pip install uv
python -m uv python install 3.11
python -m uv venv --python 3.11 .venv

# 1.2 装依赖（torch 用 CPU 版，省约 1.5GB）
python -m uv pip install --python .venv/Scripts/python.exe "torch==2.2.2" \
  --index-url https://download.pytorch.org/whl/cpu
python -m uv pip install --python .venv/Scripts/python.exe -r requirements.txt

# 1.3 必须降级 NumPy：chromadb 0.4.22 不兼容 NumPy 2.x
python -m uv pip install --python .venv/Scripts/python.exe "numpy==1.26.4"
```

### 1.4 嵌入模型

`backend/models/` 不在版本库里，需要单独下载（约 470MB）。国内直连 HuggingFace 会超时，用镜像：

```bash
export HF_ENDPOINT=https://hf-mirror.com
.venv/Scripts/python.exe -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
    local_dir='models',
    allow_patterns=['*.json','*.txt','*.bin','*.safetensors','1_Pooling/*','2_Dense/*','*.model','modules.json'],
)
"
```

### 1.5 向量库

仓库里的 `backend/chroma_db/` 是别的机器生成的，换环境后无法跨进程打开，**不要复用**。用脚本重建：

```bash
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
.venv/Scripts/python.exe scripts/rebuild_vector_db.py --out C:/mindisle_chroma
```

脚本会把 9846 条语料写入 `C:/mindisle_chroma`，使用 **cosine** 度量（相似度 = 1 - 距离，阈值含义直观）。
自检输出里相似度应在 0.85 以上。

---

## 2. 每次启动

### 2.1 后端

```bash
cd backend
export DATABASE_URL="sqlite:///./soulstation.db"   # 用 SQLite，免装 MySQL
export REDIS_ENABLED="False"                        # 本地没有 Redis
export CHROMA_DB_PATH="C:/mindisle_chroma"          # 必须是纯英文路径
export HF_HUB_OFFLINE="1" TRANSFORMERS_OFFLINE="1"  # 用本地模型，不联网

# 首次运行需要建表 + 灌测试账号
.venv/Scripts/python.exe -c "
from app.main import app
from app.core.init_db import init_db
init_db()
"
.venv/Scripts/python.exe seeds/init_users.py

# 启动
.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

> 注意：上面的环境变量是**覆盖**，没有改动 `backend/.env`。
> `.env` 里的 `DATABASE_URL` 指向 3307 端口，和本机 MySQL（3306）不一致，直接用会连不上。

### 2.2 前端

```bash
cd frontend
npm install      # 首次
npx vite --host 127.0.0.1 --port 5173
```

访问 http://127.0.0.1:5173 ，用测试账号登录：

| 角色 | 账号 | 密码 |
|---|---|---|
| 用户 | user1@test.com | 123456 |
| 咨询师 | counselor1@test.com | 123456 |
| 管理员 | admin@test.com | 123456 |

屿灯页地址：`http://127.0.0.1:5173/workspace/lamp`

---

## 3. 验收清单（E 线）

| # | 操作 | 预期 |
|---|---|---|
| 1 | 发「我最近很焦虑，晚上睡不好」 | 有流式回复；气泡下方出现「参考 N 条知识」，展开能看到条目与相似度 |
| 2 | 查库 | `ai_message_sources` 有对应记录，`score` 在 0.8 以上 |
| 3 | 发「我不想活了」 | 顶部出现 L3 红条 + **阻塞弹层**；未勾选时按钮禁用；热线可拨号 |
| 4 | 查库 | `risk_events` 新增一条 `level=3`、`handled_status=pending` |
| 5 | 发「我没有想自杀，只是随便问问」 | **不触发**任何风险提示（否定语境生效） |
| 6 | 后台风险工单页 | 能看到第 4 步那条，可标记「已联系」并写备注 |

查库示例：

```bash
cd backend
.venv/Scripts/python.exe -c "
from app.core.database import SessionLocal
from app.models.risk import RiskEvent, AiMessageSource
db=SessionLocal()
print('风险事件:', [(r.id,r.level,r.keywords) for r in db.query(RiskEvent).all()])
print('引用条数:', db.query(AiMessageSource).count())
"
```

---

## 4. 已知问题

### 4.1 模型端点失效（阻塞真实回复）

当前 `.env` 里没有 `DOUBAO_MODEL`，走代码默认值 `doubao-1-5-pro-32k-250115`，方舟返回：

```
400 InvalidEndpoint.ClosedEndpoint
```

说明 **Key 有效**（无效会返回 401），但**接入点已关闭**。去火山方舟控制台「在线推理」确认接入点，
把 `.env` 里的 `DOUBAO_MODEL` 改成 `ep-xxxx` 形式的接入点 ID 即可，代码不用动。

在修好之前：对话会显示「抱歉，我遇到了一些问题…」，但**风险提示、引用来源、落库都正常工作**。

### 4.2 向量库不要并发打开

`chromadb 0.4.22` 的持久化索引在 Windows 上多进程并发访问会损坏（表现为 `Cannot open header file`，
`header.bin` 被截断）。**只让后端服务进程打开它**，不要同时用脚本去读同一个目录。

### 4.3 仓库里的 chroma_db 不建议提交

重建后的向量库体积大且与平台相关，已加入 `.gitignore`。语料 JSON 在 `database/` 里，重建脚本可复现。

---

## 5. 相关改动说明

| 文件 | 改动 |
|---|---|
| `frontend/src/views/mindisle/views/LampView.vue` | 重写：SSE 流式、风险三级、引用折叠、答案反馈、上下文预填 |
| `frontend/src/api/aiSupport.js` | 新增 `streamChat()`，按事件回调 risk/sources/content/done/title |
| `frontend/src/styles/ai-support.css` | 屿灯补充样式，复用 `.mi-portal` 主题变量 |
| `backend/app/services/rag_service.py` | 嵌入模型路径归一化；支持 cosine 度量；按相似度过滤 |
| `backend/app/core/config.py` | 新增 `RAG_METRIC` / `RAG_MIN_SIMILARITY` |
| `backend/scripts/rebuild_vector_db.py` | 新增：可复现的向量库重建脚本（含中文路径检查） |
