@echo off

REM 设置本地环境变量
set DB_HOST=127.0.0.1
set DB_PORT=3306
set DB_NAME=wechat_member
set DB_USER=root
set DB_PASSWORD=

REM 显示设置的环境变量
echo 环境变量已设置:
echo DB_HOST=%DB_HOST%
echo DB_PORT=%DB_PORT%
echo DB_NAME=%DB_NAME%
echo DB_USER=%DB_USER%

echo 正在运行应用程序...
youlan_kids_go

pause