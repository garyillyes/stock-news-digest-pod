import shutil
from pathlib import Path
from datetime import datetime, timedelta, UTC

# Configuration
PAGES_DIR = Path("docs")
MAX_AGE_DAYS = 30

def run_cleanup():
    """Removes directories in the pages directory older than MAX_AGE_DAYS."""
    print("--- Starting Cleanup Script ---")
    if not PAGES_DIR.exists():
        print(f"Directory not found: {PAGES_DIR}. Exiting.")
        return

    # Get today's date
    now = datetime.now(UTC)
    cutoff_date = now - timedelta(days=MAX_AGE_DAYS)
    print(f"Removing all directories created before {cutoff_date.strftime('%Y-%m-%d')}...")

    deleted_count = 0
    for entry in PAGES_DIR.iterdir():
        # Expecting directory names like "YYYY-MM-DD"
        if entry.is_dir():
            try:
                # Parse the directory name as a date
                dir_date = datetime.strptime(entry.name, "%Y-%m-%d").replace(tzinfo=UTC)
                
                # Check if the directory is older than the cutoff
                if dir_date < cutoff_date:
                    print(f"Deleting {entry.name} (Age: {(now - dir_date).days} days)...")
                    shutil.rmtree(entry) # Recursively delete the directory
                    deleted_count += 1
            except ValueError:
                # Ignore files or directories that don't match the date format
                print(f"Skipping '{entry.name}', not a valid date format.")
            except OSError as e:
                print(f"Error deleting {entry.name}: {e}")

    print(f"--- Cleanup Finished: Deleted {deleted_count} old digests. ---")

if __name__ == "__main__":
    run_cleanup()
