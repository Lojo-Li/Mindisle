#!/usr/bin/env bash
# ============================================================
# SoulStation 本地一键启动脚本（Windows Git Bash）
# 用途：在没有 MySQL / Docker 的情况下，用 SQLite 快速跑起来看 UI
# 用法：bash dev-start.sh
# ============================================================
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"
PY="$BACKEND/.venv/Scripts/python.exe"

export DATABASE_URL="sqlite:///./soulstation_dev.db"
export APP_DEBUG="False"
export REDIS_ENABLED="False"

echo "==> [1/4] 检查 Python 虚拟环境"
if [ ! -f "$PY" ]; then
  echo "   未找到虚拟环境，正在使用 Python 3.12 创建..."
  py -3.12 -m venv "$BACKEND/.venv"
  "$PY" -m pip install -q --upgrade pip
  echo "   安装后端依赖（首次较慢）..."
  "$PY" -m pip install -q -r "$BACKEND/requirements.txt" || {
    echo "   完整依赖安装失败，改为安装核心依赖（跳过 chromadb / sentence-transformers）"
    "$PY" -m pip install -q \
      fastapi==0.109.0 "uvicorn[standard]==0.27.0" python-multipart==0.0.6 \
      sqlalchemy==2.0.25 pymysql==1.1.0 alembic==1.13.1 redis==5.0.1 \
      "python-jose[cryptography]==3.3.0" passlib==1.7.4 bcrypt==4.0.1 \
      python-dotenv==1.0.0 "pydantic[email]==2.5.3" pydantic-settings==2.1.0 \
      fastapi-mail==1.4.1 openai==1.10.0 python-docx==1.1.0 aiofiles==23.2.1
  }
fi

echo "==> [2/4] 初始化数据库"
cd "$BACKEND"
if [ ! -f soulstation_dev.db ]; then
  "$PY" -c "from app.core.database import Base, engine; import app.models; Base.metadata.create_all(bind=engine)"
  "$PY" seeds/init_users.py
  "$PY" seeds/init_test_data.py
  "$PY" seeds/init_extended_tests.py
  "$PY" seeds/add_more_accounts.py
  "$PY" seeds/_demo_articles.py
  "$PY" seeds/_fix_admin_table.py
  echo "   数据库初始化完成"
else
  echo "   已存在 soulstation_dev.db，跳过初始化（如需重建请删除该文件）"
fi

echo "==> [3/4] 启动后端 http://127.0.0.1:8000"
"$PY" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

echo "==> [4/4] 启动前端 http://localhost:5173"
cd "$FRONTEND"
[ -d node_modules ] || npm install
npm run dev &
FRONTEND_PID=$!

trap 'echo "正在停止服务..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null' EXIT INT TERM

echo ""
echo "============================================================"
echo " 前端:      http://localhost:5173"
echo " API 文档:  http://127.0.0.1:8000/docs"
echo " 后台管理:  http://localhost:5173/admin/dashboard"
echo ""
echo " 管理员:    admin@test.com / 123456"
echo " 普通用户:  user1@test.com / 123456"
echo " 咨询师:    counselor1@test.com / 123456"
echo ""
echo " 按 Ctrl+C 停止全部服务"
echo "============================================================"
wait
