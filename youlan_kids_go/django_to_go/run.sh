#!/bin/bash

# 构建并启动Go应用

echo "正在启动优兰儿童Go应用..."

# 确保依赖已安装
go mod tidy

echo "依赖安装完成，开始构建应用..."

# 构建应用
go build -o youlan_kids_go

if [ $? -eq 0 ]; then
    echo "应用构建成功，正在启动..."
    # 启动应用
    ./youlan_kids_go
else
    echo "应用构建失败，请检查错误信息"
    exit 1
fi