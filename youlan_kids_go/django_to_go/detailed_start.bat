@echo off
REM 详细启动脚本，用于捕获应用程序的环境变量和日志输出

REM 显示当前的环境变量
echo ===== 当前环境变量 =====
env

echo. 
echo ===== 启动应用程序 =====
REM 启动应用程序并将所有输出重定向到日志文件
start "Go App" /b .\youlan_kids_go > app.log 2>&1

REM 等待3秒，让应用程序有时间启动
ping -n 3 127.0.0.1 > nul

REM 检查应用程序是否在运行
echo. 
echo ===== 检查应用程序进程 =====
tasklist | findstr "youlan_kids_go"

REM 检查端口8080是否在使用中
echo. 
echo ===== 检查端口8080 =====
netstat -ano | findstr ":8080"

REM 显示应用程序日志
echo. 
echo ===== 应用程序日志 =====
type app.log

pause