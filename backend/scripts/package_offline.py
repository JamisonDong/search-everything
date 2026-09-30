#!/usr/bin/env python3
"""
人员数据态势分析大屏 - 纯断网物理隔离离线分发包打包脚本
在有外网连接的开发机/打包机上运行。
自动编译前端静态产物、全量下载 Python 离线 Wheel 包，并生成一键离线部署压缩包。
"""

import os
import sys
import shutil
import subprocess
import zipfile
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

def run_cmd(cmd, cwd=PROJECT_ROOT):
    print(f"[*] 执行指令: {cmd}")
    res = subprocess.run(cmd, shell=True, cwd=cwd)
    if res.returncode != 0:
        print(f"[!] 指令失败，退出码: {res.returncode}")
        sys.exit(res.returncode)

def write_zip_entry(zipf: zipfile.ZipFile, src: Path, arcname: str):
    """写入压缩包；Windows 脚本统一转为 CRLF 换行 (LF 换行的 .bat 在 cmd 中 goto 跳转可能找不到标签)"""
    if src.suffix.lower() in (".bat", ".ps1"):
        data = src.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
        zipf.writestr(str(arcname), data, compress_type=zipfile.ZIP_DEFLATED)
    else:
        zipf.write(src, arcname)

def main():
    parser = argparse.ArgumentParser(description="纯离线部署分发包制作工具")
    parser.add_argument("--output", type=str, default="personnel_dashboard_offline_release.zip", help="输出压缩包文件名")
    parser.add_argument("--include-db", action="store_true", help="是否包含已生成的本地数据库文件 (data/personnel.duckdb)")
    args = parser.parse_args()

    print("==========================================================")
    print("    人员数据态势分析大屏 - 纯断网离线部署分发包制作开始          ")
    print("==========================================================")

    # 1. 编译前端静态资源
    dist_dir = PROJECT_ROOT / "frontend" / "dist"
    print("\n>>> 步骤 1/4: 检查并编译前端工程 (生产模式)...")
    if not (dist_dir / "index.html").exists():
        print("[*] 正在编译前端...")
        run_cmd("npm run build", cwd=PROJECT_ROOT / "frontend")
    else:
        print("[√] 前端已存在构建产物 (frontend/dist)，确认就绪。")

    # 2. 下载全量 Python 离线 Wheel 依赖包
    wheels_dir = PROJECT_ROOT / "offline_wheels"
    wheels_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n>>> 步骤 2/4: 下载后端离线 Wheel 依赖包至 {wheels_dir.name}/ ...")
    pip_cmd = f"{sys.executable} -m pip download -r backend/requirements.txt --dest offline_wheels/"
    run_cmd(pip_cmd)
    wheel_count = len(list(wheels_dir.glob("*.whl")))
    print(f"[√] 离线 Wheel 下载完成，共计 {wheel_count} 个依赖包。")

    # 3. 准备打包文件列表
    print("\n>>> 步骤 3/4: 准备打包文件树...")
    output_zip_path = PROJECT_ROOT / args.output
    if output_zip_path.exists():
        output_zip_path.unlink()

    # 要包含的文件和目录
    include_paths = [
        "backend",
        "frontend/dist",
        "offline_wheels",
        "start_mac.sh",
        "start_windows.bat",
        "setup_windows.bat",
        "import_csv.bat",
        "install_offline.sh",
        "install_offline.bat",
        "README.md",
        ".gitignore"
    ]

    if args.include_db:
        db_file = PROJECT_ROOT / "data" / "personnel.duckdb"
        if db_file.exists():
            include_paths.append("data/personnel.duckdb")
            print(f"[*] 已选择包含预生成数据库文件 (大小: {db_file.stat().st_size / (1024*1024):.2f} MB)")
        else:
            print("[!] 未找到 data/personnel.duckdb，跳过包含。")

    # 4. 创建 ZIP 压缩包
    print(f"\n>>> 步骤 4/4: 正在压缩并封装为离线介质包 {output_zip_path.name} ...")
    with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for item in include_paths:
            p = PROJECT_ROOT / item
            if not p.exists():
                continue
            if p.is_file():
                write_zip_entry(zipf, p, str(p.relative_to(PROJECT_ROOT)))
            elif p.is_dir():
                for root, dirs, files in os.walk(p):
                    # 排除 pycache 等
                    if "__pycache__" in root:
                        continue
                    for f in files:
                        if f.endswith((".pyc", ".DS_Store")):
                            continue
                        full_path = Path(root) / f
                        write_zip_entry(zipf, full_path, str(full_path.relative_to(PROJECT_ROOT)))

    zip_size_mb = output_zip_path.stat().st_size / (1024 * 1024)
    print(f"\n==========================================================")
    print(f" [√] 纯断网离线安装包制作完成！")
    print(f" 文件位置: {output_zip_path.resolve()}")
    print(f" 文件大小: {zip_size_mb:.2f} MB")
    print(f" 使用方法: 将该压缩包刻录光盘或通过专渡U盘拷贝至断网目标机即可。")
    print(f"==========================================================")

if __name__ == "__main__":
    main()
