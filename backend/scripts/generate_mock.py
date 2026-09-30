#!/usr/bin/env python3
"""
高仿真政务脱敏数据生成器 (用于开发与测试)
模拟生成 20 多个 CSV 文件、几十万至上千万条结构化数据。
字段：id, 姓名, 性别, 年龄, 居住城市, 详细地址, 外文性别, 外文名字, 年收入
"""

import os
import sys
import random
import argparse
import time
from pathlib import Path

# 常用姓氏与名
SURNAMES = ["王", "李", "张", "刘", "陈", "杨", "赵", "黄", "周", "吴", 
            "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗", 
            "梁", "宋", "郑", "谢", "韩", "唐", "冯", "于", "董", "萧"]

MALE_NAMES = ["伟", "强", "勇", "军", "峰", "磊", "洋", "斌", "亮", "明", 
              "超", "辉", "波", "刚", "涛", "鹏", "杰", "浩", "宇", "鑫",
              "建华", "志强", "文斌", "俊杰", "子轩", "浩然", "海涛", "永健"]

FEMALE_NAMES = ["芳", "娜", "敏", "静", "秀英", "丽", "艳", "娟", "萍", "莉",
                "丹", "萍", "淑芬", "玲", "玉兰", "婷", "洁", "慧", "巧", "琳",
                "雨婷", "梓涵", "雅静", "梦婷", "思琪", "晓彤", "诗涵", "雪梅"]

FIRST_NAMES_EN = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
                  "Thomas", "Charles", "Daniel", "Matthew", "Anthony", "Donald", "Mark", "Paul",
                  "Steven", "Andrew", "Kenneth", "Joshua", "Kevin", "Brian", "George", "Edward",
                  "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica",
                  "Sarah", "Karen", "Nancy", "Lisa", "Betty", "Margaret", "Sandra", "Ashley",
                  "Kimberly", "Emily", "Donna", "Michelle", "Dorothy", "Carol", "Amanda", "Melissa"]

CITIES = [
    "北京市", "上海市", "广州市", "深圳市", "成都市", 
    "杭州市", "武汉市", "西安市", "南京市", "重庆市", 
    "苏州市", "天津市", "长沙市", "青岛市", "郑州市",
    "宁波市", "合肥市", "福州市", "厦门市", "济南市"
]

DISTRICTS = {
    "北京市": ["海淀区", "朝阳区", "西城区", "东城区", "丰台区", "昌平区"],
    "上海市": ["浦东新区", "黄浦区", "徐汇区", "静安区", "长宁区", "杨浦区"],
    "广州市": ["天河区", "越秀区", "海珠区", "白云区", "番禺区"],
    "深圳市": ["南山区", "福田区", "罗湖区", "宝安区", "龙岗区"],
    "成都市": ["武侯区", "锦江区", "青羊区", "金牛区", "高新区"],
    "杭州市": ["西湖区", "滨江区", "拱墅区", "上城区", "余杭区"]
}

DEFAULT_DISTRICTS = ["开发区", "高新区", "新城区", "中心区", "工业园区"]

ROADS = ["中关村南大街", "人民南路", "建设大道", "南京西路", "深南大道", "天府大道", "和平西路", "解放路", "迎宾路", "学府路"]
COMMUNITIES = ["锦绣花园", "学府嘉园", "科技新苑", "博雅名轩", "智谷家园", "金地国际", "阳光水岸", "华府名都", "碧桂园", "绿城百合"]

def generate_id(index: int, birth_year: int) -> str:
    # 模拟 18 位身份证编号格式：地区(6位) + 出生年(4位)月(2位)日(2位) + 顺序码(3位) + 校验码(1位)
    prefix = 110101 + (index % 500) * 10
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    seq = random.randint(100, 999)
    check = random.choice("0123456789X")
    return f"{prefix:06d}{birth_year:04d}{month:02d}{day:02d}{seq:03d}{check}"

def generate_record(index: int):
    is_male = random.random() < 0.52
    gender_cn = "男" if is_male else "女"
    gender_en = "Male" if is_male else "Female"

    surname = random.choice(SURNAMES)
    first_name_cn = random.choice(MALE_NAMES) if is_male else random.choice(FEMALE_NAMES)
    name_cn = f"{surname}{first_name_cn}"

    first_name_en = random.choice(FIRST_NAMES_EN)
    # 简单外文拼音姓氏
    name_en = f"{first_name_en} {surname}"

    # 年龄分布：偏向 20-65 岁
    age = int(random.gauss(38, 14))
    age = max(18, min(88, age))
    birth_year = 2026 - age

    record_id = generate_id(index, birth_year)
    city = random.choice(CITIES)
    districts = DISTRICTS.get(city, DEFAULT_DISTRICTS)
    district = random.choice(districts)
    road = random.choice(ROADS)
    num = random.randint(1, 999)
    community = random.choice(COMMUNITIES)
    room = f"{random.randint(1, 32)}号楼{random.randint(1, 4)}单元{random.randint(101, 2802)}室"
    address = f"{district}{road}{num}号{community}{room}"

    # 年收入分布 (单位：元)，对数正态分布偏向中低收入，少部分高收入
    income_base = random.lognormvariate(11.5, 0.65) # 均值约 10w~15w 之间
    annual_income = round(max(24000.0, min(3500000.0, income_base)), 2)

    return (record_id, name_cn, gender_cn, age, city, address, gender_en, name_en, annual_income)

def main():
    parser = argparse.ArgumentParser(description="生成高仿真测试 CSV 数据集")
    parser.add_argument("--total", type=int, default=200000, help="生成总数据条数 (默认: 200,000)")
    parser.add_argument("--num-files", type=int, default=20, help="切分的 CSV 文件数量 (默认: 20)")
    parser.add_argument("--output-dir", type=str, default="data/csv_sources", help="输出目录")
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows_per_file = args.total // args.num_files
    remainder = args.total % args.num_files

    print(f"=== 开始生成测试数据 ===")
    print(f"总记录数: {args.total:,} 条 | 文件数量: {args.num_files} 个 | 输出目录: {out_dir.resolve()}")
    start_time = time.time()

    current_id_idx = 1
    for file_idx in range(1, args.num_files + 1):
        num_rows = rows_per_file + (1 if file_idx <= remainder else 0)
        file_path = out_dir / f"demo_data_part_{file_idx:02d}.csv"
        
        # 头部字段
        header = "id,姓名,性别,年龄,居住城市,详细地址,外文性别,外文名字,年收入\n"
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(header)
            lines = []
            for _ in range(num_rows):
                rec = generate_record(current_id_idx)
                current_id_idx += 1
                lines.append(f"{rec[0]},{rec[1]},{rec[2]},{rec[3]},{rec[4]},{rec[5]},{rec[6]},{rec[7]},{rec[8]}\n")
                if len(lines) >= 10000:
                    f.writelines(lines)
                    lines.clear()
            if lines:
                f.writelines(lines)
                lines.clear()

        print(f"  [√] 已生成文件 {file_idx:02d}/{args.num_files}: {file_path.name} ({num_rows:,} 行)")

    elapsed = time.time() - start_time
    print(f"=== 生成完成！共耗时 {elapsed:.2f} 秒，总生成 {args.total:,} 条数据 ===")

if __name__ == "__main__":
    main()
