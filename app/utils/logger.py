import hashlib
import logging
from datetime import datetime
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("pharmvector")


def hash_user_id(user_id: int) -> str:
    return hashlib.sha256(str(user_id).encode()).hexdigest()


def log_user_action(user_id: int, action: str, details: Optional[dict] = None):
    hashed_id = hash_user_id(user_id)
    timestamp = datetime.utcnow().isoformat()
    log_message = f"UserAction | HashedID: {hashed_id} | Timestamp: {timestamp} | Action: {action}"
    if details:
        log_message += f" | Details: {details}"
    logger.info(log_message)
