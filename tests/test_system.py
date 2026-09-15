import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from starlette.testclient import TestClient
from backend.main import app
from backend.app.core.config import settings

def test_full_system():
    client = TestClient(app)

    print("1. 测试前端离线静态页面挂载...")
    res = client.get("/")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert "学城人员综合数据智能检索与态势分析大屏" in res.text or "<!DOCTYPE html>" in res.text
    print("   [√] 前端单机离线静态首页正常交付！")

    print("2. 测试大屏聚合统计 API (/api/dashboard/stats)...")
    res = client.get("/api/dashboard/stats")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    data = res.json()
    assert "kpi" in data
    assert "city_distribution" in data
    assert "age_pyramid" in data
    assert "income_distribution" in data
    print(f"   [√] 成功获取统计指标！总人数: {data['kpi']['total_count']:,} 条，聚合耗时: {data['total_execution_ms']} ms")

    print("3. 测试多维条件复合检索 API (/api/search)...")
    res = client.get("/api/search?keyword=张&city=北京市&page=1&page_size=10")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    search_data = res.json()
    print(f"   [√] 检索条件 '张'+'北京市' 命中: {search_data['total']:,} 条，检索耗时: {search_data['query_cost_ms']} ms")
    assert len(search_data["items"]) <= 10

    if search_data["items"]:
        first_person = search_data["items"][0]
        person_id = first_person["id"]
        print(f"4. 测试单人全景档案调阅 API (/api/personnel/{person_id})...")
        res = client.get(f"/api/personnel/{person_id}")
        assert res.status_code == 200
        detail = res.json()
        assert detail["id"] == person_id
        print(f"   [√] 档案调阅成功: {detail['name']} ({detail['gender']}, {detail['age']}岁, {detail['city']})")

    print("5. 测试涉密安全审计记录 API (/api/audit/logs)...")
    res = client.get("/api/audit/logs")
    assert res.status_code == 200
    logs = res.json()
    assert len(logs) > 0, "Audit logs should not be empty after search"
    print(f"   [√] 安全审计日志生效！已留存 {len(logs)} 条涉密操作轨迹，最新行为: {logs[0]['action']}")

    print("6. 测试脱敏模式 (/api/search?mask_sensitive=true)...")
    res = client.get("/api/search?keyword=李&mask_sensitive=true&page=1&page_size=5")
    assert res.status_code == 200
    masked_data = res.json()
    for item in masked_data["items"]:
        assert "*" in item["id"], "ID must be masked"
        assert "*" in item["name"], "Name must be masked"
    print("   [√] 数据脱敏模式验证通过（姓名与身份证均包含掩码打码）！")

    print("\n==========================================")
    print(" 全链路系统自动化测试 100% 全部通过！")
    print("==========================================")

if __name__ == "__main__":
    test_full_system()
