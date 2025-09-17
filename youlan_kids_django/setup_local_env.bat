@echo off
REM ===================================================
REM 悠蓝儿童项目 - 本地开发环境设置脚本
REM 此脚本适用于Windows环境，帮助在无法使用Docker时快速设置开发环境
REM ===================================================

echo 开始设置本地开发环境...
echo.

REM 1. 检查Python安装情况
python --version >nul 2>&1
if %errorlevel% neq 0 (
echo 错误: 未找到Python安装。请先安装Python 3.10或更高版本。
echo 访问 https://www.python.org/downloads/ 下载安装。
pause
exit /b 1
)

REM 2. 检查Python版本
for /f "tokens=2 delims=." %%i in ('python --version 2^>^&1') do set PYTHON_MAJOR=%%i
for /f "tokens=3 delims=." %%i in ('python --version 2^>^&1') do set PYTHON_MINOR=%%i

if %PYTHON_MAJOR% lss 3 (
echo 错误: 需要Python 3.10或更高版本，当前版本为Python %PYTHON_MAJOR%.%PYTHON_MINOR%
pause
exit /b 1
) else if %PYTHON_MAJOR% equ 3 if %PYTHON_MINOR% lss 10 (
echo 错误: 需要Python 3.10或更高版本，当前版本为Python %PYTHON_MAJOR%.%PYTHON_MINOR%
pause
exit /b 1
) else (
echo 已检测到Python %PYTHON_MAJOR%.%PYTHON_MINOR%，版本符合要求
)

echo.

REM 3. 创建虚拟环境
if not exist "venv" (
echo 创建虚拟环境...
python -m venv venv
if %errorlevel% neq 0 (
echo 错误: 创建虚拟环境失败。
pause
exit /b 1
)
echo 虚拟环境创建成功。
) else (
echo 虚拟环境已存在，跳过创建步骤。
)

echo.

REM 4. 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
echo 错误: 激活虚拟环境失败。
pause
exit /b 1
)
echo 虚拟环境已激活。

echo.

REM 5. 安装项目依赖
echo 安装项目依赖...
pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
echo 错误: 安装依赖失败。请检查requirements.txt文件或网络连接。
pause
exit /b 1
)
echo 依赖安装成功。

echo.

REM 6. 提示用户数据库连接状态
echo 注意：项目配置使用阿里云RDS数据库（%DB_HOST%）
echo 请确保您的网络可以访问该数据库服务器。
echo.

REM 7. 提供操作菜单
echo ====== 开发环境设置完成 ======
echo 请选择要执行的操作：
echo 1. 运行开发服务器
rem echo 2. 执行数据库迁移（注意：请确保有权限修改数据库）
echo 2. 退出

echo.
set /p choice="请输入选项 [1-2]: "

if "%choice%" equ "1" (
echo 启动Django开发服务器...
echo 服务器将在 http://127.0.0.1:8000 上运行
python manage.py runserver
) else if "%choice%" equ "2" (
echo 退出脚本。
echo 若要再次使用开发环境，请手动运行 venv\Scripts\activate.bat 激活虚拟环境。
pause
exit /b 0
) else (
echo 无效的选项。请重新运行脚本并选择有效的选项。
pause
exit /b 1
)

:end
echo 脚本执行完毕。
pause