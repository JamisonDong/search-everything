@echo off
chcp 65001 >nul
:: ==============================================================================
:: 学城私有项目 - Windows 现场一键导数工具 (导入 20+ 个 CSV 1600万数据)
:: ==============================================================================

echo ==========================================================
echo     学城私有项目 - 1600万数据本地数据库一键导入工具       
echo ==========================================================

cd /d "%~dp0"

:: 1. 检查 Python 运行环境
if not exist ".venv\Scripts\python.exe" (
    echo [*] 检测到运行环境尚未初始化，正在自动配置环境...
    call setup_windows.bat
)

:: 2. 检查 CSV 数据源目录
if not exist "data\csv_sources" (
    mkdir "data\csv_sources"
)

dir /b "data\csv_sources\*.csv" >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] 提示: 在 data\csv_sources 目录下未检测到任何 .csv 文件！
    echo 请将您的 20 多个原始 CSV 文件复制到该目录下:
    echo 👉 %~dp0data\csv_sources\
    echo.
    set /p CHOICE="是否生成 20 万条高仿真测试数据用于体验？(Y/N): "
    if /i "%CHOICE%"=="Y" (
        echo [*] 正在生成 20 万条测试数据并切分为 20 个 CSV 文件...
        call .venv\Scripts\python.exe backend\scripts\generate_mock.py --total 200000 --num-files 20
    ) else (
        echo [!] 请放入真实 CSV 文件后再次双击运行本脚本。
        pause
        exit /b 0
    )
)

:: 3. 执行高效清洗、排重与建库
echo [*] 开始执行数据清洗、唯一性排重与 DuckDB 列存索引构建...
call .venv\Scripts\python.exe backend\scripts\import_csv.py

if %errorlevel% neq 0 (
    echo [!] 导入过程中出现错误，请检查 CSV 格式。
    pause
    exit /b 1
)

echo ==========================================================
echo  [√] 1600 万数据导入与全量索引构建完毕！
echo  现在您可以直接双击 start_windows.bat 启动大屏系统进行检索！
echo ==========================================================
pause
