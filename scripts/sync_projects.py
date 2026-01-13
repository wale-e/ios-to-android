#!/usr/bin/env python3
"""
Sync iOS Swift changes to existing Android Kotlin project.
Detects changes since last sync and applies incremental updates.
"""

import os
import sys
import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Optional
import subprocess


@dataclass
class FileChange:
    ios_path: str
    android_path: Optional[str]
    change_type: str  # added, modified, deleted
    old_checksum: Optional[str]
    new_checksum: Optional[str]


@dataclass  
class SyncState:
    last_sync_date: str
    ios_commit: Optional[str]
    ios_path: str
    android_path: str
    package_name: str
    file_mapping: dict
    checksums: dict


def load_sync_state(android_path: Path) -> Optional[SyncState]:
    """Load sync state from Android project."""
    sync_file = android_path / ".ios-android-sync.json"
    if not sync_file.exists():
        return None
    
    try:
        data = json.loads(sync_file.read_text())
        return SyncState(
            last_sync_date=data.get('lastSyncDate', ''),
            ios_commit=data.get('iosCommit'),
            ios_path=data.get('iosPath', ''),
            android_path=data.get('androidPath', ''),
            package_name=data.get('packageName', ''),
            file_mapping=data.get('fileMapping', {}),
            checksums=data.get('checksums', {})
        )
    except (json.JSONDecodeError, KeyError):
        return None


def save_sync_state(android_path: Path, state: SyncState) -> None:
    """Save sync state to Android project."""
    sync_file = android_path / ".ios-android-sync.json"
    data = {
        'lastSyncDate': state.last_sync_date,
        'iosCommit': state.ios_commit,
        'iosPath': state.ios_path,
        'androidPath': state.android_path,
        'packageName': state.package_name,
        'fileMapping': state.file_mapping,
        'checksums': state.checksums
    }
    sync_file.write_text(json.dumps(data, indent=2))


def get_file_checksum(filepath: Path) -> str:
    """Calculate MD5 checksum of a file."""
    if not filepath.exists():
        return ""
    return hashlib.md5(filepath.read_bytes()).hexdigest()


def get_git_commit(path: Path) -> Optional[str]:
    """Get current git commit hash."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            cwd=path,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        pass
    return None


def get_changed_files_git(ios_path: Path, since_commit: str) -> list[str]:
    """Get files changed since a specific commit using git."""
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only', since_commit, 'HEAD', '--', '*.swift'],
            cwd=ios_path,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return [f for f in result.stdout.strip().split('\n') if f]
    except FileNotFoundError:
        pass
    return []


def detect_changes(ios_path: Path, state: SyncState) -> list[FileChange]:
    """Detect changes in iOS project since last sync."""
    changes = []
    
    # Find all Swift files (excluding Pods, etc.)
    swift_files = list(ios_path.rglob("*.swift"))
    swift_files = [f for f in swift_files if not any(
        x in str(f) for x in ['Pods/', 'Carthage/', 'build/', '.build/', 'DerivedData/']
    )]
    
    current_files = {}
    for filepath in swift_files:
        rel_path = str(filepath.relative_to(ios_path))
        current_files[rel_path] = get_file_checksum(filepath)
    
    # Check for modified and added files
    for rel_path, checksum in current_files.items():
        old_checksum = state.checksums.get(rel_path)
        android_path = state.file_mapping.get(rel_path)
        
        if old_checksum is None:
            # New file
            changes.append(FileChange(
                ios_path=rel_path,
                android_path=None,
                change_type='added',
                old_checksum=None,
                new_checksum=checksum
            ))
        elif old_checksum != checksum:
            # Modified file
            changes.append(FileChange(
                ios_path=rel_path,
                android_path=android_path,
                change_type='modified',
                old_checksum=old_checksum,
                new_checksum=checksum
            ))
    
    # Check for deleted files
    for rel_path in state.checksums:
        if rel_path not in current_files:
            changes.append(FileChange(
                ios_path=rel_path,
                android_path=state.file_mapping.get(rel_path),
                change_type='deleted',
                old_checksum=state.checksums[rel_path],
                new_checksum=None
            ))
    
    return changes


def classify_file(filepath: str, content: str) -> str:
    """Classify a Swift file into a category."""
    path_lower = filepath.lower()
    name = Path(filepath).stem.lower()
    
    if 'test' in path_lower or name.endswith('tests') or name.endswith('test'):
        return 'test'
    elif 'viewmodel' in name or 'vm' in name:
        return 'viewmodel'
    elif 'View' in content and 'body:' in content:
        return 'view'
    elif 'UIViewController' in content:
        return 'view'
    elif 'model' in path_lower or ('struct' in content and 'Codable' in content):
        return 'model'
    elif 'service' in path_lower or 'api' in path_lower or 'network' in path_lower:
        return 'service'
    elif 'extension' in path_lower:
        return 'extension'
    elif 'util' in path_lower or 'helper' in path_lower:
        return 'utility'
    return 'other'


def convert_swift_to_kotlin(swift_content: str) -> str:
    """Convert Swift to Kotlin (basic)."""
    import re
    kotlin = swift_content
    
    replacements = [
        (r'\blet\b', 'val'), (r'\bvar\b', 'var'), (r'\bfunc\b', 'fun'),
        (r'\bnil\b', 'null'), (r'\bself\b', 'this'), (r'\bstruct\b', 'data class'),
        (r'\benum\b', 'enum class'), (r'\bprotocol\b', 'interface'),
        (r'\bBool\b', 'Boolean'), (r'\?\?', '?:'),
        (r'-> Void', ': Unit'), (r'-> (\w+)', r': \1'),
        (r'\\\(([^)]+)\)', r'${\1}'),
        (r'\.count\b', '.size'), (r'\.isEmpty\b', '.isEmpty()'),
        (r'\.append\(', '.add('), (r'print\(', 'println('),
    ]
    
    for pattern, replacement in replacements:
        kotlin = re.sub(pattern, replacement, kotlin)
    
    return kotlin


def determine_android_path(ios_path: str, file_type: str, package_name: str) -> str:
    """Determine the Android path for a converted file."""
    pkg_path = package_name.replace('.', '/')
    filename = Path(ios_path).stem + ".kt"
    
    type_to_dir = {
        'model': f'app/src/main/java/{pkg_path}/model',
        'viewmodel': f'app/src/main/java/{pkg_path}/viewmodel',
        'view': f'app/src/main/java/{pkg_path}/ui/screens',
        'service': f'app/src/main/java/{pkg_path}/data/repository',
        'extension': f'app/src/main/java/{pkg_path}/util',
        'utility': f'app/src/main/java/{pkg_path}/util',
        'other': f'app/src/main/java/{pkg_path}',
    }
    
    dir_path = type_to_dir.get(file_type, type_to_dir['other'])
    return f"{dir_path}/{filename}"


def apply_change(change: FileChange, ios_path: Path, android_path: Path, 
                 package_name: str, dry_run: bool = False) -> Optional[str]:
    """Apply a single file change."""
    
    if change.change_type == 'deleted':
        if change.android_path:
            target = android_path / change.android_path
            if target.exists():
                if dry_run:
                    print(f"  Would delete: {change.android_path}")
                else:
                    target.unlink()
                    print(f"  Deleted: {change.android_path}")
        return None
    
    # For added or modified files
    source = ios_path / change.ios_path
    if not source.exists():
        return None
    
    swift_content = source.read_text(errors='ignore')
    file_type = classify_file(change.ios_path, swift_content)
    
    # Skip test files for now
    if file_type == 'test':
        print(f"  Skipping test file: {change.ios_path}")
        return None
    
    # Determine target path
    if change.android_path:
        target_rel = change.android_path
    else:
        target_rel = determine_android_path(change.ios_path, file_type, package_name)
    
    target = android_path / target_rel
    
    # Convert content
    kotlin_content = convert_swift_to_kotlin(swift_content)
    
    # Add package declaration
    pkg_parts = target_rel.replace('app/src/main/java/', '').rsplit('/', 1)[0]
    pkg = pkg_parts.replace('/', '.')
    kotlin_content = f"package {pkg}\n\n// TODO: VERIFY - Synced from {change.ios_path}\n\n" + kotlin_content
    
    if dry_run:
        print(f"  Would {'update' if change.change_type == 'modified' else 'create'}: {target_rel}")
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        
        if change.change_type == 'modified' and target.exists():
            # Add conflict markers if file has local changes
            old_content = target.read_text()
            if old_content != kotlin_content:
                kotlin_content = f'''// <<<<<<< ANDROID (local)
// The following is the existing Android code.
// Review and merge with the iOS changes below.
// =======

{old_content}

// >>>>>>> iOS (incoming)
// The following is the converted iOS code.
// =======

{kotlin_content}
'''
        
        target.write_text(kotlin_content)
        action = "Updated" if change.change_type == 'modified' else "Created"
        print(f"  {action}: {target_rel}")
    
    return target_rel


def sync_projects(ios_path: Path, android_path: Path, 
                  since: Optional[str] = None,
                  files: Optional[list[str]] = None,
                  dry_run: bool = False,
                  interactive: bool = False) -> None:
    """Sync iOS changes to Android project."""
    
    # Load existing sync state
    state = load_sync_state(android_path)
    if not state:
        print("Error: No sync state found. Run convert_project.py first.", file=sys.stderr)
        sys.exit(1)
    
    print(f"iOS project: {ios_path}")
    print(f"Android project: {android_path}")
    print(f"Last sync: {state.last_sync_date}")
    print()
    
    # Detect changes
    print("Detecting changes...")
    changes = detect_changes(ios_path, state)
    
    # Filter by specific files if requested
    if files:
        changes = [c for c in changes if any(f in c.ios_path for f in files)]
    
    if not changes:
        print("No changes detected.")
        return
    
    # Summarize changes
    added = [c for c in changes if c.change_type == 'added']
    modified = [c for c in changes if c.change_type == 'modified']
    deleted = [c for c in changes if c.change_type == 'deleted']
    
    print(f"Found {len(changes)} changes:")
    print(f"  Added: {len(added)}")
    print(f"  Modified: {len(modified)}")
    print(f"  Deleted: {len(deleted)}")
    print()
    
    if dry_run:
        print("Dry run - showing what would be done:")
        print()
    
    # Apply changes
    new_mapping = dict(state.file_mapping)
    new_checksums = dict(state.checksums)
    
    for change in changes:
        if interactive and not dry_run:
            response = input(f"Apply {change.change_type} for {change.ios_path}? [y/n/q] ").lower()
            if response == 'q':
                print("Sync aborted.")
                return
            if response != 'y':
                continue
        
        result = apply_change(change, ios_path, android_path, state.package_name, dry_run)
        
        if not dry_run:
            if change.change_type == 'deleted':
                if change.ios_path in new_mapping:
                    del new_mapping[change.ios_path]
                if change.ios_path in new_checksums:
                    del new_checksums[change.ios_path]
            else:
                if result:
                    new_mapping[change.ios_path] = result
                if change.new_checksum:
                    new_checksums[change.ios_path] = change.new_checksum
    
    # Update sync state
    if not dry_run:
        state.last_sync_date = datetime.now().isoformat()
        state.ios_commit = get_git_commit(ios_path)
        state.file_mapping = new_mapping
        state.checksums = new_checksums
        save_sync_state(android_path, state)
        print()
        print("Sync complete. State updated.")
    
    print()
    print("Next steps:")
    print("1. Review files with conflict markers")
    print("2. Search for TODO: VERIFY comments")
    print("3. Build and test the Android project")


def main():
    parser = argparse.ArgumentParser(description="Sync iOS changes to Android project")
    parser.add_argument("ios_path", help="Path to iOS project")
    parser.add_argument("android_path", help="Path to Android project")
    parser.add_argument("--since", help="Sync changes since date or commit")
    parser.add_argument("--files", help="Comma-separated list of specific files to sync")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    parser.add_argument("--interactive", "-i", action="store_true", help="Prompt for each change")
    
    args = parser.parse_args()
    
    ios_path = Path(args.ios_path).resolve()
    android_path = Path(args.android_path).resolve()
    
    if not ios_path.exists():
        print(f"Error: iOS path not found: {ios_path}", file=sys.stderr)
        sys.exit(1)
    
    if not android_path.exists():
        print(f"Error: Android path not found: {android_path}", file=sys.stderr)
        sys.exit(1)
    
    files = args.files.split(',') if args.files else None
    
    sync_projects(
        ios_path=ios_path,
        android_path=android_path,
        since=args.since,
        files=files,
        dry_run=args.dry_run,
        interactive=args.interactive
    )


if __name__ == "__main__":
    main()
