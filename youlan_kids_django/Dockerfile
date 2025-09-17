# 使用Python 3.10作为基础镜像
# 支持构建参数BASE_IMAGE来指定镜像源
ARG BASE_IMAGE=python:3.10-slim-buster
FROM ${BASE_IMAGE}

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements.txt并安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 配置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONUTF8=1 \
    PYTHONIOENCODING=utf-8

# 暴露应用端口
EXPOSE 8000

# 运行Django应用
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]