@echo off
chcp 65001 >nul
setlocal
:: ==============================================================================
:: 人员数据态势分析大屏 - Windows 一键安装与启动
:: 首次运行: 自动安装 Python 与依赖、从 CSV 创建数据库、配置本地访问域名
:: 之后运行: 直接启动服务并打开大屏
:: 注意: 批处理的 if/else 代码块内不要写半角括号，会被 cmd 误判为代码块结束
:: ==============================================================================

:: ---------- 访问地址配置，可按需修改 ----------
:: 本地域名写入本机 hosts 并指向 127.0.0.1，只有本机能访问
set "APP_DOMAIN=dashboard.internal"
set "APP_PORT=8000"

cd /d "%~dp0"

echo ==========================================================
echo     人员数据态势分析大屏
echo ==========================================================

:: ---------- 1. Python 运行环境 ----------
if exist ".venv\Scripts\python.exe" goto :ENV_CHECK
echo [*] 首次启动，正在配置运行环境...
if not exist "offline_wheels" goto :ENV_ONLINE

echo [*] 检测到离线依赖包 offline_wheels，执行本地离线安装...
python -m venv .venv >nul 2>&1
if errorlevel 1 goto :ENV_ONLINE
".venv\Scripts\python.exe" -m pip install --no-index --find-links=offline_wheels -r backend\requirements.txt
if not errorlevel 1 goto :ENV_CHECK
echo [!] 离线依赖与本机 Python 版本不匹配，改为联网安装...

:ENV_ONLINE
call setup_windows.bat --from-start
if not exist ".venv\Scripts\python.exe" goto :ENV_FAILED

:ENV_CHECK
".venv\Scripts\python.exe" -c "import duckdb, fastapi, uvicorn" >nul 2>&1
if not errorlevel 1 goto :DB_CHECK
echo [*] 依赖库不完整，正在联网补装...
call setup_windows.bat --from-start
".venv\Scripts\python.exe" -c "import duckdb, fastapi, uvicorn" >nul 2>&1
if not errorlevel 1 goto :DB_CHECK

:ENV_FAILED
echo [!] 运行环境未就绪。若刚刚安装完 Python，请关闭本窗口后重新双击 start_windows.bat。
pause
exit /b 1

:: ---------- 2. 数据库 ----------
:DB_CHECK
if exist "data\personnel.duckdb" goto :DOMAIN
if not exist "data\csv_sources" mkdir "data\csv_sources"
dir /b "data\csv_sources\*.csv" >nul 2>&1
if errorlevel 1 goto :NO_CSV
echo [*] 发现 CSV 数据文件，开始创建数据库并建立索引。数据量大时需要几分钟，请勿关闭窗口...
".venv\Scripts\python.exe" backend\scripts\import_csv.py
if errorlevel 1 goto :DB_FAILED
goto :DOMAIN

:NO_CSV
echo.
echo [!] 尚未创建数据库，且 data\csv_sources 目录下没有 CSV 文件。
echo     请把原始 CSV 文件复制到: %~dp0data\csv_sources\
echo     然后重新双击 start_windows.bat，将自动创建数据库。
echo.
echo     如只想先看演示效果，可生成 20 万条模拟数据。演示数据单独存放，不会混入真实数据；
echo     之后放入真实 CSV 并双击 import_csv.bat 即可替换为真实数据库。
choice /C YN /N /M "是否生成演示数据？[Y/N]: "
if errorlevel 2 exit /b 0
".venv\Scripts\python.exe" backend\scripts\generate_mock.py --total 200000 --num-files 20 --output-dir data\demo_csv
if errorlevel 1 goto :DB_FAILED
".venv\Scripts\python.exe" backend\scripts\import_csv.py --csv-dir data\demo_csv
if errorlevel 1 goto :DB_FAILED
goto :DOMAIN

:DB_FAILED
echo [!] 数据库创建失败，请检查上方错误信息与 CSV 文件格式。
del /q "data\personnel.duckdb" "data\personnel.duckdb.wal" >nul 2>&1
pause
exit /b 1

:: ---------- 3. 本地访问域名 ----------
:DOMAIN
set "APP_URL=http://127.0.0.1:%APP_PORT%"
echo [*] 正在配置本地访问域名 %APP_DOMAIN%。首次配置会弹出管理员授权窗口，请点击“是”...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0backend\scripts\setup_local_domain.ps1" -Domain "%APP_DOMAIN%"
if errorlevel 1 goto :DOMAIN_FAILED
set "APP_URL=http://%APP_DOMAIN%:%APP_PORT%"
goto :START

:DOMAIN_FAILED
echo [!] 本地域名未配置成功，可能未同意管理员授权或被安全软件拦截，本次改用 %APP_URL% 访问。

:: ---------- 4. 启动服务 ----------
:START
echo.
echo [√] 系统准备就绪，大屏访问地址: %APP_URL%
echo     服务启动后将自动打开浏览器。关闭本窗口即停止服务。
echo.
:: 等端口可连接后再打开浏览器，避免服务未就绪时页面报错
start "" /min powershell -NoProfile -WindowStyle Hidden -Command "for ($i = 0; $i -lt 120; $i++) { try { $c = New-Object Net.Sockets.TcpClient; $c.Connect('127.0.0.1', %APP_PORT%); $c.Close(); break } catch { Start-Sleep -Milliseconds 500 } }; Start-Process '%APP_URL%'"
".venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port %APP_PORT%
pause
