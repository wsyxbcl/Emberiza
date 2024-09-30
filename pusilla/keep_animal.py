import argparse
import os
import shutil
from shutil import copytree, ignore_patterns


def copy_animal_dir(src, dst, exclude_dirs):
    copytree(
        src,
        dst,
        ignore=ignore_patterns(*exclude_dirs),
        dirs_exist_ok=True,
    )

def move_animal_dir(src, dst):
    for root, dirs, files in os.walk(src):
        if "Animal" in dirs:
            animal_dir = os.path.join(root, "Animal")
            # Get the relative path from the source to the 'Animal' directory
            rel_path = os.path.relpath(root, src)
            target_dir = os.path.join(dst, rel_path)

            # Create destination directories if they don't exist
            os.makedirs(target_dir, exist_ok=True)

            # Move the entire 'Animal' directory to the target location
            shutil.move(animal_dir, os.path.join(target_dir, "Animal"))
            print(f"Moved: {animal_dir} to {target_dir}/Animal")

if __name__ == "__main__":
    dir_name_exclude = ["Blank", "Others", "Person", "Vehicle"]

    parser = argparse.ArgumentParser(description="Copy or move only the 'Animal' directory while preserving structure.")
    parser.add_argument("src_dir", help="Source directory")
    parser.add_argument("dst_dir", help="Destination directory")
    parser.add_argument("--move", action="store_true", help="Move the 'Animal' directory instead of copying")
    args = parser.parse_args()

    if args.move:
        # Call move function
        move_animal_dir(args.src_dir, args.dst_dir)
    else:
        # Call copy function
        copy_animal_dir(args.src_dir, args.dst_dir, dir_name_exclude)