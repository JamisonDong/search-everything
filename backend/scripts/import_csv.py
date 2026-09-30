#!/usr/bin/env python3
"""
人员数据态势分析大屏 - 1600万数据高效清洗与导入脚本 (基于 DuckDB 高性能列存引擎)
支持自动编码探测 (UTF-8 / GBK / GB18030)、多文件并行清洗、字段规范化、去重、索引创建与性能评测。
"""

import os
import sys
import time
import glob
import argparse
from pathlib import Path
import duckdb

def detect_file_encoding(file_path: Path) -> str:
    """快速探测 CSV 文件编码 (UTF-8 或 GB18030/GBK)"""
    with open(file_path, "rb") as f:
        sample = f.read(65536) # 读取前 64KB
    
    # 尝试 UTF-8 (剥离末尾可能被截断的 1~3 个字节)
    for trim in range(4):
        try:
            (sample[:len(sample)-trim] if trim > 0 else sample).decode("utf-8")
            return "utf-8"
        except UnicodeDecodeError:
            continue

    # 尝试 GB18030 / GBK
    for trim in range(4):
        try:
            (sample[:len(sample)-trim] if trim > 0 else sample).decode("gb18030")
            return "gb18030"
        except UnicodeDecodeError:
            continue

    return "utf-8"

def init_database_schema(con: duckdb.DuckDBPyConnection):
    """初始化人员底座表结构与安全审计表"""
    con.execute("""
    CREATE TABLE IF NOT EXISTS personnel (
        id VARCHAR PRIMARY KEY,
        name VARCHAR NOT NULL,
        gender VARCHAR,
        age INTEGER,
        city VARCHAR,
        address VARCHAR,
        foreign_gender VARCHAR,
        foreign_name VARCHAR,
        annual_income DOUBLE
    );
    """)

    con.execute("""
    CREATE TABLE IF NOT EXISTS system_metadata (
        key VARCHAR PRIMARY KEY,
        value VARCHAR,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

def import_csv_files(con: duckdb.DuckDBPyConnection, csv_dir: Path):
    """高效批量导入 CSV 文件"""
    csv_files = sorted(list(csv_dir.glob("*.csv")))
    if not csv_files:
        print(f"[!] 警告: 在目录 {csv_dir} 未找到任何 .csv 文件！")
        return 0

    print(f"=== 发现 {len(csv_files)} 个 CSV 文件，开始分析与导入 ===")
    total_imported = 0
    start_time = time.time()

    # 检查是否全部为 UTF-8 编码，若是，可使用 DuckDB 原生超高速多核并行加载
    encodings = {f: detect_file_encoding(f) for f in csv_files}
    all_utf8 = all(enc == "utf-8" for enc in encodings.values())

    if all_utf8:
        print(f"[*] 所有文件均为标准 UTF-8 编码，启用 DuckDB SIMD 原生多文件并行加载管道...")
        file_paths = [str(f.resolve()) for f in csv_files]
        
        # 创建临时暂存表
        con.execute("DROP TABLE IF EXISTS staging_import;")
        con.execute(f"""
        CREATE TEMPORARY TABLE staging_import AS 
        SELECT 
            TRIM(CAST(id AS VARCHAR)) AS id,
            TRIM(CAST("姓名" AS VARCHAR)) AS name,
            TRIM(CAST("性别" AS VARCHAR)) AS gender,
            TRY_CAST("年龄" AS INTEGER) AS age,
            TRIM(CAST("居住城市" AS VARCHAR)) AS city,
            TRIM(CAST("详细地址" AS VARCHAR)) AS address,
            TRIM(CAST("外文性别" AS VARCHAR)) AS foreign_gender,
            TRIM(CAST("外文名字" AS VARCHAR)) AS foreign_name,
            TRY_CAST(REGEXP_REPLACE(CAST("年收入" AS VARCHAR), '[^0-9.]', '', 'g') AS DOUBLE) AS annual_income
        FROM read_csv_auto({file_paths}, header=True, union_by_name=True);
        """)

        # 排重并写入主表
        print("[*] 正在执行 ID 唯一性排重与入库...")
        con.execute("""
        INSERT OR REPLACE INTO personnel (id, name, gender, age, city, address, foreign_gender, foreign_name, annual_income)
        SELECT id, name, gender, age, city, address, foreign_gender, foreign_name, annual_income
        FROM staging_import
        WHERE id IS NOT NULL AND id != '';
        """)
        con.execute("DROP TABLE IF EXISTS staging_import;")
    else:
        print(f"[*] 检测到混合编码文件 (GBK/GB18030)，采用逐文件自适应探测流式加载...")
        for idx, f in enumerate(csv_files, 1):
            enc = encodings[f]
            t0 = time.time()
            print(f"  -> [{idx}/{len(csv_files)}] 导入 {f.name} (编码: {enc})...", end="", flush=True)
            con.execute(f"""
            INSERT OR REPLACE INTO personnel (id, name, gender, age, city, address, foreign_gender, foreign_name, annual_income)
            SELECT 
                TRIM(CAST(id AS VARCHAR)) AS id,
                TRIM(CAST("姓名" AS VARCHAR)) AS name,
                TRIM(CAST("性别" AS VARCHAR)) AS gender,
                TRY_CAST("年龄" AS INTEGER) AS age,
                TRIM(CAST("居住城市" AS VARCHAR)) AS city,
                TRIM(CAST("详细地址" AS VARCHAR)) AS address,
                TRIM(CAST("外文性别" AS VARCHAR)) AS foreign_gender,
                TRIM(CAST("外文名字" AS VARCHAR)) AS foreign_name,
                TRY_CAST(REGEXP_REPLACE(CAST("年收入" AS VARCHAR), '[^0-9.]', '', 'g') AS DOUBLE) AS annual_income
            FROM read_csv_auto('{f.resolve()}', header=True, encoding='{enc}')
            WHERE id IS NOT NULL AND TRIM(CAST(id AS VARCHAR)) != '';
            """)
            print(f" 完成 ({time.time() - t0:.2f}s)")

    # 统计总数
    res = con.execute("SELECT COUNT(*) FROM personnel;").fetchone()
    total_imported = res[0] if res else 0

    elapsed = time.time() - start_time
    print(f"=== 导入完毕！当前数据库有效总记录数: {total_imported:,} 条，总耗时: {elapsed:.2f} 秒 ===")
    return total_imported

def build_performance_indexes(con: duckdb.DuckDBPyConnection):
    """为高频检索与大屏过滤构建核心 B-Tree 索引"""
    print("=== 开始构建数据库高性能查询索引 ===")
    t0 = time.time()

    indexes = [
        ("idx_personnel_city", "city"),
        ("idx_personnel_gender", "gender"),
        ("idx_personnel_age", "age"),
        ("idx_personnel_income", "annual_income"),
        ("idx_personnel_name", "name"),
        ("idx_personnel_foreign_name", "foreign_name"),
    ]

    for idx_name, column in indexes:
        print(f"  -> 创建索引 {idx_name} on ({column})...", end="", flush=True)
        t_idx = time.time()
        try:
            con.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON personnel ({column});")
            print(f" 完成 ({time.time() - t_idx:.2f}s)")
        except Exception as e:
            print(f" [跳过或已存在: {e}]")

    print(f"=== 索引构建完成！耗时: {time.time() - t0:.2f} 秒 ===")

def main():
    parser = argparse.ArgumentParser(description="人员数据高效导入与索引生成")
    parser.add_argument("--csv-dir", type=str, default="data/csv_sources", help="CSV 存放目录")
    parser.add_argument("--db-path", type=str, default="data/personnel.duckdb", help="DuckDB 数据库文件路径")
    args = parser.parse_args()

    csv_dir = Path(args.csv_dir)
    db_path = Path(args.db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"[*] 数据库路径: {db_path.resolve()}")
    con = duckdb.connect(str(db_path))

    init_database_schema(con)
    import_csv_files(con, csv_dir)
    build_performance_indexes(con)

    # 记录导入元数据
    con.execute("""
    INSERT OR REPLACE INTO system_metadata (key, value) VALUES 
    ('last_imported_at', CURRENT_TIMESTAMP::VARCHAR),
    ('data_version', '1.0');
    """)

    con.close()
    print(f"[√] 数据库准备完毕！文件大小: {db_path.stat().st_size / (1024*1024):.2f} MB")

if __name__ == "__main__":
    main()
