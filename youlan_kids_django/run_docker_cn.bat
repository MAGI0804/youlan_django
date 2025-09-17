@echo off
REM 使用国内Docker镜像源的批处理脚本

cls
echo =====================================================
echo        使用国内Docker镜像源运行项目

echo 此脚本使用阿里云Docker镜像源，解决连接超时问题
echo =====================================================
echo.

echo 请选择要执行的操作:
echo 1. 构建并运行Docker容器
echo 2. 仅构建Docker镜像
echo 3. 仅运行Docker容器
echo 4. 停止并移除Docker容器
echo 5. 查看容器日志
echo 6. 进入Docker容器
echo 7. 退出

echo.
set /p choice=请输入选项(1-7): 

if "%choice%"=="1" goto build_and_run
if "%choice%"=="2" goto build_only
if "%choice%"=="3" goto run_only
if "%choice%"=="4" goto stop_remove
if "%choice%"=="5" goto view_logs
if "%choice%"=="6" goto enter_container
if "%choice%"=="7" goto exit

echo 无效的选项，请重新运行脚本。
pause
goto :eof

:build_and_run
echo 开始构建并运行Docker容器(使用国内镜像源)...
docker-compose -f docker-compose.cn.yml build
docker-compose -f docker-compose.cn.yml up
goto :eof

:build_only
echo 开始构建Docker镜像(使用国内镜像源)...
docker-compose -f docker-compose.cn.yml build
echo 构建完成。
pause
goto :eof

:run_only
echo 开始运行Docker容器(使用国内镜像源)...
docker-compose -f docker-compose.cn.yml up
goto :eof

:stop_remove
echo 停止并移除Docker容器...
docker-compose -f docker-compose.cn.yml down
echo 操作完成。
pause
goto :eof

:view_logs
echo 查看容器日志...
docker-compose -f docker-compose.cn.yml logs -f
goto :eof

:enter_container
echo 进入Docker容器...
docker-compose -f docker-compose.cn.yml exec web /bin/bash
goto :eof

:exit
echo 感谢使用，再见！
pause