@echo off
REM 启动应用程序并记录输出到日志文件
.\youlan_kids_go > app.log 2>&1
REM 显示日志文件内容
type app.log
pause