from fastapi import APIRouter, Depends, Query, HTTPException, Request
from typing import Optional, List
import duckdb
import os
import time
from pathlib import Path

from backend.app.db.duckdb_client import get_db
from backend.app.services.dashboard_service import DashboardService
from backend.app.services.search_service import SearchService
from backend.app.services.audit_service import AuditService
from backend.app.core.config import settings

router = APIRouter()

@router.get("/dashboard/stats")
def get_dashboard_stats(db: duckdb.DuckDBPyConnection = Depends(get_db)):
    """获取大屏全量统计指标 (秒级聚合)"""
    return DashboardService.get_all_dashboard_data(db)

@router.get("/search")
def search_personnel(
    request: Request,
    keyword: Optional[str] = Query(None, description="搜索关键词(姓名/外文名/证件/地址)"),
    city: Optional[str] = Query(None, description="居住城市"),
    gender: Optional[str] = Query(None, description="性别(男/女)"),
    min_age: Optional[int] = Query(None, description="最小年龄"),
    max_age: Optional[int] = Query(None, description="最大年龄"),
    min_income: Optional[float] = Query(None, description="最低年收入"),
    max_income: Optional[float] = Query(None, description="最高年收入"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=5, le=100, description="每页条数"),
    order_by: str = Query("annual_income", description="排序字段 (annual_income, age, id, name)"),
    order_dir: str = Query("desc", description="排序方向 (desc, asc)"),
    mask_sensitive: bool = Query(False, description="是否开启脱敏模式"),
    operator: Optional[str] = Query(None, description="操作员标识"),
    db: duckdb.DuckDBPyConnection = Depends(get_db)
):
    """多维条件复合检索"""
    results = SearchService.search_personnel(
        con=db,
        keyword=keyword,
        city=city,
        gender=gender,
        min_age=min_age,
        max_age=max_age,
        min_income=min_income,
        max_income=max_income,
        page=page,
        page_size=page_size,
        order_by=order_by,
        order_dir=order_dir,
        mask_sensitive=mask_sensitive
    )

    # 记录安全审计日志
    client_ip = request.client.host if request.client else "127.0.0.1"
    AuditService.log_event(
        action="SEARCH",
        operator=operator or settings.DEFAULT_OPERATOR,
        details={
            "keyword": keyword,
            "city": city,
            "gender": gender,
            "age_range": [min_age, max_age],
            "income_range": [min_income, max_income],
            "page": page,
            "total_hits": results["total"],
            "query_cost_ms": results["query_cost_ms"],
            "mask_sensitive": mask_sensitive
        },
        client_ip=client_ip
    )

    return results

@router.get("/personnel/{person_id}")
def get_personnel_detail(
    person_id: str,
    request: Request,
    mask_sensitive: bool = Query(False, description="是否脱敏"),
    operator: Optional[str] = Query(None, description="操作员标识"),
    db: duckdb.DuckDBPyConnection = Depends(get_db)
):
    """获取单个人员详细全景档案"""
    detail = SearchService.get_personnel_detail(db, person_id, mask_sensitive=mask_sensitive)
    if not detail:
        raise HTTPException(status_code=404, detail="未找到该人员档案")

    client_ip = request.client.host if request.client else "127.0.0.1"
    AuditService.log_event(
        action="VIEW_DETAIL",
        operator=operator or settings.DEFAULT_OPERATOR,
        details={
            "person_id": person_id,
            "mask_sensitive": mask_sensitive
        },
        client_ip=client_ip
    )

    return detail

@router.get("/audit/logs")
def get_audit_logs(limit: int = Query(50, ge=1, le=200)):
    """获取最近安全操作审计日志"""
    return AuditService.get_recent_logs(limit=limit)

@router.get("/system/status")
def get_system_status(db: duckdb.DuckDBPyConnection = Depends(get_db)):
    """获取当前系统与数据文件状态"""
    db_size_mb = 0
    if settings.DB_PATH.exists():
        db_size_mb = round(settings.DB_PATH.stat().st_size / (1024 * 1024), 2)

    total_records = db.execute("SELECT count(*) FROM personnel;").fetchone()[0]

    # 获取最后导入时间
    last_imported = "暂无导入记录"
    try:
        meta = db.execute("SELECT value FROM system_metadata WHERE key = 'last_imported_at';").fetchone()
        if meta:
            last_imported = meta[0]
    except Exception:
        pass

    return {
        "status": "RUNNING",
        "security_level": settings.SECURITY_LEVEL,
        "terminal_id": settings.TERMINAL_ID,
        "database_engine": "DuckDB Embedded Columnar Engine",
        "database_file": str(settings.DB_PATH),
        "database_size_mb": db_size_mb,
        "total_records": total_records,
        "last_imported_at": last_imported,
        "offline_mode": True
    }
