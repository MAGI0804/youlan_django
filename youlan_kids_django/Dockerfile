FROM python:3.10-slim-buster

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=100

# 配置pip使用国内镜像源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn

# 直接在根目录复制和安装，避免路径问题
COPY . /app/
WORKDIR /app

# 安装项目依赖
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install gunicorn

# 暴露端口
EXPOSE 8000

# 运行Gunicorn WSGI服务器，使用4个工作进程
CMD ["gunicorn", "youlan_kids_django.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "300"]