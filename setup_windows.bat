@echo off
chcp 65001 >nul
:: ==============================================================================
:: 学城私有项目 - 纯净 Windows 电脑环境自动化静默配置脚本
:: 目标场景：电脑什么都没有 (无 Python, 无 Node)，但可以联网
:: ==============================================================================

echo ==========================================================
echo     学城私有项目 - 纯净 Windows 电脑环境自动化配置        
echo ==========================================================

cd /d "%~dp0"

:: 1. 探测是否已有 Python
set PYTHON_CMD=
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    goto :PYTHON_FOUND
)

py -3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py -3
    goto :PYTHON_FOUND
)

:: 2. 系统未安装 Python，开始全自动静默下载与安装
echo [*] 未检测到系统 Python，正在为您全自动静默就绪 Python 3.11 环境...

:: 尝试优先使用微软官方包管理器 winget
winget --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [*] 检测到系统内置 winget 工具，正在调用微软官方源静默安装 Python 3.11...
    winget install Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
    goto :REFRESH_ENV
)

:: 若无 winget，调用系统原生 PowerShell 下载官方安装器
echo [*] 正在调用 PowerShell 从国内高速镜像拉取 Python 3.11 安装器...
set INSTALLER_PATH=%TEMP%\python-3.11.9-amd64.exe
powershell -NoProfile -ExecutionPolicy Bypass -Command "Write-Host '正在下载 Python 3.11 (约25MB)...'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://registry.npmmirror.com/-/binary/python/3.11.9/python-3.11.9-amd64.exe', '%INSTALLER_PATH%')"

if not exist "%INSTALLER_PATH%" (
    echo [!] 镜像下载异常，尝试从官方源下载...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe', '%INSTALLER_PATH%')"
)

if exist "%INSTALLER_PATH%" (
    echo [*] 正在后台静默安装 Python 3.11 并自动配置系统路径 (请稍候约 30 秒)...
    "%INSTALLER_PATH%" /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1 Include_test=0
    del "%INSTALLER_PATH%" >nul 2>&1
) else (
    echo [!] 自动下载 Python 失败，请检查网络连接。
    pause
    exit /b 1
)

:REFRESH_ENV
:: 刷新当前 CMD 的环境变量 PATH
for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do set "SYS_PATH=%%b"
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "USER_PATH=%%b"
set "PATH=%SYS_PATH%;%USER_PATH%;%PATH%;C:\Program Files\Python311;C:\Program Files\Python311\Scripts;%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts"

python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
) else (
    echo [!] Python 已安装，但可能需要重启当前命令窗口以生效 PATH。
    echo 请直接双击运行 start_windows.bat 即可！
    pause
    exit /b 0
)

:PYTHON_FOUND
echo [√] 系统 Python 环境确认就绪:
%PYTHON_CMD% --version

:: 3. 创建本地独立运行环境 (.venv)
if not exist ".venv" (
    echo [*] 正在创建项目专属独立虚拟环境 (.venv)...
    %PYTHON_CMD% -m venv .venv
)

:: 4. 通过高速国内镜像极速安装后端依赖
echo [*] 正在通过国内镜像加速拉取后端依赖库 (DuckDB, FastAPI, Uvicorn 等)...
call .venv\Scripts\python.exe -m pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/ >nul 2>&1
call .venv\Scripts\pip.exe install -i https://mirrors.aliyun.com/pypi/simple/ -r backend\requirements.txt

if %errorlevel% neq 0 (
    echo [*] 阿里源重试失败，切换清华大学开源镜像拉取...
    call .venv\Scripts\pip.exe install -i https://pypi.tuna.tsinghua.edu.cn/simple -r backend\requirements.txt
)

echo ==========================================================
echo  [√] Windows 环境自动化配置完成！
echo  您现在可以直接双击 start_windows.bat 启动大屏系统！
echo ==========================================================
pause
