#!/bin/bash

echo "===================================="
echo "SoulStation Backend Server"
echo "===================================="
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python环境，请先安装Python"
    exit 1
fi

# 检查是否安装了依赖
if [ ! -d "venv" ]; then
    echo "[信息] 创建虚拟环境..."
    python3 -m venv venv
fi

echo "[信息] 激活虚拟环境..."
source venv/bin/activate

echo "[信息] 安装依赖..."
pip install -r requirements.txt -q

echo ""
echo "[信息] 启动后端服务..."
echo ""
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
