# 使用国内Docker镜像源的指南

由于Docker Hub连接超时问题，我们提供了一个使用国内Docker镜像源的替代配置方案。

## 配置说明

1. 我们创建了两个文件：
   - `docker-compose.cn.yml`：使用国内阿里云Docker镜像源的Compose配置文件
   - 更新了`Dockerfile`：支持通过构建参数指定基础镜像源

2. 国内镜像源的优势：
   - 更快的下载速度
   - 解决`failed to fetch oauth token`连接超时问题
   - 提高Docker镜像拉取和构建的稳定性

## 使用方法

### 方法1：直接使用国内配置文件

在项目根目录下，使用以下命令代替原来的`docker-compose`命令：

```bash
# 构建镜像
 docker-compose -f docker-compose.cn.yml build

# 运行容器
 docker-compose -f docker-compose.cn.yml up

# 停止并移除容器
 docker-compose -f docker-compose.cn.yml down
```

### 方法2：使用提供的批处理脚本（仅限Windows）

我们提供了批处理脚本`run_docker_cn.bat`，可以一键执行使用国内镜像源的Docker操作。

## 注意事项

1. 确保您的网络环境允许访问`registry.cn-hangzhou.aliyuncs.com`
2. 如果需要，可以在`docker-compose.cn.yml`文件中修改为其他可用的国内镜像源
3. 此配置仅改变了基础镜像的拉取源，不影响应用程序的功能