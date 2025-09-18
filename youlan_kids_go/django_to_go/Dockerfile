# 使用官方Go镜像作为构建环境
FROM golang:1.21-alpine AS builder

# 设置工作目录
WORKDIR /app

# 复制go.mod和go.sum文件
COPY go.mod go.sum ./

# 下载依赖
RUN go mod download

# 复制源代码
COPY . .

# 构建应用
RUN CGO_ENABLED=0 GOOS=linux go build -o youlan_kids_go

# 使用Alpine作为运行环境，减小镜像大小
FROM alpine:3.18

# 添加tzdata包以支持时区设置
RUN apk --no-cache add ca-certificates tzdata

# 设置工作目录
WORKDIR /app

# 从构建阶段复制可执行文件
COPY --from=builder /app/youlan_kids_go .

# 复制配置文件（如果有）
COPY config/ config/

# 暴露应用端口
EXPOSE 8080

# 设置时区为上海
ENV TZ=Asia/Shanghai

# 启动命令
CMD ["./youlan_kids_go"]