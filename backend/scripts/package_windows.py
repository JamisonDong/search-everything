#!/usr/bin/env python3
"""
学城私有项目 - Windows 纯断网离线安装包专属打包工具
在有外网的开发机 (Mac/Linux/Win) 上运行。
核心功能：
1. 定向跨平台下载 Windows 64位 (win_amd64) 二进制 Wheel 依赖库 (DuckDB, FastAPI, Pydantic 等)。
2. 自动排除 Windows 不支持的 unix-only 依赖 (如 uvloop)。
3. 检查并编译前端静态产物至 frontend/dist。
4. 封装包含 Windows 一键启动脚本、离线安装脚本、导数工具与说明文档的 ZIP 分发包。
"""

import os
import sys
import shutil
import subprocess
import zipfile
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Windows 环境专属依赖清单 (排除 unix 专属的 uvloop)
WINDOWS_REQUIREMENTS = [
    "duckdb>=1.2.0",
    "fastapi>=0.115.0",
    "uvicorn>=0.34.0",
    "pydantic>=2.10.0",
    "python-multipart>=0.0.20",
    "starlette>=0.46.0",
    "anyio>=3.6.2",
    "idna>=2.8",
    "click>=7.0",
    "h11>=0.8",
    "annotated-types>=0.6.0",
    "typing-extensions>=4.8.0"
]

def run_cmd(cmd, cwd=PROJECT_ROOT):
    print(f"[*] 执行: {cmd}")
    res = subprocess.run(cmd, shell=True, cwd=cwd)
    if res.returncode != 0:
        print(f"[!] 指令失败，退出代码: {res.returncode}")
        sys.exit(res.returncode)

def download_windows_wheels(dest_dir: Path, py_version: str = "311"):
    """
    通过 pip 在 Mac/Linux 上跨平台定向下载 Windows win_amd64 wheels
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # 转换为 pip 能够识别的格式，如 311 对应 Python 3.11
    req_file = dest_dir / "requirements_win.txt"
    with open(req_file, "w", encoding="utf-8") as f:
        f.write("\n".join(WINDOWS_REQUIREMENTS) + "\n")

    print(f"[*] 正在跨平台拉取 Windows (win_amd64) 依赖轮子 (目标 Python: {py_version})...")
    
    pip_cmd = (
        f"{sys.executable} -m pip download "
        f"--platform win_amd64 "
        f"--python-version {py_version} "
        f"--implementation cp "
        f"--abi cp{py_version} "
        f"--only-binary=:all: "
        f"--dest {dest_dir} "
        f"-r {req_file}"
    )
    run_cmd(pip_cmd)
    
    # 清理临时需求文件
    if req_file.exists():
        req_file.unlink()

    wheels = list(dest_dir.glob("*.whl"))
    print(f"[√] Windows 离线 Wheels 下载完毕，共计 {len(wheels)} 个轮子文件。")
    return len(wheels)

def main():
    parser = argparse.ArgumentParser(description="制作学城项目 Windows 专属离线部署安装包")
    parser.add_argument("--output", type=str, default="xuecheng_windows_v1.0.zip", help="输出压缩包名")
    parser.add_argument("--py-version", type=str, default="311", help="目标 Windows 机器 Python 版本 (默认 311 代表 Python 3.11)")
    parser.add_argument("--include-db", action="store_true", help="是否随包携带预制数据库 (data/xuecheng.duckdb)")
    args = parser.parse_args()

    print("==========================================================")
    print(f"  学城私有项目 - Windows 纯断网离线分发包打包工具        ")
    print(f"  目标系统: Windows (x86_64 / win_amd64)                 ")
    print(f"  目标 Python 版本: {args.py_version}                     ")
    print("==========================================================")

    # 1. 检查/编译前端
    dist_dir = PROJECT_ROOT / "frontend" / "dist"
    print("\n>>> 步骤 1/4: 检查前端静态产物...")
    if not (dist_dir / "index.html").exists():
        print("[*] 正在编译前端...")
        run_cmd("npm run build", cwd=PROJECT_ROOT / "frontend")
    else:
        print("[√] 前端已存在预编译静态产物 (frontend/dist)。")

    # 2. 下载 Windows win_amd64 专属 Wheels
    wheels_dir = PROJECT_ROOT / "offline_wheels_win"
    print("\n>>> 步骤 2/4: 下载 Windows 专属二进制依赖轮子...")
    download_windows_wheels(wheels_dir, py_version=args.py_version)

    # 3. 准备 ZIP 打包清单
    output_zip = PROJECT_ROOT / args.output
    if output_zip.exists():
        output_zip.unlink()

    include_items = [
        ("backend", "backend"),
        ("frontend/dist", "frontend/dist"),
        ("offline_wheels_win", "offline_wheels"), # 在 Windows 解压包中统一命名为 offline_wheels
        ("start_windows.bat", "start_windows.bat"),
        ("install_offline.bat", "install_offline.bat"),
        ("import_csv.bat", "import_csv.bat"),
        ("README.md", "README.md"),
        (".gitignore", ".gitignore")
    ]

    if args.include_db:
        db_path = PROJECT_ROOT / "data" / "xuecheng.duckdb"
        if db_path.exists():
            include_items.append(("data/xuecheng.duckdb", "data/xuecheng.duckdb"))
            print(f"[*] 随包包含 1600 万已建库数据库: {db_path.name} ({db_path.stat().st_size / (1024*1024):.2f} MB)")

    # 4. 压缩封装
    print(f"\n>>> 步骤 3/4: 正在打包封装为 {output_zip.name} ...")
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for src_rel, dest_rel in include_items:
            src_path = PROJECT_ROOT / src_rel
            if not src_path.exists():
                continue
            if src_path.is_file():
                zipf.write(src_path, dest_rel)
            elif src_path.is_dir():
                for root, dirs, files in os.walk(src_path):
                    if "__pycache__" in root:
                        continue
                    for f in files:
                        if f.endswith((".pyc", ".DS_Store")):
                            continue
                        f_full = Path(root) / f
                        f_dest = Path(dest_rel) / f_full.relative_to(src_path)
                        zipf.write(f_full, str(f_dest))

    zip_mb = output_zip.stat().st_size / (1024 * 1024)
    print("\n==========================================================")
    print(f" [√] Windows 专属离线安装包制作完成！")
    print(f" 生成文件: {output_zip.resolve()}")
    print(f" 文件体积: {zip_mb:.2f} MB")
    print(" 交付说明:")
    print(" 1. 将此压缩包拷贝至涉密 Windows 电脑解压。")
    print(" 2. 双击运行 install_offline.bat 进行零网络本地安装。")
    print(" 3. 双击运行 start_windows.bat 启动服务并自动打开大屏。")
    print(" 4. 如需现场导数，将 CSV 文件放入 data\\csv_sources 并双击 import_csv.bat。")
    print("==========================================================")

if __name__ == "__main__":
    main()
