import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def backup_sqlite():
    db_path_str = settings.DATABASE_URL.replace("sqlite:///", "")
    db_path = Path(db_path_str)

    if not db_path.exists():
        logger.error(f"Database file at {db_path} does not exist. Run seed/app first.")
        return

    backup_dir = Path("./data/backups")
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"app_backup_{timestamp}.db"

    logger.info(f"Initiating online SQLite backup from {db_path} to {backup_file}...")

    src_conn = sqlite3.connect(db_path)
    dst_conn = sqlite3.connect(backup_file)

    try:
        with dst_conn:
            src_conn.backup(dst_conn, pages=100, progress=None)
        logger.info(f"SQLite online backup completed successfully: {backup_file}")
    except Exception as e:
        logger.error(f"SQLite backup failed: {e}")
        raise
    finally:
        dst_conn.close()
        src_conn.close()

if __name__ == "__main__":
    backup_sqlite()
