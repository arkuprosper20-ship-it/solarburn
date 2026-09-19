import os
import shutil

base = r"d:/PS15_SolarFlare"

# Define target directories
folders = {
    "dashboard": ["dashboard.html", "dashboard.css", "dashboard.js", "dashboard.py", "run_dashboard.bat"],
    "data": ["calibration_dataset.csv", "celestrrak_cache.json", "celestrak_cache.json", "telemetry_inline.json"],
    "scripts": ["satellite.min.js", "sepEngine.js"],
    "assets": ["sun_orange.png", "sun_purple.png", "sun_yellow.png"],
    "docs": ["README.md", "README_RUN.md"],
}

for folder, files in folders.items():
    target_dir = os.path.join(base, folder)
    os.makedirs(target_dir, exist_ok=True)
    for fname in files:
        src = os.path.join(base, fname)
        if os.path.exists(src):
            shutil.move(src, target_dir)
            print(f"Moved {fname} to {folder}/")
        else:
            print(f"File {fname} not found, skipping.")

print("Reorganization complete.")
