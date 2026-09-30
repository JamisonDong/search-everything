import json
import time
from datetime import datetime
from typing import Dict, Any, List
from backend.app.core.config import settings

class AuditService:
    @staticmethod
    def log_event(action: str, operator: str, details: Dict[str, Any], client_ip: str = "127.0.0.1"):
        """
        记录安全审计日志
        action: SEARCH, VIEW_DETAIL, EXPORT_ATTEMPT, LOGIN
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "operator": operator or settings.DEFAULT_OPERATOR,
            "terminal_id": settings.TERMINAL_ID,
            "client_ip": client_ip,
            "action": action,
            "details": details
        }
        
        try:
            with open(settings.AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"[!] 审计日志记录失败: {e}")

    @staticmethod
    def get_recent_logs(limit: int = 50) -> List[Dict[str, Any]]:
        """获取最近的审计记录"""
        if not settings.AUDIT_LOG_FILE.exists():
            return []
            
        logs = []
        try:
            with open(settings.AUDIT_LOG_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            logs.append(json.loads(line))
                        except Exception:
                            continue
            # 返回最新的 limit 条
            return logs[-limit:][::-1]
        except Exception as e:
            print(f"[!] 读取审计日志失败: {e}")
            return []
