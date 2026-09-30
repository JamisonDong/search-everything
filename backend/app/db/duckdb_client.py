import duckdb
from typing import Generator
from backend.app.core.config import settings

def get_db_connection() -> duckdb.DuckDBPyConnection:
    """
    获取 DuckDB 只读只查连接
    只读模式可支持高并发无锁并发查询，保障底层数据不被非法变更
    """
    if not settings.DB_PATH.exists():
        # 如果数据库尚未生成，创建连接并初始化基础结构
        con = duckdb.connect(str(settings.DB_PATH))
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
        return con
    return duckdb.connect(str(settings.DB_PATH), read_only=True)

def get_db() -> Generator[duckdb.DuckDBPyConnection, None, None]:
    """FastAPI 依赖注入连接器"""
    con = get_db_connection()
    try:
        yield con
    finally:
        con.close()
