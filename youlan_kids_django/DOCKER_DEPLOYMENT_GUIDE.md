# 悠蓝童装 Django 项目 Docker 部署与远程开发指南

本指南将帮助您使用 Docker 将 youlan_kids_django 项目打包并部署到服务器上，并配置远程开发环境。

## 环境要求

- Docker Desktop (Windows/Mac) 或 Docker Engine (Linux)
- Docker Compose
- Git
- 支持 Docker 的远程服务器

### Windows 环境特别说明

在 Windows 上使用 Docker 需要注意以下几点：

1. 确保 Docker Desktop 已正确安装
2. 启动 Docker Desktop 应用程序（而不仅仅是启动服务）
3. 验证 Docker 是否正常运行：
   ```bash
   docker run hello-world
   ```
4. 如果遇到连接问题，请检查：
   - Docker Desktop 应用是否正在运行
   - Windows Subsystem for Linux (WSL) 是否正确配置
   - 用户是否有足够的权限访问 Docker

如果看到类似 `error during connect: Head "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/_ping"` 的错误，通常表示 Docker Desktop 应用未启动。

## 项目结构

```
youlan_kids_django/
├── Dockerfile             # Docker 镜像构建配置
├── docker-compose.yml     # 多容器应用配置
├── .env                   # 环境变量配置
├── .dockerignore          # Docker 构建排除文件
├── requirements.txt       # Python 依赖
├── manage.py              # Django 管理脚本
└── youlan_kids_django/    # Django 项目配置目录
```

## 本地开发与测试

### 1. 构建并启动容器

```bash
cd youlan_kids_django
# 首次构建或修改了Dockerfile后执行
docker-compose build
# 启动服务
docker-compose up
```

项目将在 `http://localhost:8000` 上运行。

### 2. 执行数据库迁移

在另一个终端中执行：

```bash
docker-compose exec web python manage.py migrate
```

### 3. 创建超级用户

```bash
docker-compose exec web python manage.py createsuperuser
```

## 部署到服务器

### 1. 将项目代码推送到远程仓库

```bash
git add .
git commit -m "Add Docker deployment configuration"
git push origin main
```

### 2. 在服务器上拉取代码

```bash
ssh user@server_ip
git clone https://github.com/MAGI0804/youlan_django.git
cd youlan_kids_django
```

### 3. 修改生产环境配置

编辑 `.env` 文件，调整生产环境的配置：

```env
DEBUG=False
ALLOWED_HOSTS=your_domain.com,server_ip
DB_HOST=db  # 保持不变，使用Docker内部网络
```

### 4. 构建并启动生产容器

```bash
# 生产环境使用 -d 后台运行
# 设置生产环境变量
DEBUG=False docker-compose up -d --build
```

### 5. 执行生产环境数据库迁移

```bash
docker-compose exec web python manage.py migrate
```

## 远程开发配置

### VS Code Remote Development

1. 安装 VS Code 扩展：
   - Remote - Containers
   - Python
   - Django

2. 连接到远程服务器上的容器：
   - 使用 Remote - SSH 扩展连接到服务器
   - 右键点击 `docker-compose.yml` 文件，选择 "Remote-Containers: Open Folder in Container..."

3. 配置调试器：
   在 `.vscode/launch.json` 中添加：
   ```json
   {
       "version": "0.2.0",
       "configurations": [
           {
               "name": "Python: Django",
               "type": "python",
               "request": "launch",
               "program": "${workspaceFolder}/manage.py",
               "args": [
                   "runserver",
                   "0.0.0.0:8000"
               ],
               "django": true
           }
       ]
   }
   ```

### PyCharm Remote Development

1. 在 PyCharm 中配置远程解释器：
   - 打开 Settings > Project > Python Interpreter
   - 点击齿轮图标 > Add
   - 选择 "On Docker Compose"
   - 选择 `docker-compose.yml` 文件和 `web` 服务

2. 配置运行/调试配置：
   - 创建新的 Django Server 配置
   - 设置主机为 0.0.0.0，端口为 8000

## 常用 Docker 命令

```bash
# 查看运行中的容器
docker-compose ps

# 查看容器日志
docker-compose logs web

# 进入容器终端
docker-compose exec web bash

# 停止所有容器
docker-compose down

# 查看容器资源使用情况
docker stats
```

## 数据持久化

- 数据库数据存储在 `mysql_data` 卷中，即使容器重启或重建，数据也会保留
- 项目代码通过绑定挂载（bind mount）与容器同步，本地修改会立即反映到容器中

## 注意事项

1. 生产环境中务必设置 `DEBUG=False` 和安全的 `SECRET_KEY`
2. 定期备份数据库和重要数据
3. 考虑在生产环境中使用 Nginx 作为反向代理
4. 如需使用 HTTPS，请配置 TLS/SSL 证书
5. 生产环境建议使用 Gunicorn 或 uWSGI 代替 Django 开发服务器

## 高级配置（生产环境）

### 使用 Gunicorn 代替开发服务器

修改 `Dockerfile` 的最后一行：

```dockerfile
# 替换为
CMD ["gunicorn", "youlan_kids_django.wsgi:application", "--bind", "0.0.0.0:8000"]
```

并在 `requirements.txt` 中添加 `gunicorn`。

### 使用 Nginx 作为反向代理

在 `docker-compose.yml` 中添加 Nginx 服务：

```yaml
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - static_volume:/app/static
      - media_volume:/app/media
    depends_on:
      - web
```

## 故障排除

### Docker 引擎连接问题

如果遇到类似 `error during connect: Head "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/_ping"` 的错误：

1. **确保 Docker Desktop 应用正在运行**：
   - 在 Windows 上，需要手动打开 Docker Desktop 应用程序
   - 等待 Docker 引擎完全启动（系统托盘图标变为绿色）

2. **检查 Docker 服务状态**：
   ```powershell
   # 查看 Docker 相关服务
   Get-Service *Docker*
   
   # 尝试以管理员身份启动服务
   Start-Service com.docker.service -Verbose
   ```

3. **验证 Docker 安装**：
   ```bash
   docker --version
   docker info
   ```

4. **WSL 2 配置问题**：
   - 确保 WSL 2 已正确安装和配置
   - 检查 `wsl -l -v` 显示的状态
   - 尝试重新安装或更新 WSL 2

### Docker Hub 连接超时问题

如果遇到类似 `failed to fetch oauth token: Post "https://auth.docker.io/token": dial tcp 199.59.149.239:443: connectex` 的错误：

1. **检查网络连接和防火墙设置**：
   - 确保您的网络可以访问 Docker Hub（https://auth.docker.io 和 https://registry-1.docker.io）
   - 检查防火墙或安全软件是否阻止了 Docker 的网络连接

2. **配置 Docker 代理**：
   在 Docker Desktop 中配置代理设置：
   - 打开 Docker Desktop 设置
   - 导航到 "Resources" > "Proxies"
   - 启用 "Manual proxy configuration"
   - 输入您的 HTTP 和 HTTPS 代理地址

3. **使用国内 Docker 镜像源**：
   配置 Docker 镜像加速器以提高下载速度：
   - 在 Docker Desktop 设置中，导航到 "Docker Engine"
   - 添加以下配置：
   ```json
   {
     "registry-mirrors": [
       "https://registry.docker-cn.com",
       "https://docker.mirrors.ustc.edu.cn",
       "https://hub-mirror.c.163.com"
     ]
   }
   ```
   - 点击 "Apply & Restart" 保存更改并重启 Docker

4. **手动下载基础镜像**：
   如果镜像拉取持续失败，可以尝试先手动拉取基础镜像：
   ```bash
   docker pull python:3.10-slim-buster
   ```

5. **暂时禁用 IPv6**：
   在某些网络环境中，禁用 IPv6 可能有助于解决连接问题：
   - 打开网络适配器设置
   - 禁用 IPv6 协议
   - 重启 Docker 服务

### 其他常见问题

- **数据库连接失败**：检查 `DB_HOST` 是否设置为 `db`（Docker 网络中）
- **静态文件无法访问**：执行 `python manage.py collectstatic` 命令
- **权限问题**：检查文件和目录的权限设置
- **端口冲突**：修改 `docker-compose.yml` 中的端口映射
- **构建镜像失败**：检查 `Dockerfile` 中的依赖是否正确，网络连接是否正常

如有其他问题，请查看容器日志获取详细错误信息：
```bash
docker-compose logs web
docker-compose logs db
```

### 替代方案：使用本地 Python 环境（不使用 Docker）

如果在配置 Docker 时遇到无法解决的问题，可以暂时使用本地 Python 环境进行开发：

1. **安装 Python 3.10 或更高版本**

2. **创建虚拟环境**：
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```

3. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

4. **运行开发服务器**：
   ```bash
   python manage.py runserver
   ```

5. **使用外部数据库**：
   修改 `settings.py` 中的数据库配置，使用本地或远程 MySQL 数据库

## 部署到远程服务器的替代方案

如果 Docker 配置遇到困难，也可以考虑以下部署方式：

### 1. 使用 Gunicorn + Nginx（传统部署）

1. 在服务器上安装 Python、Gunicorn、Nginx
2. 配置 Nginx 作为反向代理
3. 使用 systemd 管理 Gunicorn 进程
4. 配置静态文件和媒体文件服务

### 2. 使用 PaaS 平台

考虑使用以下平台进行更简单的部署：
- Heroku
- Vercel
- Railway
- DigitalOcean App Platform

这些平台通常提供一键部署 Django 应用的功能，无需手动配置 Docker。