import time
import re
from typing import Dict, Any, List, Optional
import duckdb

def mask_text(name: str, id_card: str, address: str, income: float) -> Dict[str, Any]:
    """涉密数据动态脱敏处理"""
    # 姓名脱敏
    if not name:
        masked_name = ""
    elif len(name) <= 2:
        masked_name = name[0] + "*"
    else:
        masked_name = name[0] + "*" * (len(name) - 2) + name[-1]

    # 身份证脱敏：前6后4，中间打码
    if id_card and len(id_card) >= 10:
        masked_id = id_card[:6] + "********" + id_card[-4:]
    else:
        masked_id = "********"

    # 地址脱敏：保留省市县区前缀，门牌号社区打码
    if address and len(address) > 6:
        masked_address = address[:6] + "*******"
    else:
        masked_address = "***"

    # 收入脱敏
    masked_income = "保密 (已脱敏)"

    return {
        "name": masked_name,
        "id": masked_id,
        "address": masked_address,
        "income_display": masked_income
    }

class SearchService:
    @staticmethod
    def search_personnel(
        con: duckdb.DuckDBPyConnection,
        keyword: Optional[str] = None,
        city: Optional[str] = None,
        gender: Optional[str] = None,
        min_age: Optional[int] = None,
        max_age: Optional[int] = None,
        min_income: Optional[float] = None,
        max_income: Optional[float] = None,
        page: int = 1,
        page_size: int = 20,
        order_by: str = "annual_income",
        order_dir: str = "desc",
        mask_sensitive: bool = False
    ) -> Dict[str, Any]:
        """
        多维复合高性能检索
        """
        t0 = time.time()
        conditions = ["1=1"]
        params = []

        if keyword:
            kw = keyword.strip()
            # 关键字转义
            kw_clean = kw.replace("'", "''")
            # 匹配 姓名、外文姓名、证件号、详细地址
            conditions.append(f"""(
                name ILIKE '%{kw_clean}%' OR 
                foreign_name ILIKE '%{kw_clean}%' OR 
                id LIKE '%{kw_clean}%' OR 
                address ILIKE '%{kw_clean}%'
            )""")

        if city and city.strip():
            city_clean = city.strip().replace("'", "''")
            conditions.append(f"city = '{city_clean}'")

        if gender and gender.strip() and gender in ["男", "女"]:
            conditions.append(f"gender = '{gender.strip()}'")

        if min_age is not None:
            conditions.append(f"age >= {int(min_age)}")

        if max_age is not None:
            conditions.append(f"age <= {int(max_age)}")

        if min_income is not None:
            conditions.append(f"annual_income >= {float(min_income)}")

        if max_income is not None:
            conditions.append(f"annual_income <= {float(max_income)}")

        where_clause = " AND ".join(conditions)

        # 排序安全白名单
        valid_sort_cols = {"id": "id", "age": "age", "annual_income": "annual_income", "name": "name"}
        sort_col = valid_sort_cols.get(order_by, "annual_income")
        sort_direction = "DESC" if order_dir.lower() == "desc" else "ASC"

        # 统计符合条件的记录总数
        count_sql = f"SELECT COUNT(*) FROM personnel WHERE {where_clause};"
        total_count = con.execute(count_sql).fetchone()[0]

        # 分页查询
        page = max(1, page)
        page_size = min(100, max(5, page_size))
        offset = (page - 1) * page_size

        query_sql = f"""
        SELECT 
            id, name, gender, age, city, address, foreign_gender, foreign_name, annual_income
        FROM personnel
        WHERE {where_clause}
        ORDER BY {sort_col} {sort_direction} NULLS LAST
        LIMIT {page_size} OFFSET {offset};
        """
        rows = con.execute(query_sql).fetchall()

        items = []
        for r in rows:
            rec_id, name, r_gender, age, r_city, address, f_gender, f_name, income = r
            
            if mask_sensitive:
                masked = mask_text(name, rec_id, address, income)
                items.append({
                    "id": masked["id"],
                    "raw_id": rec_id if not mask_sensitive else None,
                    "name": masked["name"],
                    "gender": r_gender,
                    "age": age,
                    "city": r_city,
                    "address": masked["address"],
                    "foreign_gender": f_gender,
                    "foreign_name": f_name[0] + "***" if f_name else "",
                    "annual_income": None,
                    "income_display": masked["income_display"]
                })
            else:
                items.append({
                    "id": rec_id,
                    "name": name,
                    "gender": r_gender,
                    "age": age,
                    "city": r_city,
                    "address": address,
                    "foreign_gender": f_gender,
                    "foreign_name": f_name,
                    "annual_income": income,
                    "income_display": f"¥ {income:,.2f}" if income is not None else "暂无"
                })

        query_cost = round((time.time() - t0) * 1000, 2)

        return {
            "total": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size if total_count > 0 else 0,
            "query_cost_ms": query_cost,
            "items": items
        }

    @staticmethod
    def get_personnel_detail(con: duckdb.DuckDBPyConnection, person_id: str, mask_sensitive: bool = False) -> Optional[Dict[str, Any]]:
        """获取个人详细档案画像"""
        clean_id = person_id.strip().replace("'", "''")
        row = con.execute(f"""
        SELECT 
            id, name, gender, age, city, address, foreign_gender, foreign_name, annual_income
        FROM personnel
        WHERE id = '{clean_id}'
        LIMIT 1;
        """).fetchone()

        if not row:
            return None

        rec_id, name, r_gender, age, r_city, address, f_gender, f_name, income = row
        if mask_sensitive:
            masked = mask_text(name, rec_id, address, income)
            return {
                "id": masked["id"],
                "name": masked["name"],
                "gender": r_gender,
                "age": age,
                "city": r_city,
                "address": masked["address"],
                "foreign_gender": f_gender,
                "foreign_name": f_name[0] + "***" if f_name else "",
                "annual_income": None,
                "income_display": masked["income_display"],
                "is_masked": True
            }

        return {
            "id": rec_id,
            "name": name,
            "gender": r_gender,
            "age": age,
            "city": r_city,
            "address": address,
            "foreign_gender": f_gender,
            "foreign_name": f_name,
            "annual_income": income,
            "income_display": f"¥ {income:,.2f}" if income is not None else "暂无",
            "is_masked": False
        }
