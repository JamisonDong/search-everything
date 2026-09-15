import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = BASE_DIR.parent

class Settings(BaseModel):
    PROJECT_NAME: str = "学城私有数据智能检索大屏系统"
    VERSION: str = "1.0.0"
    SECURITY_LEVEL: str = "涉密专机 · 严禁外联"
    
    # 路径配置
    DB_PATH: Path = PROJECT_ROOT / "data" / "xuecheng.duckdb"
    CSV_DIR: Path = PROJECT_ROOT / "data" / "csv_sources"
    LOG_DIR: Path = PROJECT_ROOT / "logs"
    AUDIT_LOG_FILE: Path = PROJECT_ROOT / "logs" / "audit_log.jsonl"
    
    # 运行配置
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # 默认操作员标识 (涉密水印用)
    DEFAULT_OPERATOR: str = "涉密操作员-01"
    TERMINAL_ID: str = "SEC-TERM-LOCAL"

settings = Settings()

# 确保目录存在
settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
settings.CSV_DIR.mkdir(parents=True, exist_ok=True)
