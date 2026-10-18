"""
Backup and Restore Service
Provides local point-in-time snapshots of the database and verified restoration.
"""

import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from backend.config import DATA_DIR, BACKUPS_DIR

DB_PATH = DATA_DIR / "cpgrams_workbench.db"

def create_backup() -> Dict[str, Any]:
    """Creates a timestamped snapshot of the SQLite database."""
    if not DB_PATH.exists():
        raise FileNotFoundError("Database file does not exist.")

    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"cpgrams_backup_{timestamp_str}.db"
    backup_path = BACKUPS_DIR / backup_filename

    # Safe SQLite online backup
    src = sqlite3.connect(str(DB_PATH))
    dst = sqlite3.connect(str(backup_path))
    with dst:
        src.backup(dst)
    dst.close()
    src.close()

    file_size_kb = round(os.path.getsize(str(backup_path)) / 1024, 2)
    return {
        "filename": backup_filename,
        "path": str(backup_path),
        "size_kb": file_size_kb,
        "created_at": datetime.now().isoformat()
    }

def list_backups() -> List[Dict[str, Any]]:
    """Lists all available local database backups."""
    backups = []
    for f in sorted(BACKUPS_DIR.glob("*.db"), key=os.path.getmtime, reverse=True):
        stat = f.stat()
        backups.append({
            "filename": f.name,
            "path": str(f),
            "size_kb": round(stat.st_size / 1024, 2),
            "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
        })
    return backups

def restore_backup(backup_filename: str) -> Dict[str, Any]:
    """
    Restores the database from a verified backup snapshot.
    Performs integrity check on backup before replacing active database.
    """
    backup_path = BACKUPS_DIR / backup_filename
    if not backup_path.exists():
        raise FileNotFoundError(f"Backup file '{backup_filename}' not found.")

    # 1. Verify integrity of the backup file
    conn = sqlite3.connect(str(backup_path))
    cursor = conn.cursor()
    cursor.execute("PRAGMA integrity_check;")
    result = cursor.fetchone()
    conn.close()

    if not result or result[0] != "ok":
        raise ValueError(f"Backup file failed integrity check: {result}")

    # 2. Safety copy of current database before restore
    safety_copy = BACKUPS_DIR / f"pre_restore_safety_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    if DB_PATH.exists():
        shutil.copy2(str(DB_PATH), str(safety_copy))

    # 3. Perform restoration
    src = sqlite3.connect(str(backup_path))
    dst = sqlite3.connect(str(DB_PATH))
    with dst:
        src.backup(dst)
    dst.close()
    src.close()

    return {
        "restored_from": backup_filename,
        "safety_snapshot": safety_copy.name,
        "status": "success",
        "timestamp": datetime.now().isoformat()
    }
