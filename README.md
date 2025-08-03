# The Expanse: A Telltale Series - Autosaver

A lightweight Python script that automatically creates rotating and archival backups of save files for *The Expanse: A Telltale Series* on **Windows**.
It creates rotating backups in the `\Rotate` folder, which are the last 5 saves in the game. When a save is more than 10 minutes older than any other save, it will create another copy within the `\Archive` folder.

## Folder Structure

```
.
├── expanse_autosaver.py
├── Saved\
│   ├── SaveSlot_n.sav
│   ├── SaveSlot_n_backup.sav
│   ├── SaveSlot_n_header.sav
│   └── SaveSlot_n_header_backup.sav
├── Rotating\
│   └── SaveSlot_n\
│       ├── 1\  ← newest
│       │   ├── SaveSlot_n.sav
│       │   ├── SaveSlot_n_backup.sav
│       │   ├── SaveSlot_n_header.sav
│       │   └── SaveSlot_n_header_backup.sav
│       └── 5\  ← oldest
│       │   ├── SaveSlot_n.sav
│       │   ├── SaveSlot_n_backup.sav
│       │   ├── SaveSlot_n_header.sav
│       │   └── SaveSlot_n_header_backup.sav
├── Archive\
│   └── SaveSlot_n\
│       └── YYYY-MM-DD-HH-MM\
│           ├── SaveSlot_n.sav
│           ├── SaveSlot_n_backup.sav
│           ├── SaveSlot_n_header.sav
│           └── SaveSlot_n_header_backup.sav
```

## Setup

Place `expanse_autosaver.py` in your Expanse save folder, usually located here:
   ```
   C:\Users\<username>\Documents\My Games\Telltale\Expanse
   ```

## Usage

1. Run the script with Python:

   ```bash
   python .\expanse_autosaver.py
   ```
   If you don't have Python installed, please follow an up to date guide on how to do so.
  
2. The script will monitor all `SaveSlot_*.sav` files in the `Saved\` folder.
   * Rotating backups are stored under `Rotating\SaveSlot_X\[1–5]`.
   * Full archival snapshots are stored under `Archive\SaveSlot_X\[timestamp]`.

3. To stop the script, press `Ctrl + C` in the terminal.

4. When restoring one of the saves:
   * Copy the contents of the desired folder over to `[...]\My Games\Telltale\Expanse\Saved` and replace. 
   * Reload the save within the game.

## Notes

* Only works on **Windows**.
* No changes are ever made to the original save files.
* Folders are created only when needed.
* This script is free to use, modify, and share. No license is required.
