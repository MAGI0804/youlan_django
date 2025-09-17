# 项目部署指南

## 1. 本地环境准备

确保您的开发环境已安装以下软件：
- Git
- Docker 和 Docker Compose
- Python 3.10 或更高版本

## 2. 清理冗余文件（已完成）

已删除以下冗余文件，保持项目结构整洁：
- 多个Dockerfile变体（Dockerfile-aliyun、Dockerfile-offline等）
- 多个docker-compose.yml变体
- 多个运行脚本（run_docker_*.bat/sh）

## 3. 创建标准化配置文件（已完成）

已更新以下核心配置文件：
- **Dockerfile**：使用Python 3.10镜像，配置国内PyPI源
- **.dockerignore**：按照业内标准忽略不需要的文件
- **docker-compose.yml**：标准的Docker Compose配置

## 4. 将项目上传到GitHub

### 4.1 初始化Git仓库

如果项目尚未初始化Git仓库，请执行以下命令：

```bash
# 在项目根目录执行
git init
# 添加所有文件
git add .
# 提交更改
git commit -m "初始提交 - 清理后的项目结构"
```

### 4.2 连接到GitHub并推送代码

```bash
# 添加GitHub远程仓库（将YOUR_USERNAME和YOUR_REPOSITORY替换为实际值）
git remote add origin https://github.com/MAGI0804/youlan_django.git
# 推送到GitHub主分支
git push -u origin main
```

## 5. 服务器部署

### 5.1 从GitHub拉取项目代码

在服务器上执行以下命令：

```bash
# 克隆GitHub仓库（将YOUR_USERNAME和YOUR_REPOSITORY替换为实际值）
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
sudo chown -R $USER:$USER YOUR_REPOSITORY
sudo chmod -R 755 YOUR_REPOSITORY
cd YOUR_REPOSITORY/youlan_kids_django
```

### 5.2 配置环境变量

确保服务器上有正确的.env文件（如果没有，创建一个）：

```bash
# 创建或编辑.env文件
nano .env
```

添加必要的环境变量：

```
SECRET_KEY=your_secret_key_here
DEBUG=True
# 根据需要添加其他环境变量
```

### 5.3 使用Docker运行项目

```bash
# 确保Docker服务正在运行
sudo systemctl start docker
# 使用Docker Compose构建和运行项目
docker-compose up -d --build
```

### 5.4 验证部署

检查容器是否正在运行：

```bash
docker ps
```

查看应用日志：

```bash
docker-compose logs -f
```

## 6. 常见问题排查

### 6.1 Docker镜像拉取失败

如果遇到镜像拉取超时或失败问题：

```bash
# 清理Docker缓存
docker system prune -a
# 重新构建
DOCKER_BUILDKIT=1 docker-compose up -d --build
```

### 6.2 网络连接问题

如果Docker无法连接到外部网络，请检查Docker守护进程配置：

```bash
# 编辑Docker配置文件
sudo nano /etc/docker/daemon.json
```

确保配置简洁，避免强制使用不可用的镜像加速器：

```json
{}
```

然后重启Docker服务：

```bash
sudo systemctl restart docker
```

## 7. 定期更新

当有新的代码更改时，在服务器上更新项目：

```bash
cd YOUR_REPOSITORY/youlan_kids_django
# 拉取最新代码
git pull origin main
# 重新构建和运行
docker-compose down
docker-compose up -d --build
```

## 8. 生产环境部署建议

对于生产环境，建议进行以下优化：
- 设置`DEBUG=False`
- 使用更强的`SECRET_KEY`
- 配置反向代理（如Nginx）
- 考虑使用Gunicorn或uWSGI代替Django开发服务器
- 配置数据库备份策略
- 启用HTTPS