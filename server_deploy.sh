#!/bin/bash

# 服务器部署脚本 - 用于清理旧文件并从GitHub拉取最新代码

# 设置变量（用户需要根据实际情况修改）
GITHUB_REPO="https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git"
PROJECT_NAME="youlan_kids_customization"
DJANGO_APP_DIR="youlan_kids_django"

# 确保脚本有执行权限
# chmod +x server_deploy.sh

# 颜色定义
green="\033[0;32m"
red="\033[0;31m"
reset="\033[0m"

# 显示欢迎信息
echo -e "${green}====== 项目部署脚本 ======${reset}"

echo "1. 清理服务器上的旧项目文件..."

# 停止并移除任何正在运行的Docker容器
if [ -d "/opt/projects/${PROJECT_NAME}/${DJANGO_APP_DIR}" ]; then
    cd "/opt/projects/${PROJECT_NAME}/${DJANGO_APP_DIR}"
    echo "停止并移除正在运行的Docker容器..."
    docker-compose down --remove-orphans
fi

# 删除旧的项目文件
if [ -d "/opt/projects/${PROJECT_NAME}" ]; then
    echo "删除旧的项目文件..."
    sudo rm -rf "/opt/projects/${PROJECT_NAME}"
fi

# 创建项目目录
echo "创建项目目录..."
sudo mkdir -p "/opt/projects"
sudo chown -R $USER:$USER "/opt/projects"

# 克隆GitHub仓库
echo "2. 从GitHub拉取最新代码..."
cd "/opt/projects"
git clone $GITHUB_REPO $PROJECT_NAME

if [ $? -ne 0 ]; then
    echo -e "${red}错误：克隆GitHub仓库失败！请检查仓库URL是否正确，以及服务器是否有网络连接。${reset}"
    exit 1
fi

echo "设置文件权限..."
sudo chown -R $USER:$USER "/opt/projects/${PROJECT_NAME}"
sudo chmod -R 755 "/opt/projects/${PROJECT_NAME}"

# 进入Django应用目录
cd "/opt/projects/${PROJECT_NAME}/${DJANGO_APP_DIR}"

# 检查并创建.env文件
echo "3. 配置环境变量..."
if [ ! -f ".env" ]; then
    echo "创建.env文件..."
    cat > .env << EOF
SECRET_KEY=django-insecure-m89*e)$=h*0a#6!$=e+r@w5%985!j!f8y2mt%@#qw%o=i#!f*6
DEBUG=True
# 根据需要添加其他环境变量
EOF
    echo "注意：请根据实际需求修改.env文件中的配置！"
fi

# 使用Docker运行项目
echo "4. 构建并运行Docker容器..."

echo "检查Docker服务状态..."
if ! systemctl is-active --quiet docker; then
    echo "启动Docker服务..."
    sudo systemctl start docker
fi

echo "开始构建Docker镜像..."
DOCKER_BUILDKIT=1 docker-compose up -d --build

if [ $? -ne 0 ]; then
    echo -e "${red}错误：Docker构建失败！尝试清理缓存并重试...${reset}"
    docker system prune -a -f
    DOCKER_BUILDKIT=1 docker-compose up -d --build
    
    if [ $? -ne 0 ]; then
        echo -e "${red}错误：构建仍然失败！请检查网络连接和Docker配置。${reset}"
        echo "建议检查Docker守护进程配置："
        echo "sudo nano /etc/docker/daemon.json"
        echo "确保配置为：{}"
        echo "然后重启Docker服务：sudo systemctl restart docker"
        exit 1
    fi
fi

# 显示部署结果
echo -e "${green}5. 部署完成！${reset}"
echo "查看正在运行的容器："
docker ps
echo ""
echo "查看应用日志：docker-compose logs -f"
echo "访问应用：http://服务器IP:8000"
echo ""
echo "定期更新项目的命令："
echo "cd /opt/projects/${PROJECT_NAME}/${DJANGO_APP_DIR}"
echo "git pull origin main"
echo "docker-compose down"
echo "docker-compose up -d --build"