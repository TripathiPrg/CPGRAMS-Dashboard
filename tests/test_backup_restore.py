"""
Automated Test Suite: Database Backup & Verified Restore
Verifies backup snapshot creation, integrity checks, and verified restoration.
"""

import os
import pytest
from backend.services.backup_service import create_backup, list_backups, restore_backup
from backend.database import SessionLocal, init_db
from backend.models import Grievance

def test_backup_and_restore_cycle():
    init_db()
    
    # 1. Create backup
    backup_meta = create_backup()
    assert os.path.exists(backup_meta["path"])
    assert backup_meta["size_kb"] > 0
    assert backup_meta["filename"].startswith("cpgrams_backup_")

    # 2. List backups
    all_backups = list_backups()
    assert len(all_backups) > 0
    assert any(b["filename"] == backup_meta["filename"] for b in all_backups)

    # 3. Restore backup
    res = restore_backup(backup_meta["filename"])
    assert res["status"] == "success"
    assert "pre_restore_safety_" in res["safety_snapshot"]

    # 4. Verify DB remains intact after restore
    db = SessionLocal()
    count = db.query(Grievance).count()
    db.close()
    assert count >= 4
