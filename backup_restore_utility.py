#!/usr/bin/env python3
"""
Backup and Restore Utility
Handles backup and restoration of workflow configurations and data
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import tarfile
import gzip

class BackupManager:
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, workflow_file: str, metadata: Optional[Dict] = None) -> str:
        """Create a backup of workflow configuration"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"workflow_backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        # Create backup directory
        backup_path.mkdir(exist_ok=True)
        
        # Copy workflow file
        if os.path.exists(workflow_file):
            shutil.copy2(workflow_file, backup_path / "workflow.json")
        
        # Save metadata
        if metadata:
            with open(backup_path / "metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2)
        
        # Create compressed archive
        archive_name = f"{backup_name}.tar.gz"
        archive_path = self.backup_dir / archive_name
        
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(backup_path, arcname=backup_name)
        
        # Remove uncompressed directory
        shutil.rmtree(backup_path)
        
        print(f"Backup created: {archive_path}")
        return str(archive_path)
    
    def list_backups(self) -> List[Dict]:
        """List all available backups"""
        backups = []
        for file in self.backup_dir.glob("*.tar.gz"):
            stat = file.stat()
            backups.append({
                "name": file.name,
                "path": str(file),
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        return sorted(backups, key=lambda x: x["created"], reverse=True)
    
    def restore_backup(self, backup_file: str, restore_path: str = ".") -> bool:
        """Restore a backup"""
        backup_path = Path(backup_file)
        
        if not backup_path.exists():
            print(f"Error: Backup file not found: {backup_file}")
            return False
        
        restore_path = Path(restore_path)
        restore_path.mkdir(exist_ok=True)
        
        # Extract archive
        with tarfile.open(backup_path, "r:gz") as tar:
            tar.extractall(restore_path)
        
        # Find workflow.json in extracted files
        for root, dirs, files in os.walk(restore_path):
            if "workflow.json" in files:
                workflow_path = Path(root) / "workflow.json"
                target_path = restore_path / "workflow_restored.json"
                shutil.copy2(workflow_path, target_path)
                print(f"Workflow restored to: {target_path}")
                return True
        
        print("Error: workflow.json not found in backup")
        return False
    
    def delete_backup(self, backup_file: str) -> bool:
        """Delete a backup file"""
        backup_path = Path(backup_file)
        if backup_path.exists():
            backup_path.unlink()
            print(f"Backup deleted: {backup_file}")
            return True
        else:
            print(f"Error: Backup file not found: {backup_file}")
            return False
    
    def cleanup_old_backups(self, keep_days: int = 30) -> int:
        """Delete backups older than specified days"""
        cutoff_date = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
        deleted_count = 0
        
        for file in self.backup_dir.glob("*.tar.gz"):
            if file.stat().st_mtime < cutoff_date:
                file.unlink()
                deleted_count += 1
        
        print(f"Deleted {deleted_count} old backups")
        return deleted_count

if __name__ == "__main__":
    manager = BackupManager()
    
    # Example usage
    print("Backup Manager Utility")
    print("=" * 50)
    
    # List backups
    backups = manager.list_backups()
    print(f"\nFound {len(backups)} backups:")
    for backup in backups:
        print(f"  - {backup['name']} ({backup['size']} bytes)")

