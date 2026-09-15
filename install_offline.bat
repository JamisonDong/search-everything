@echo off
chcp 65001 >nul
:: ==============================================================================
:: 学城私有项目 - Windows 纯断网环境一键离线安装脚本
:: 100% 零外网请求 (--no-index)
:: ==============================================================================

echo ==========================================================
echo     学城私有项目 - Windows 纯断网环境一键离线安装与初始化  
echo ==========================================================

cd /d "%~dp0"

:: 1. 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] 错误: 未检测到系统 Python，请先安装 Python 3.10+ 并勾选 Add to PATH。
    pause
    exit /b 1
)

:: 2. 检查 offline_wheels 目录
if not exist "offline_wheels" (
    echo [!] 错误: 未找到 offline_wheels 目录，缺少离线依赖包！
    pause
    exit /b 1
)

:: 3. 创建虚拟环境
echo [*] 正在创建本地独立运行环境 (.venv)...
if not exist ".venv" (
    python -m venv .venv
)

:: 4. 纯离线安装依赖
echo [*] 正在从本地 offline_wheels 安装依赖 (严禁访问互联网)...
call .venv\Scripts\pip.exe install --no-index --find-links=offline_wheels -r backend\requirements.txt

if %errorlevel% neq 0 (
    echo [!] 依赖安装出现异常，请检查 Python 版本与 Wheel 架构是否匹配。
    pause
    exit /b 1
)

echo ==========================================================
echo  [√] 离线环境初始化成功！
echo  接下来直接双击 start_windows.bat 即可启动系统！
echo ==========================================================
pause
