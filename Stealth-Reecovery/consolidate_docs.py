#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from pathlib import Path

base_dir = Path(".")
output_file = "CONSOLIDATED_DOCUMENTATION.md"

# Define the structure
sections = {
    "Project Overview": [
        "README.md",
    ],
    "Quick Start Guides": [
        ("PSP-001 Quick Start", "PSP_001_QUICKSTART.md"),
        ("Retry Quick Start", "RETRY_QUICK_START.md"),
    ],
    "Implementation Status": [
        ("Phase 0 Complete", "PHASE_0_COMPLETE.md"),
        ("PSP-001 Complete", "PSP_001_COMPLETE.md"),
        ("PSP-001 Summary", "PSP_001_SUMMARY.md"),
        ("Retry-001 Complete", "RETRY_001_COMPLETE.md"),
        ("Full Stack Complete", "FULLSTACK_COMPLETE.md"),
        ("Stack Operational", "STACK_OPERATIONAL.md"),
        ("Implementation Summary", "IMPLEMENTATION_SUMMARY.md"),
        ("Application Status Report", "APPLICATION_STATUS_REPORT.md"),
    ],
    "Architecture & Design": [
        ("Partition Strategy", "docs/PARTITION_STRATEGY.md"),
        ("Observability", "OBSERVABILITY.md"),
    ],
    "Deployment & Operations": [
        ("Deployment Guide", "DEPLOYMENT_GUIDE.md"),
        ("Docker Guide", "DOCKER_GUIDE.md"),
        ("Demo Seed Data", "docs/DEMO_SEED.md"),
    ],
    "Testing & Quality": [
        ("Comprehensive Test Checklist", "COMPREHENSIVE_TEST_CHECKLIST.md"),
        ("Test Report (2025-10-19)", "TEST_REPORT_20251019-013718.md"),
        ("Phase 1 Complete Summary", "tests/_PHASE_1_COMPLETE_SUMMARY.md"),
    ],
    "Frontend (Tinko Console)": [
        ("Overview", "tinko-console/README.md"),
        ("Completion Summary", "tinko-console/COMPLETION_SUMMARY.md"),
        ("Restoration Complete", "tinko-console/RESTORATION_COMPLETE.md"),
        ("Frontend Deployment", "tinko-console/DEPLOYMENT.md"),
        ("Architecture", "tinko-console/docs/ARCHITECTURE.md"),
        ("Components", "tinko-console/docs/COMPONENTS.md"),
        ("Theme", "tinko-console/docs/THEME.md"),
        ("Visuals", "tinko-console/docs/VISUALS.md"),
        ("Testing", "tinko-console/docs/TESTING.md"),
        ("Test Report", "tinko-console/TEST_REPORT.md"),
    ],
    "Specifications": [
        ("Tinko Failed Payment Recovery", "specs/tinko_failed_payment_recovery.md"),
        ("QW Validation", "artifacts/qw-validation.md"),
    ],
    "Changelog & Reports": [
        ("Changelog", "CHANGELOG.md"),
        ("Delivery Summary", "DELIVERY_SUMMARY.md"),
        ("Delivery Report (2025-10-19)", "DELIVERY_REPORT_20251019-013718.md"),
        ("Final Success Report (2025-10-19)", "FINAL_SUCCESS_REPORT_20251019-013718.md"),
        ("Phase Summary (2025-10-19)", "PHASE_SUMMARY_20251019-013718.md"),
        ("Delivery Artifacts", "DELIVERY_ARTIFACTS_README.md"),
    ],
}

with open(output_file, 'w', encoding='utf-8') as out:
    # Write header
    out.write("""# Tinko - Stealth Recovery Platform
## Consolidated Documentation

**Generated:** October 20, 2025  
**Repository:** STEALTH-TINKO  
**Project:** Failed Payment Recovery System

---

# Table of Contents

""")
    
    # Write TOC
    for i, section in enumerate(sections.keys(), 1):
        anchor = section.lower().replace(" & ", "--").replace(" ", "-").replace("(", "").replace(")", "")
        out.write(f"{i}. [{section}](#{anchor})\n")
    
    out.write("\n---\n\n")
    
    # Write content
    files_found = 0
    files_missing = 0
    
    for section_name, items in sections.items():
        out.write(f"# {section_name}\n\n")
        
        for item in items:
            if isinstance(item, tuple):
                title, filepath = item
                out.write(f"## {title}\n\n")
            else:
                filepath = item
            
            full_path = base_dir / filepath
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        out.write(content)
                        out.write("\n\n")
                    files_found += 1
                    print(f"  ✓ {filepath}")
                except Exception as e:
                    out.write(f"*Error reading file: {filepath} - {e}*\n\n")
                    print(f"  ✗ {filepath} - {e}")
                    files_missing += 1
            else:
                out.write(f"*File not found: {filepath}*\n\n")
                print(f"  - {filepath} (not found)")
                files_missing += 1
        
        out.write("---\n\n")
    
    # Write footer
    out.write(f"""
# End of Consolidated Documentation

**Files Included:** {files_found}  
**Files Missing:** {files_missing}  
**Total Sections:** {len(sections)}  
**Generated:** October 20, 2025  
**Source Repository:** stealthorga-crypto/STEALTH-TINKO
""")

print(f"\n✅ Consolidated documentation created: {output_file}")
print(f"📄 Files included: {files_found}")
print(f"❌ Files missing: {files_missing}")
print(f"📋 Total sections: {len(sections)}")
