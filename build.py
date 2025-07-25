import os
import shutil
import PyInstaller.__main__
from typing import List


def build_game():
    # --- Configuration --- #
    entry_point = "code/main.py"
    build_name = "ProjectMonster"
    extra_dirs = ["audio", "data", "graphics", "save"]
    dist_dir = "dist"
    build_dir = "build"

    # --- Clean previous builds ---
    if os.path.exists(dist_dir):
        shutil.rmtree(build_dir)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    if os.path.exists(f"{build_name}.spec"):
        shutil.rmtree(f"{build_name}.spec")

    # --- Prepare additional data arguments ---
    # PyInstaller format: "source_path;destination_folder_inside_dist"
    datas: List[str] = []
    for folder in extra_dirs:
        if os.path.exists(folder):
            datas.append(f"{folder}{os.pathsep}{folder}")

    # --- Build command ---
    pyinstaller_args = [
        entry_point,
        "--name", build_name,
        "--onedir",
        "--windowed"
    ]

    # Add data directories
    for d in datas:
        pyinstaller_args.extend(["--add-data", d])

    # Run PyInstaller
    PyInstaller.__main__.run(pyinstaller_args)

    print(f"\n✅ Build completed! Executable is in '{dist_dir}/{build_name}/'")


if __name__ == "__main__":
    build_game()
    