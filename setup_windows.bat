@echo off
chcp 65001 >nul
setlocal
:: ==============================================================================
:: 人员数据态势分析大屏 - Windows 运行环境自动配置，目标机需可联网
:: 未安装 Python 时自动安装 Python 3.11 到当前用户目录，无需管理员权限；
:: 然后创建 .venv 并通过国内镜像安装后端依赖。
:: 通常由 start_windows.bat 自动调用，也可单独双击运行。
:: 注意: 批处理的 if/else 代码块内不要写半角括号，会被 cmd 误判为代码块结束
:: ==============================================================================

cd /d "%~dp0"
set "RC=0"

echo [*] 正在检测 Python 环境...
set "PYTHON_EXE="
call :PROBE python
if not defined PYTHON_EXE call :PROBE py -3
if not defined PYTHON_EXE call :PROBE_PATHS
if defined PYTHON_EXE goto :PYTHON_FOUND

echo [*] 未检测到 Python 3.10 及以上版本，开始自动安装 Python 3.11...
winget --version >nul 2>&1
if errorlevel 1 goto :DOWNLOAD_INSTALLER
echo [*] 通过系统自带的 winget 安装 Python 3.11，请稍候...
winget install -e --id Python.Python.3.11 --scope user --silent --accept-package-agreements --accept-source-agreements
call :PROBE_PATHS
if defined PYTHON_EXE goto :PYTHON_FOUND
echo [!] winget 安装未成功，改为下载安装程序...

:DOWNLOAD_INSTALLER
set "INSTALLER_PATH=%TEMP%\python-3.11.9-amd64.exe"
echo [*] 正在下载 Python 3.11 安装程序，约 25MB...
powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $out = '%INSTALLER_PATH%'; foreach ($u in @('https://registry.npmmirror.com/-/binary/python/3.11.9/python-3.11.9-amd64.exe', 'https://mirrors.huaweicloud.com/python/3.11.9/python-3.11.9-amd64.exe', 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe')) { try { (New-Object Net.WebClient).DownloadFile($u, $out); if ((Get-Item $out).Length -gt 20MB) { exit 0 } } catch { } }; exit 1"
if errorlevel 1 goto :INSTALL_FAILED
echo [*] 正在静默安装 Python 3.11，约需 1 分钟...
"%INSTALLER_PATH%" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_test=0
del /q "%INSTALLER_PATH%" >nul 2>&1
call :PROBE_PATHS
if defined PYTHON_EXE goto :PYTHON_FOUND

:INSTALL_FAILED
echo [!] Python 自动安装失败。请手动安装 Python 3.11，安装时勾选 Add python.exe to PATH，
echo     然后重新双击 start_windows.bat。
set "RC=1"
goto :END

:PYTHON_FOUND
echo [√] 使用 Python: %PYTHON_EXE%
if exist ".venv\Scripts\python.exe" goto :INSTALL_DEPS
echo [*] 正在创建项目独立运行环境 .venv ...
"%PYTHON_EXE%" -m venv .venv
if errorlevel 1 goto :VENV_FAILED

:INSTALL_DEPS
echo [*] 正在通过国内镜像安装后端依赖：DuckDB、FastAPI、Uvicorn 等...
".venv\Scripts\python.exe" -m pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/ >nul 2>&1
".venv\Scripts\python.exe" -m pip install -i https://mirrors.aliyun.com/pypi/simple/ -r backend\requirements.txt
if not errorlevel 1 goto :DONE
echo [*] 阿里云镜像安装失败，切换清华大学镜像重试...
".venv\Scripts\python.exe" -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r backend\requirements.txt
if not errorlevel 1 goto :DONE
echo [*] 国内镜像均失败，尝试官方源...
".venv\Scripts\python.exe" -m pip install -r backend\requirements.txt
if not errorlevel 1 goto :DONE
echo [!] 依赖安装失败，请检查网络连接后重新双击 start_windows.bat。
set "RC=1"
goto :END

:VENV_FAILED
echo [!] 创建 .venv 失败，请检查磁盘空间与目录写入权限。
set "RC=1"
goto :END

:DONE
echo [√] 运行环境配置完成。

:END
if /i not "%~1"=="--from-start" pause
exit /b %RC%

:: ---------- 子程序 ----------
:PROBE
:: 用给定命令探测 Python，只接受 3.10 及以上版本，输出其完整路径
for /f "delims=" %%i in ('%* -c "import sys; print(sys.executable) if sys.version_info >= (3, 10) else None" 2^>nul') do set "PYTHON_EXE=%%i"
exit /b 0

:PROBE_PATHS
:: 安装后当前窗口的 PATH 不会刷新，直接查找默认安装位置
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"& exit /b 0
if exist "%ProgramFiles%\Python311\python.exe" set "PYTHON_EXE=%ProgramFiles%\Python311\python.exe"& exit /b 0
exit /b 0
