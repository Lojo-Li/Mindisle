# 心屿 Mindisle 云服务器部署指南

从零到公网可访问，约 15 分钟。

---

## 一、准备云服务器

### 1.1 服务器要求

| 项目 | 最低 | 推荐 |
|---|---|---|
| CPU | 2 核 | 2 核 |
| 内存 | 2 GB | 4 GB |
| 硬盘 | 20 GB | 40 GB |
| 系统 | Ubuntu 22.04 / CentOS 7+ | Ubuntu 22.04 |

> 内存低于 2GB 时，构建镜像可能因 OOM 失败。可以在本地构建好推送到镜像仓库，或在服务器加 swap。

### 1.2 开放端口

在云厂商控制台的**安全组**里放行：

- `22`  SSH 登录
- `8000` 应用端口（或者用 80，见第四节）

### 1.3 安装 Docker

```bash
# 一键安装（Ubuntu / Debian）
curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun
systemctl enable --now docker

# 验证
docker --version
docker compose version
```

> 国内服务器建议配置镜像加速，否则拉基础镜像会很慢：
> ```bash
> mkdir -p /etc/docker
> cat > /etc/docker/daemon.json <<'EOF'
> {
>   "registry-mirrors": [
>     "https://docker.m.daocloud.io",
>     "https://dockerproxy.com"
>   ]
> }
> EOF
> systemctl restart docker
> ```

---

## 二、上传项目

### 方式 A：从 Git 拉取（推荐）

```bash
cd /opt
git clone https://github.com/Lojo-Li/Mindisle.git
cd Mindisle
```

### 方式 B：本地打包上传

在本地项目根目录执行：

```bash
# 打包（排除依赖和大文件）
tar --exclude='frontend/node_modules' \
    --exclude='backend/.venv' \
    --exclude='backend/__pycache__' \
    --exclude='.git' \
    --exclude='e2e_c_module' \
    -czf mindisle.tar.gz .

# 上传到服务器
scp mindisle.tar.gz root@你的服务器IP:/opt/
```

服务器上解压：

```bash
cd /opt && mkdir -p Mindisle && tar -xzf mindisle.tar.gz -C Mindisle && cd Mindisle
```

---

## 三、配置并部署

### 3.1 准备数据库

任选一种：

**选项 1：用云厂商托管 MySQL（推荐，省心）**

在腾讯云/阿里云控制台购买 MySQL 实例，创建数据库 `soulstation`，记下连接信息。

**选项 2：服务器本地装 MySQL**

```bash
apt update && apt install -y mysql-server
systemctl enable --now mysql

# 建库建用户
mysql -u root <<'EOF'
CREATE DATABASE IF NOT EXISTS soulstation DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'mindisle'@'%' IDENTIFIED BY '换成强密码';
GRANT ALL PRIVILEGES ON soulstation.* TO 'mindisle'@'%';
FLUSH PRIVILEGES;
EOF
```

### 3.2 导入数据（表结构 + 测试数据）

```bash
mysql -h 127.0.0.1 -u root -p < deploy/init-db.sql
```

导入成功后应包含：20 个用户、9 位咨询师、9 套量表、159 道题、1 个管理员。

### 3.3 配置环境变量

```bash
cp deploy/.env.example deploy/.env
nano deploy/.env
```

必须修改的两项：

```ini
SECRET_KEY=随便敲一串32位以上的字符
DATABASE_URL=mysql+pymysql://mindisle:你的密码@127.0.0.1:3306/soulstation
```

> 数据库在**同一个 docker compose 网络**里时用服务名，独立 MySQL 用 `127.0.0.1` 或内网 IP。
>
> 如果 MySQL 装在宿主机（非容器），需要把 `127.0.0.1` 改成 `172.17.0.1`（Docker 默认网桥网关），
> 或者把 MySQL 容器化后加入同一网络。

### 3.4 一键部署

```bash
bash deploy/deploy.sh
```

脚本会依次完成：检查依赖 → 校验配置 → 构建镜像 → 启动容器 → 健康检查 → 输出访问地址。

看到这个就成功了：

```
============================================
  部署完成
============================================
  访问地址: http://1.2.3.4:8000
```

---

## 四、配置域名和 HTTPS（可选但推荐）

直接用 `http://IP:8000` 可以访问，但链接不好看、也不安全。用 Nginx 反代到 80/443：

```bash
apt install -y nginx
```

```nginx
# /etc/nginx/sites-available/mindisle
server {
    listen 80;
    server_name your-domain.com;      # 换成你的域名，没有域名就填服务器 IP

    client_max_body_size 20M;         # 允许上传 20MB 文件

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # AI 流式输出必须关掉缓冲，否则对话会卡住
        proxy_buffering off;
        proxy_read_timeout 300s;
    }
}
```

```bash
ln -s /etc/nginx/sites-available/mindisle /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
```

**配 HTTPS（有域名时）：**

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d your-domain.com
```

Certbot 会自动改好 Nginx 配置并设置证书自动续期。

---

## 五、日常运维

```bash
# 查看日志
docker logs -f mindisle

# 查看状态
docker ps
docker stats mindisle

# 重启
docker compose -f deploy/docker-compose.yml restart

# 停止
docker compose -f deploy/docker-compose.yml down

# 更新代码后重新部署
git pull
bash deploy/deploy.sh

# 进入容器排查
docker exec -it mindisle bash
```

---

## 六、测试账号

| 角色 | 账号 | 密码 |
|---|---|---|
| 学生 | `user@test.com` | `123456` |
| 咨询师 | `consultant@test.com` | `123456` |
| 管理员 | `admin@soulstation.com` | `admin123` |

其他学生账号：`student1@test.com` ~ `student2@test.com`、`worker1@test.com`、`parent1@test.com` 等，密码均为 `123456`。

其他咨询师：`counselor5@test.com` ~ `counselor12@test.com`，密码均为 `123456`。

---

## 七、常见问题

### 页面能打开，但接口全 404

后端没起来或前端与后端不同源。检查：

```bash
docker logs mindisle | tail -30
curl http://127.0.0.1:8000/api/counselor/list
```

### 数据库连接失败

```bash
# 容器内测试连通性
docker exec -it mindisle bash
python -c "import pymysql; pymysql.connect(host='你的主机',user='mindisle',password='密码',database='soulstation'); print('OK')"
```

如果宿主机是 `127.0.0.1`，容器内访问不到宿主机服务，需改用 `172.17.0.1` 或宿主机内网 IP。

### AI 对话（屿灯）不工作

`deploy/.env` 里没配模型密钥。这是可选功能，不配不影响其他模块。填好 `OPENAI_API_KEY` 或豆包密钥后重启即可。

### 预约时提示「咨询师未开放该时段」

排班系统要求咨询师先发布可预约时段。用咨询师账号登录 → 「时段管理」→ 发布时段，学生才能预约。

### 上传的图片重启后丢失

`docker-compose.yml` 已经把 `/app/uploads` 挂到命名卷 `mindisle_uploads`，重启不会丢。如果要迁到别处：

```bash
docker run --rm -v mindisle_mindisle_uploads:/data -v $(pwd):/backup alpine tar czf /backup/uploads.tar.gz -C /data .
```

### 构建时内存不足被 kill

加 swap：

```bash
fallocate -l 2G /swapfile && chmod 600 /swapfile
mkswap /swapfile && swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

---

## 八、安全建议

上线给外部使用前，务必：

1. **改掉所有默认密码**（尤其是管理员 `admin123`）
2. **`SECRET_KEY` 用真随机值**，不要用模板默认
3. **数据库不给公网访问**，只允许服务器内网连
4. **`APP_DEBUG=False`**（模板已默认）
5. 定期备份数据库：

```bash
# 每天凌晨 3 点备份，保留 7 天
cat > /etc/cron.d/mindisle-backup <<'EOF'
0 3 * * * root mysqldump -u mindisle -p'密码' soulstation | gzip > /backup/soulstation-$(date +\%F).sql.gz && find /backup -name "*.sql.gz" -mtime +7 -delete
EOF
```
