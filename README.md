# The Expanse: A Telltale Series - Autosaver

A lightweight Python script that automatically creates rotating and archival backups of save files for *The Expanse: A Telltale Series* on **Windows**.

## Folder Structure

```
.
├── expanse_autosaver.py
├── Saved\
│   └── SaveSlot_*.sav
├── Rotating\
│   └── SaveSlot_X\
│       ├── 1\  ← newest
│       └── 5\  ← oldest
├── Archive\
│   └── SaveSlot_X\
│       └── YYYY-MM-DD-HH-MM\
```

## Setup

1. Place `expanse_autosaver.py` in your Expanse save folder, usually located here:
   ```
   C:\Users\<username>\Documents\My Games\Telltale\Expanse
   ```

2. Run the script with Python:

   ```bash
   python .\expanse_autosaver.py
   ```
  If you don't have Python installed, please follow an up to date guide on how to do so.
  
3. The script will monitor all `SaveSlot_*.sav` files in the `Saved\` folder.

* Rotating backups are stored under `Rotating\SaveSlot_X\[1–5]`
* Full archival snapshots are stored under `Archive\SaveSlot_X\[timestamp]`

To stop the script, press `Ctrl + C` in the terminal.

## Notes

* Only works on **Windows**.
* No changes are ever made to the original save files.
* Folders are created only when needed.
* This script is free to use, modify, and share. No license is required.
