#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Archive old markdown files after consolidation
Creates a backup directory and moves all individual .md files there
"""
import os
import shutil
from pathlib import Path
from datetime import datetime

base_dir = Path(".")
archive_dir = base_dir / "_archived_docs" / datetime.now().strftime("%Y%m%d_%H%M%S")

# Files to archive (same list from consolidation)
files_to_archive = [
    "README.md",  # Keep this one - it's important for GitHub
    "PSP_001_QUICKSTART.md",
    "RETRY_QUICK_START.md",
    "PHASE_0_COMPLETE.md",
    "PSP_001_COMPLETE.md",
    "PSP_001_SUMMARY.md",
    "RETRY_001_COMPLETE.md",
    "FULLSTACK_COMPLETE.md",
    "STACK_OPERATIONAL.md",
    "IMPLEMENTATION_SUMMARY.md",
    "APPLICATION_STATUS_REPORT.md",
    "docs/PARTITION_STRATEGY.md",
    "OBSERVABILITY.md",
    "DEPLOYMENT_GUIDE.md",
    "DOCKER_GUIDE.md",
    "docs/DEMO_SEED.md",
    "COMPREHENSIVE_TEST_CHECKLIST.md",
    "TEST_REPORT_20251019-013718.md",
    "tests/_PHASE_1_COMPLETE_SUMMARY.md",
    "tinko-console/COMPLETION_SUMMARY.md",
    "tinko-console/RESTORATION_COMPLETE.md",
    "tinko-console/RESTORATION_SUCCESS.md",
    "tinko-console/DEPLOYMENT.md",
    "tinko-console/FIX-LOCALHOST-ERROR.md",
    "tinko-console/docs/ARCHITECTURE.md",
    "tinko-console/docs/COMPONENTS.md",
    "tinko-console/docs/THEME.md",
    "tinko-console/docs/VISUALS.md",
    "tinko-console/docs/TESTING.md",
    "tinko-console/docs/TESTING-CHECKLIST.md",
    "tinko-console/docs/MOTION.md",
    "tinko-console/docs/PROGRESS.md",
    "tinko-console/docs/ROLLBACK.md",
    "tinko-console/docs/CROSS-PLATFORM.md",
    "tinko-console/docs/CROSS-PLATFORM-SUMMARY.md",
    "tinko-console/docs/AUDIT.md",
    "tinko-console/TEST_REPORT.md",
    "specs/tinko_failed_payment_recovery.md",
    "artifacts/qw-validation.md",
    "CHANGELOG.md",
    "DELIVERY_SUMMARY.md",
    "DELIVERY_REPORT_20251019-013718.md",
    "FINAL_SUCCESS_REPORT_20251019-013718.md",
    "PHASE_SUMMARY_20251019-013718.md",
    "DELIVERY_ARTIFACTS_README.md",
]

# Files to keep (don't archive)
keep_files = [
    "README.md",  # Main README should stay
    "tinko-console/README.md",  # Frontend README should stay
    "CONSOLIDATED_DOCUMENTATION.md",  # Our new consolidated doc
]

print("📦 Creating archive directory...")
archive_dir.mkdir(parents=True, exist_ok=True)

archived_count = 0
kept_count = 0
not_found = 0

for filepath in files_to_archive:
    full_path = base_dir / filepath
    
    if filepath in keep_files:
        print(f"  ⏭️  Keeping: {filepath}")
        kept_count += 1
        continue
    
    if full_path.exists():
        # Create subdirectories in archive if needed
        archive_target = archive_dir / filepath
        archive_target.parent.mkdir(parents=True, exist_ok=True)
        
        # Move file to archive
        shutil.move(str(full_path), str(archive_target))
        print(f"  ✓ Archived: {filepath}")
        archived_count += 1
    else:
        print(f"  - Not found: {filepath}")
        not_found += 1

print(f"\n✅ Archive complete!")
print(f"📦 Archived: {archived_count} files")
print(f"📌 Kept: {kept_count} files")
print(f"❌ Not found: {not_found} files")
print(f"📁 Archive location: {archive_dir}")
print(f"\n💡 You now have:")
print(f"   - CONSOLIDATED_DOCUMENTATION.md (342KB with all content)")
print(f"   - README.md (kept for GitHub)")
print(f"   - tinko-console/README.md (kept for frontend)")
print(f"   - {archive_dir} (backup of all archived files)")
