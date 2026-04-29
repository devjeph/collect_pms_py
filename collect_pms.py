import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

def main():
    # Load configuration from .env with UTF-8 support for Japanese characters
    load_dotenv(encoding='utf-8')
    
    source_raw = os.getenv("SOURCE_DIR")
    target_raw = os.getenv("TARGET_DIR")

    if not source_raw or not target_raw:
        print("Error: SOURCE_DIR or TARGET_DIR not defined in .env")
        return

    source = Path(source_raw)
    
    # Logic: Specifically target a 'PMS' subfolder within your target directory
    target_base = Path(target_raw)
    target_pms = target_base / "PMS"

    # --- Defensive Check for Source ---
    if not source.exists():
        print(f"FAILED: Source directory not reachable: {source}")
        return

    # --- Create the Target PMS folder if it doesn't exist ---
    if not target_pms.exists():
        print(f"Target PMS folder not found. Creating: {target_pms}")
        # parents=True ensures the entire path tree is built if missing
        target_pms.mkdir(parents=True, exist_ok=True)

    # Dictionary to track unique filenames and their latest versions
    latest_files_map = {}

    print(f"Scanning for unique PMS files in {source}...")

    # Recursive search through all subfolders
    for pms_file in source.rglob("*.pms"):
        fname = pms_file.name
        
        if fname not in latest_files_map:
            latest_files_map[fname] = pms_file
        else:
            existing_file = latest_files_map[fname]
            # Compare modification timestamps
            if pms_file.stat().st_mtime > existing_file.stat().st_mtime:
                latest_files_map[fname] = pms_file

    if not latest_files_map:
        print("No PMS files found to collect.")
        return

    print(f"Found {len(latest_files_map)} unique files. Syncing to {target_pms}...")

    # Copy logic
    updated_count = 0
    for fname, path_obj in latest_files_map.items():
        dest_file = target_pms / fname
        try:
            # Only copy if the file is new or the source is more recent
            if not dest_file.exists() or path_obj.stat().st_mtime > dest_file.stat().st_mtime:
                shutil.copy2(path_obj, dest_file)
                updated_count += 1
        except Exception as e:
            print(f"Error copying {fname}: {e}")

    print(f"Sync Complete. {updated_count} files updated in: {target_pms}")

if __name__ == "__main__":
    main()