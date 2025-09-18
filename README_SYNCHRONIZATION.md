# 商品数据同步指南

## 概述

本指南提供了如何同步商品数据到`StyleCodeData`模型的详细说明，以及在Docker服务未运行时的替代方案。

## 已完成的工作

1. **添加了`StyleCodeData`模型**：
   - 在`commodity/models.py`中添加了新模型，以`style_code`为主键
   - 包含`name`、`image`、`category`、`category_detail`和`price`字段
   - 自动在添加商品时创建或更新对应记录

2. **添加了搜索类目路由**：
   - 在`commodity/views.py`中添加了`search_categories`视图函数
   - 在`commodity/urls.py`中添加了`search_categories`路由
   - 该接口可以返回所有类目的详细信息，支持搜索功能

3. **创建了数据同步脚本**：
   - `sync_style_code_data.py`用于同步现有商品数据到`StyleCodeData`模型

## 使用指南

### 前提条件

确保您的环境满足以下要求：

- Python 3.6+ 和 Django
- Docker服务（如果使用容器化部署）
- 已安装项目依赖（可以通过`pip install -r requirements.txt`安装）

### 方案一：使用Docker容器（推荐）

如果您使用Docker容器运行项目，请按照以下步骤操作：

1. **启动Docker服务**
   
   在Windows上，可以通过以下方式启动Docker：
   - 点击桌面快捷方式
   - 或通过Windows开始菜单搜索并启动Docker Desktop

2. **启动项目容器**
   
   ```bash
   cd d:/youlan_kids_customization
   docker-compose up -d
   ```

3. **执行数据库迁移**
   
   ```bash
   docker exec -it youlan_kids_django_web_1 python manage.py migrate
   ```

4. **运行同步脚本**
   
   ```bash
   python sync_style_code_data.py
   ```

### 方案二：在本地环境执行（替代方案）

如果您无法使用Docker，可以在本地环境中执行以下操作：

1. **激活Python虚拟环境**（如果使用）
   
   ```bash
   # 假设您有一个名为venv的虚拟环境
   venv\Scripts\activate
   ```

2. **执行数据库迁移**
   
   ```bash
   cd d:/youlan_kids_customization/youlan_kids_django
   python manage.py migrate
   ```

3. **运行同步脚本**
   
   ```bash
   cd d:/youlan_kids_customization
   python sync_style_code_data.py
   ```

## 搜索类目API使用说明

新添加的`search_categories`接口可以返回所有类目的详细信息，包括主类目和子类目（category_detail）。

### 请求格式

```bash
POST /commodity/search_categories
Content-Type: application/json

{
    "shopname": "youlan_kids",
    "search_keyword": "可选的搜索关键词"
}
```

### 响应格式

```json
{
    "code": 200,
    "message": "查询成功",
    "data": [
        {
            "name": "类目名称",
            "details": ["子类目1", "子类目2", ...]
        },
        ...
    ],
    "total_count": 类目总数
}
```

## 故障排除

### 常见问题

1. **Docker服务未运行**
   
   如果收到类似`error during connect: Get "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/v1.51/containers/...`的错误，请确保Docker Desktop已启动。

2. **数据库连接问题**
   
   如果同步脚本无法连接到数据库，请检查您的数据库配置和连接状态。

3. **权限问题**
   
   如果遇到文件权限错误，请确保您有足够的权限访问项目文件和运行相关命令。

## 后续步骤

完成数据同步后，您可以：

1. 验证`StyleCodeData`模型是否正确存储了数据
2. 使用新的`search_categories`接口获取类目信息
3. 继续开发其他功能或进行测试

如需进一步帮助，请联系系统管理员或开发团队。

---
更新时间：`${datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`