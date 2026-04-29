import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

def main():
    # Load with UTF-8 to ensure Japanese characters in the path are read correctly
    load_dotenv(encoding='utf-8')
    
    source = Path(os.getenv("SOURCE_DIR", ""))
    target = Path(os.getenv("TARGET_DIR", ""))

    if not source.exists():
        print(f"FAILED: Source directory not reachable: {source}")
        return

    target.mkdir(parents=True, exist_ok=True)

    # Dictionary to store { filename: path_object }
    latest_files_map = {}

    print(f"Scanning subfolders for unique PMS files...")

    # rglob handles the recursion through all subdirectories
    for pms_file in source.rglob("*.pms"):
        fname = pms_file.name
        
        if fname not in latest_files_map:
            # First time we've seen this filename
            latest_files_map[fname] = pms_file
        else:
            # Duplicate found! Compare timestamps
            existing_file = latest_files_map[fname]
            if pms_file.stat().st_mtime > existing_file.stat().st_mtime:
                # The new one is later; swap it in
                latest_files_map[fname] = pms_file

    if not latest_files_map:
        print("No PMS files found.")
        return

    print(f"Found {len(latest_files_map)} unique files. Starting copy...")

    # Copy the unique set to the target folder
    count = 0
    for fname, path_obj in latest_files_map.items():
        dest = target / fname
        try:
            # Only copy if destination is missing or older
            if not dest.exists() or path_obj.stat().st_mtime > dest.stat().st_mtime:
                shutil.copy2(path_obj, dest)
                count += 1
        except Exception as e:
            print(f"Could not copy {fname}: {e}")

    print(f"Finished. Successfully updated {count} files in {target}")

if __name__ == "__main__":
    main()