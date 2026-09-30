@echo off
chcp 65001 >nul
setlocal
:: ==============================================================================
:: 人员数据态势分析大屏 - 从 CSV 创建或重建数据库
:: 读取 data\csv_sources 下的全部 CSV，清洗、去重并建立索引，生成 data\personnel.duckdb
:: 注意: 批处理的 if/else 代码块内不要写半角括号，会被 cmd 误判为代码块结束
:: ==============================================================================

cd /d "%~dp0"

echo ==========================================================
echo     人员数据态势分析大屏 - 从 CSV 创建数据库
echo ==========================================================

:: 1. 运行环境
if exist ".venv\Scripts\python.exe" goto :CHECK_CSV
echo [*] 运行环境尚未初始化，正在自动配置...
call setup_windows.bat --from-start
if not exist ".venv\Scripts\python.exe" goto :FAIL

:: 2. CSV 数据源
:CHECK_CSV
if not exist "data\csv_sources" mkdir "data\csv_sources"
dir /b "data\csv_sources\*.csv" >nul 2>&1
if not errorlevel 1 goto :CHECK_DB
echo [!] data\csv_sources 目录下没有 CSV 文件。
echo     请把原始 CSV 文件复制到: %~dp0data\csv_sources\
echo     然后重新双击 import_csv.bat。
goto :FAIL

:: 3. 已有数据库时确认重建
:CHECK_DB
if not exist "data\personnel.duckdb" goto :IMPORT
echo [!] 已存在数据库 data\personnel.duckdb。
echo     继续将按 data\csv_sources 中的全部 CSV 重新创建数据库，原数据库会被替换。
echo     请先关闭正在运行的大屏服务窗口。
choice /C YN /N /M "是否继续？[Y/N]: "
if errorlevel 2 goto :CANCEL
del /q "data\personnel.duckdb" "data\personnel.duckdb.wal" >nul 2>&1
if not exist "data\personnel.duckdb" goto :IMPORT
echo [!] 旧数据库正在被占用，无法替换。请先关闭大屏服务窗口后重试。
goto :FAIL

:: 4. 导入与建索引
:IMPORT
echo [*] 开始清洗数据、去重并建立索引。1600 万条约需 3~5 分钟，请勿关闭窗口...
".venv\Scripts\python.exe" backend\scripts\import_csv.py
if not errorlevel 1 goto :DONE
echo [!] 导入失败，请检查上方错误信息与 CSV 文件格式。
del /q "data\personnel.duckdb" "data\personnel.duckdb.wal" >nul 2>&1
goto :FAIL

:DONE
echo ==========================================================
echo  [√] 数据库创建完成！双击 start_windows.bat 即可启动大屏。
echo ==========================================================
pause
exit /b 0

:CANCEL
echo 已取消，原数据库保持不变。
pause
exit /b 0

:FAIL
pause
exit /b 1
