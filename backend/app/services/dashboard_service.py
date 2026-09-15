import time
from typing import Dict, Any, List
import duckdb

class DashboardService:
    @staticmethod
    def get_kpi_summary(con: duckdb.DuckDBPyConnection) -> Dict[str, Any]:
        """获取大屏顶部核心指标看板"""
        t0 = time.time()
        query = """
        SELECT 
            COUNT(*) AS total_count,
            COUNT(DISTINCT city) AS total_cities,
            ROUND(COALESCE(AVG(age), 0), 1) AS avg_age,
            ROUND(COALESCE(AVG(annual_income), 0), 2) AS avg_income,
            ROUND(COALESCE(MEDIAN(annual_income), 0), 2) AS median_income,
            COUNT(CASE WHEN gender = '男' THEN 1 END) AS male_count,
            COUNT(CASE WHEN gender = '女' THEN 1 END) AS female_count
        FROM personnel;
        """
        row = con.execute(query).fetchone()
        
        total = row[0] if row else 0
        male = row[5] if row else 0
        female = row[6] if row else 0

        return {
            "total_count": total,
            "total_cities": row[1] if row else 0,
            "avg_age": row[2] if row else 0,
            "avg_income": row[3] if row else 0,
            "median_income": row[4] if row else 0,
            "male_count": male,
            "female_count": female,
            "male_ratio": round(male / total * 100, 1) if total > 0 else 0,
            "female_ratio": round(female / total * 100, 1) if total > 0 else 0,
            "query_cost_ms": round((time.time() - t0) * 1000, 2)
        }

    @staticmethod
    def get_city_distribution(con: duckdb.DuckDBPyConnection, limit: int = 12) -> List[Dict[str, Any]]:
        """获取城市人员分布排行榜"""
        query = f"""
        SELECT 
            COALESCE(city, '未知城市') AS city,
            COUNT(*) AS count,
            ROUND(AVG(annual_income), 1) AS avg_income
        FROM personnel
        GROUP BY city
        ORDER BY count DESC
        LIMIT {limit};
        """
        rows = con.execute(query).fetchall()
        return [{"city": r[0], "count": r[1], "avg_income": r[2]} for r in rows]

    @staticmethod
    def get_age_pyramid(con: duckdb.DuckDBPyConnection) -> List[Dict[str, Any]]:
        """获取年龄段与性别交叉分布"""
        query = """
        SELECT 
            CASE 
                WHEN age < 25 THEN '18-24岁'
                WHEN age < 35 THEN '25-34岁'
                WHEN age < 45 THEN '35-44岁'
                WHEN age < 55 THEN '45-54岁'
                WHEN age < 65 THEN '55-64岁'
                ELSE '65岁及以上'
            END AS age_group,
            COUNT(CASE WHEN gender = '男' THEN 1 END) AS male_count,
            COUNT(CASE WHEN gender = '女' THEN 1 END) AS female_count,
            COUNT(*) AS total_count
        FROM personnel
        WHERE age IS NOT NULL
        GROUP BY age_group
        ORDER BY 
            CASE age_group
                WHEN '18-24岁' THEN 1
                WHEN '25-34岁' THEN 2
                WHEN '35-44岁' THEN 3
                WHEN '45-54岁' THEN 4
                WHEN '55-64岁' THEN 5
                ELSE 6
            END;
        """
        rows = con.execute(query).fetchall()
        return [
            {
                "age_group": r[0],
                "male": r[1],
                "female": r[2],
                "total": r[3]
            } for r in rows
        ]

    @staticmethod
    def get_income_brackets(con: duckdb.DuckDBPyConnection) -> List[Dict[str, Any]]:
        """获取年收入阶梯分段分布"""
        query = """
        SELECT 
            CASE 
                WHEN annual_income < 60000 THEN '6万以下'
                WHEN annual_income < 120000 THEN '6-12万'
                WHEN annual_income < 250000 THEN '12-25万'
                WHEN annual_income < 500000 THEN '25-50万'
                WHEN annual_income < 1000000 THEN '50-100万'
                ELSE '100万以上'
            END AS income_bracket,
            COUNT(*) AS count
        FROM personnel
        WHERE annual_income IS NOT NULL
        GROUP BY income_bracket
        ORDER BY 
            CASE income_bracket
                WHEN '6万以下' THEN 1
                WHEN '6-12万' THEN 2
                WHEN '12-25万' THEN 3
                WHEN '25-50万' THEN 4
                WHEN '50-100万' THEN 5
                ELSE 6
            END;
        """
        rows = con.execute(query).fetchall()
        return [{"bracket": r[0], "count": r[1]} for r in rows]

    @staticmethod
    def get_all_dashboard_data(con: duckdb.DuckDBPyConnection) -> Dict[str, Any]:
        """合并返回全套大屏可视化统计数据"""
        t0 = time.time()
        kpi = DashboardService.get_kpi_summary(con)
        cities = DashboardService.get_city_distribution(con)
        age_pyramid = DashboardService.get_age_pyramid(con)
        incomes = DashboardService.get_income_brackets(con)
        
        return {
            "kpi": kpi,
            "city_distribution": cities,
            "age_pyramid": age_pyramid,
            "income_distribution": incomes,
            "total_execution_ms": round((time.time() - t0) * 1000, 2)
        }
