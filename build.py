# ADB Platform Tools GUI — PyInstaller Build Script
# Run: python build.py

import os
import sys
import subprocess
import shutil

APP_NAME = "ADB-Platform-Tools"
MAIN_SCRIPT = "main.py"
PT_FOLDER = "platform-tools"
DIST_DIR = "dist"

def build():
    print("=" * 60)
    print("  ADB Platform Tools GUI — Build Script")
    print("=" * 60)

    # Step 1: Install dependencies
    print("\n[1/3] Installing dependencies…")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

    # Step 2: Run PyInstaller
    print("\n[2/3] Building executable with PyInstaller…")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", APP_NAME,
        "--add-data", f"{PT_FOLDER};platform-tools",
        "--icon", "NONE",
        "--clean",
        MAIN_SCRIPT,
    ]
    subprocess.run(cmd, check=True)

    # Step 3: Copy platform-tools next to exe
    exe_path = os.path.join(DIST_DIR, f"{APP_NAME}.exe")
    dest_pt  = os.path.join(DIST_DIR, PT_FOLDER)

    print("\n[3/3] Copying platform-tools to dist folder…")
    if os.path.exists(dest_pt):
        shutil.rmtree(dest_pt)
    shutil.copytree(PT_FOLDER, dest_pt)

    print("\n" + "=" * 60)
    print(f"  ✅ Build complete!")
    print(f"  📁 Output: {os.path.abspath(DIST_DIR)}")
    print(f"  💾 Executable: {os.path.basename(exe_path)}")
    print("=" * 60)
    print("\n⚠  Distribute the entire 'dist' folder (exe + platform-tools)")


if __name__ == "__main__":
    build()
