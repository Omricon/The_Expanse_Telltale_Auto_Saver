import time
import shutil
import logging
from pathlib import Path
from datetime import datetime
import os
import stat
import errno

# --- Configuration ---
ROOT_FOLDER = Path(__file__).parent.resolve()
SAVE_FOLDER = ROOT_FOLDER / "Saved"
ROTATING_FOLDER = ROOT_FOLDER / "Rotating"
ARCHIVE_FOLDER = ROOT_FOLDER / "Archive"
SAVE_SLOTS = [f"SaveSlot_{i}" for i in range(1, 6)]
CHECK_INTERVAL = 5	# seconds
ARCHIVE_BACKUP_MIN_AGE = 10 * 60	# seconds (10 minutes)

# --- Logging ---
log_file = ROOT_FOLDER / "expanse_autosaver.log"
logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s - %(message)s",
	datefmt="%Y-%m-%d %H:%M:%S",
	handlers=[
		logging.FileHandler(log_file, encoding="utf-8"),
		logging.StreamHandler()
	]
)

# --- Utilities ---
def timestamp():
	return datetime.now().strftime("%Y-%m-%d-%H-%M")

def get_related_files(slot):
	return [
		f"{slot}.sav",
		f"{slot}_backup.sav",
		f"{slot}_header.sav",
		f"{slot}_header_backup.sav"
	]

def get_slot_modified_time(slot):
	primary = SAVE_FOLDER / f"{slot}.sav"
	return primary.stat().st_mtime if primary.exists() else None

def get_latest_archive_timestamp(slot):
	archive_path = ARCHIVE_FOLDER / slot
	if not archive_path.exists():
		return 0
	# Find the latest valid backup directory
	all_dirs = sorted([d for d in archive_path.iterdir() if d.is_dir()], reverse=True)
	for d in all_dirs:
		save_file = d / f"{slot}.sav"
		if save_file.exists():
			return save_file.stat().st_mtime
	return 0

def handle_remove_readonly(func, path, exc):
	"""
	Error handler for shutil.rmtree that handles read-only files.
	"""
	excvalue = exc[1]
	if func in (os.rmdir, os.remove, os.unlink) and excvalue.errno == errno.EACCES:
		os.chmod(path, stat.S_IWRITE)
		func(path) # Retry the function
	else:
		# Re-raise the exception if it's not a permission error
		raise

def force_delete_with_permissions(path):
	"""
	Deletes a directory tree, using an error handler for read-only files.
	"""
	try:
		shutil.rmtree(path, onerror=handle_remove_readonly)
		logging.info(f"[DELETE] Successfully removed: {path}")
		return True
	except Exception as e:
		logging.error(f"[ERROR] Could not delete folder {path}: {e}")
		return False

def rotate_slot(slot):
	"""
	Rotates backups from 1->2, 2->3, etc., and deletes 5.
	Returns True on success, False on failure.
	"""
	slot_path = ROTATING_FOLDER / slot
	slot_path.mkdir(parents=True, exist_ok=True)

	to_delete = slot_path / "5"
	if to_delete.exists():
		if not force_delete_with_permissions(to_delete):
			if to_delete.exists(): # Check if deletion actually failed
				logging.error(f"[ERROR] Folder {to_delete} still exists after delete attempt. Aborting rotation.")
				return False # Indicate failure

	for i in range(4, 0, -1):
		archive = slot_path / str(i)
		new = slot_path / str(i + 1)
		if archive.exists():
			try:
				archive.rename(new)
			except Exception as e:
				logging.error(f"Failed to rename {archive} to {new}: {e}")
				return False

	return True # Indicate success

def copy_to_rotating(slot):
	dest = ROTATING_FOLDER / slot / "1"
	dest.mkdir(parents=True, exist_ok=True)
	try:
		for f in get_related_files(slot):
			src = SAVE_FOLDER / f
			if src.exists():
				shutil.copy2(src, dest / f)
		logging.info(f"[ROTATE] Copied new save of {slot} to Rotating/{slot}/1")
	except Exception as e:
		logging.error(f"Failed to copy to rotating folder for {slot}: {e}")


def copy_to_archive(slot):
	dest = ARCHIVE_FOLDER / slot / timestamp()
	dest.mkdir(parents=True, exist_ok=True)
	try:
		for f in get_related_files(slot):
			src = SAVE_FOLDER / f
			if src.exists():
				shutil.copy2(src, dest / f)
		logging.info(f"[ARCHIVE] Copied snapshot of {slot} to Archive/{slot}/{dest.name}")
	except Exception as e:
		logging.error(f"Failed to copy to archive folder for {slot}: {e}")


# --- Main Loop ---
def main():
	logging.info("Starting expanse_autosaver.py")
	last_modified = {}

	for slot in SAVE_SLOTS:
		last = get_slot_modified_time(slot)
		if last:
			last_modified[slot] = last
			logging.info(f"[INIT] {slot} last modified at {datetime.fromtimestamp(last).strftime('%Y-%m-%d %H:%M:%S')}")

	while True:
		try:
			time.sleep(CHECK_INTERVAL)

			for slot in SAVE_SLOTS:
				current_mtime = get_slot_modified_time(slot)
				if not current_mtime:
					continue
				
				# Use a small tolerance to avoid detecting the same write multiple times
				is_newly_modified = current_mtime > last_modified.get(slot, 0) + 1

				if is_newly_modified:
					logging.info(f"[UPDATE] Detected change in {slot}. Starting backup process.")
					last_modified[slot] = current_mtime

					# Only proceed if the rotation logic succeeds
					if rotate_slot(slot):
						time.sleep(1) # Short pause to let file system settle
						copy_to_rotating(slot)

						if current_mtime - get_latest_archive_timestamp(slot) >= ARCHIVE_BACKUP_MIN_AGE:
							copy_to_archive(slot)
					else:
						logging.warning(f"Backup process for {slot} skipped due to rotation failure.")

		except KeyboardInterrupt:
			logging.info("Shutting down...")
			break
		except Exception as e:
			logging.error(f"[CRITICAL ERROR] An unexpected error occurred in the main loop: {e}", exc_info=True)
			time.sleep(10) # Prevent rapid-fire errors

if __name__ == "__main__":
	main()
