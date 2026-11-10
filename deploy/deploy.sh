#!/usr/bin/env bash
# ============================================
# 心屿 Mindisle 一键部署脚本
# 在云服务器上执行：bash deploy/deploy.sh
# ============================================
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info() { echo -e "${GREEN}[OK]${NC} $*"; }
warn() { echo -e "${YELLOW}[!]${NC} $*"; }
fail() { echo -e "${RED}[x]${NC} $*"; exit 1; }

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "============================================"
echo "  心屿 Mindisle 部署"
echo "  项目目录: $ROOT"
echo "============================================"

# ---------- 1. 检查依赖 ----------
command -v docker >/dev/null 2>&1 || fail "未安装 Docker，请先安装：https://docs.docker.com/engine/install/"
docker compose version >/dev/null 2>&1 || fail "未安装 docker compose 插件"
info "Docker 环境正常"

# ---------- 2. 检查环境变量 ----------
if [ ! -f deploy/.env ]; then
  warn "未找到 deploy/.env，从模板复制"
  cp deploy/.env.example deploy/.env
  fail "请先编辑 deploy/.env 填写 DATABASE_URL 和 SECRET_KEY，然后重新运行"
fi

if grep -q "请替换为32位以上随机字符串" deploy/.env; then
  warn "SECRET_KEY 仍是模板默认值，自动生成一个"
  NEW_KEY=$(head -c 32 /dev/urandom | base64 | tr -d '/+=' | head -c 43)
  sed -i.bak "s|^SECRET_KEY=.*|SECRET_KEY=${NEW_KEY}|" deploy/.env && rm -f deploy/.env.bak
  info "已生成随机 SECRET_KEY"
fi

if grep -q "CHANGE_ME" deploy/.env; then
  fail "deploy/.env 中 DATABASE_URL 仍是 CHANGE_ME，请填写真实数据库连接"
fi
info "环境变量检查通过"

# ---------- 3. 构建镜像 ----------
info "开始构建镜像（首次约 3-5 分钟）..."
docker compose -f deploy/docker-compose.yml --env-file deploy/.env build

# ---------- 4. 启动 ----------
info "启动容器..."
docker compose -f deploy/docker-compose.yml --env-file deploy/.env up -d

# ---------- 5. 健康检查 ----------
info "等待服务就绪..."
for i in $(seq 1 40); do
  if curl -fsS http://127.0.0.1:8000/ >/dev/null 2>&1; then
    info "服务已就绪"
    break
  fi
  [ "$i" -eq 40 ] && fail "服务启动超时，查看日志：docker logs mindisle"
  sleep 2
done

# ---------- 6. 结果 ----------
IP=$(curl -s --max-time 5 ifconfig.me 2>/dev/null || echo "你的服务器IP")
echo ""
echo "============================================"
echo -e "${GREEN}  部署完成${NC}"
echo "============================================"
echo "  访问地址: http://${IP}:8000"
echo ""
echo "  测试账号:"
echo "    学生   user@test.com        / 123456"
echo "    咨询师 consultant@test.com  / 123456"
echo "    管理员 admin@soulstation.com / admin123"
echo ""
echo "  常用命令:"
echo "    查看日志  docker logs -f mindisle"
echo "    重启      docker compose -f deploy/docker-compose.yml restart"
echo "    停止      docker compose -f deploy/docker-compose.yml down"
echo "    更新代码  git pull && bash deploy/deploy.sh"
echo "============================================"
