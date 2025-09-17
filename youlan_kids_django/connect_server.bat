@echo off
REM 连接到远程CentOS服务器的批处理脚本

cls
echo =====================================================
echo         连接到远程服务器

echo 服务器信息:
echo - 操作系统: CentOS Linux 8
echo - 用户名: ecs-assist-user
echo - 服务器名称: iZuf635nesowrxp7kll8pgZ
echo - Docker状态: 未安装
echo =====================================================
echo.

echo 正在连接到服务器...
ssh ecs-assist-user@iZuf635nesowrxp7kll8pgZ

echo 连接已断开。
pause