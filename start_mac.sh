#!/usr/bin/env bash
# ==============================================================================
# 人员数据态势分析大屏 - Mac/Linux 一键启动脚本
# 100% 离线单机安全运行
# ==============================================================================

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=========================================================="
echo "    人员数据态势分析大屏"
echo "=========================================================="

# 1. 检查 Python 环境
if [ ! -d ".venv" ]; then
    echo "[*] 初始化 Python 虚拟运行环境..."
    python3 -m venv .venv
    if [ -d "offline_wheels" ]; then
        echo "[*] 检测到离线依赖包 (offline_wheels/)，执行纯断网无网安装..."
        .venv/bin/pip install --no-index --find-links=offline_wheels/ -r backend/requirements.txt
    else
        .venv/bin/pip install -r backend/requirements.txt
    fi
fi

# 2. 检查数据库文件
if [ ! -f "data/personnel.duckdb" ]; then
    echo "[!] 未检测到数据库文件 (data/personnel.duckdb)。"
    CSV_COUNT=$(ls -1 data/csv_sources/*.csv 2>/dev/null | wc -l || true)
    if [ "$CSV_COUNT" -gt 0 ]; then
        echo "[*] 检测到 $CSV_COUNT 个原始 CSV 文件，开始导入..."
        .venv/bin/python backend/scripts/import_csv.py
    else
        echo "[*] 未发现原始 CSV，生成仿真演示数据 (20万条)..."
        .venv/bin/python backend/scripts/generate_mock.py --total 200000 --num-files 20 --output-dir data/demo_csv
        .venv/bin/python backend/scripts/import_csv.py --csv-dir data/demo_csv
    fi
fi

# 3. 检查前端静态产物
if [ ! -d "frontend/dist" ]; then
    if command -v npm &> /dev/null; then
        echo "[*] 检测到前端尚未构建，开始本地静态打包..."
        cd frontend && npm run build && cd ..
    else
        echo "[!] 警告: 缺少 frontend/dist 静态产物且系统无 npm，请使用离线分发包完整产物。"
    fi
fi

echo "[√] 系统准备就绪，正在启动本地服务 (http://127.0.0.1:8000)..."

# 4. 自动打开浏览器
(sleep 1 && open "http://127.0.0.1:8000") &

# 5. 启动服务
.venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
