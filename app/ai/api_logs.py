"""API Logs: ghi và đọc nhật ký phiên AI (yêu cầu, code, kết quả, giải thích).
Lưu dạng JSON lines tại logs/ai_sessions.jsonl."""
import json
from datetime import datetime

from lib import config

LOG_FILE = config.ROOT / "logs" / "ai_sessions.jsonl"


def log(record: dict) -> dict:
    """Ghi một bản ghi (kèm timestamp) vào nhật ký. Trả về bản ghi đã ghi."""
    record = {"time": datetime.now().isoformat(timespec="seconds"), **record}
    LOG_FILE.parent.mkdir(exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
    return record


def read_all() -> list:
    """Đọc toàn bộ nhật ký, mới nhất ở cuối."""
    if not LOG_FILE.exists():
        return []
    with open(LOG_FILE, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]
