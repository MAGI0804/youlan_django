@echo off
REM 更新配置文件和运行脚本

REM 首先检查应用程序是否有配置文件
echo ===== 检查配置文件 =====
dir /b config\*.go

REM 检查并显示主文件内容
echo. 
echo ===== 显示主文件内容（前20行）=====
type main.go | more +0

REM 创建一个临时配置文件，尝试使用不同的端口
echo. 
echo ===== 创建临时配置文件 =====
echo package config > config\temp_config.go
echo. >> config\temp_config.go
echo // 临时配置，使用8081端口 >> config\temp_config.go
echo var ServerPort = ":8081" >> config\temp_config.go

echo. 
echo ===== 重新编译应用程序 =====
go build -o youlan_kids_go main.go

REM 运行应用程序并监控端口
echo. 
echo ===== 运行应用程序（使用8081端口）=====
start "Go App" /b .\youlan_kids_go

REM 等待3秒
timeout /t 3 /nobreak > nul

REM 检查端口8081
echo. 
echo ===== 检查端口8081 =====
netstat -ano | findstr ":8081"

REM 检查应用程序进程
echo. 
echo ===== 检查应用程序进程 =====
tasklist | findstr "youlan_kids_go"

pause