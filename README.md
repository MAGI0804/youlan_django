# 优蓝儿童定制化项目 - Django后端

## 项目简介
这是优蓝儿童定制化项目的Django后端服务，提供API接口和业务逻辑处理。

## 快速开始

### 开发环境配置
1. 进入Django项目目录
   ```bash
   cd youlan_kids_django
   ```

2. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

3. 运行开发服务器
   ```bash
   python manage.py runserver
   ```

## 部署说明
请参考 [django_migration_deployment_guide.md](django_migration_deployment_guide.md) 了解详细的部署步骤。

## Git操作指南

### 1. 初始化Git仓库 (已完成)
```bash
cd d:\youlan_kids_customization
git init
```

### 2. 添加文件并提交
```bash
git add .
git commit -m "Initial commit of youlan_kids_django"
```

### 3. 连接GitHub仓库
```bash
git remote add origin <https://github.com/MAGI0804/youlan_django.git>
git branch -M main
```

### 4. 推送到GitHub
```bash
git push -u origin main
```