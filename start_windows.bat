@echo off
chcp 65001 >nul
:: ==============================================================================
:: 学城私有数据检索与大屏系统 - Windows 一键启动脚本
:: 100% 离线单机安全运行
:: ==============================================================================

echo ==========================================================
echo     学城人员综合数据智能检索分析大屏 [涉密专机系统]      
echo ==========================================================

cd /d "%~dp0"

:: 1. 检查虚拟环境
if not exist ".venv" (
    echo [*] 正在初始化 Python 虚拟运行环境...
    python -m venv .venv
    if exist "offline_wheels" (
        echo [*] 检测到离线依赖包 (offline_wheels)，执行纯断网无网安装...
        call .venv\Scripts\pip.exe install --no-index --find-links=offline_wheels -r backend\requirements.txt
    ) else (
        call .venv\Scripts\pip.exe install -r backend\requirements.txt
    )
)

:: 2. 检查数据库文件
if not exist "data\xuecheng.duckdb" (
    echo [*] 未发现已构建数据库，开始处理数据...
    call .venv\Scripts\python backend\scripts\import_csv.py
)

:: 3. 启动并自动打开浏览器
echo [√] 系统准备就绪，正在启动本地涉密服务器 (http://127.0.0.1:8000)...
start http://127.0.0.1:8000
call .venv\Scripts\python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

pause
