# 使用官方Python镜像作为基础镜像
FROM python:3.10-slim-buster

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=100

# 配置pip使用国内镜像源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn

# 创建并设置工作目录
WORKDIR /app

# 安装项目依赖
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 复制项目代码到工作目录
COPY . .

# 暴露端口
EXPOSE 8000

# 运行Django服务器
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]