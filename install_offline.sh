#!/usr/bin/env bash
# ==============================================================================
# 人员数据态势分析大屏 - 断网目标机纯离线安装脚本 (Mac / Linux)
# 100% 零外网请求 (--no-index)
# ==============================================================================

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=========================================================="
echo "    人员数据态势分析大屏 - 纯断网环境一键离线安装与初始化        "
echo "=========================================================="

# 1. 检查 Python 3
if ! command -v python3 &> /dev/null; then
    echo "[!] 错误: 未检测到系统 Python 3，请先安装 Python 3.10 或更高版本。"
    exit 1
fi

PY_VER=$(python3 --version)
echo "[*] 检测到系统环境: $PY_VER"

# 2. 检查离线 Wheel 目录
if [ ! -d "offline_wheels" ]; then
    echo "[!] 错误: 未找到 offline_wheels/ 目录，缺少离线依赖包！"
    exit 1
fi

# 3. 创建虚拟环境
echo "[*] 正在创建本地独立运行环境 (.venv)..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# 4. 纯离线安装依赖
echo "[*] 正在从本地 offline_wheels/ 安装依赖 (严禁访问互联网)..."
.venv/bin/pip install --no-index --find-links=offline_wheels/ -r backend/requirements.txt

# 5. 赋权
chmod +x start_mac.sh 2>/dev/null || true

echo "=========================================================="
echo " [√] 离线环境初始化成功！"
echo " 接下来只需执行: ./start_mac.sh 即可直接启动系统！"
echo "=========================================================="
