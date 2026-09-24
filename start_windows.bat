@echo off
chcp 65001 >nul
:: ==============================================================================
:: 学城私有数据检索与大屏系统 - Windows 一键启动脚本
:: 100% 离线单机安全运行
:: ==============================================================================

echo ==========================================================
echo     人员数据态势分析大屏 [涉密专机系统]      
echo ==========================================================

cd /d "%~dp0"

:: 1. 检查虚拟环境
if not exist ".venv\Scripts\python.exe" (
    echo [*] 首次启动，正在检测并配置 Windows 运行环境...
    if exist "offline_wheels" (
        echo [*] 检测到离线依赖包 (offline_wheels)，执行本地离线安装...
        python -m venv .venv 2>nul || (
            echo [!] 未检测到 Python，正在启动自动环境安装...
            call setup_windows.bat
        )
        call .venv\Scripts\pip.exe install --no-index --find-links=offline_wheels -r backend\requirements.txt
    ) else (
        echo [*] 调用自动化配置脚本安装环境与依赖...
        call setup_windows.bat
    )
)

:: 2. 检查数据库文件
if not exist "data\xuecheng.duckdb" (
    echo [*] 未发现已构建数据库，开始检查 CSV 数据源...
    if exist "data\csv_sources\*.csv" (
        echo [*] 发现原始 CSV 文件，开始导入并构建索引...
        call .venv\Scripts\python.exe backend\scripts\import_csv.py
    ) else (
        echo [*] 未放入原始 CSV，正在为您生成演示仿真数据 (20万条)...
        call .venv\Scripts\python.exe backend\scripts\generate_mock.py --total 200000 --num-files 20
        call .venv\Scripts\python.exe backend\scripts\import_csv.py
    )
)

:: 3. 启动并自动打开浏览器
echo [√] 系统准备就绪，正在启动本地涉密服务器 (http://127.0.0.1:8000)...
start http://127.0.0.1:8000
call .venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

pause
