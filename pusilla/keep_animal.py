import argparse
from shutil import copytree, ignore_patterns

if __name__ == "__main__":
    dir_name_exclude = ["Blank", "Others", "Person", "Vehicle"]

    parser = argparse.ArgumentParser()
    parser.add_argument("src_dir")
    parser.add_argument("dst_dir")
    args = parser.parse_args()

    copytree(
        args.src_dir,
        args.dst_dir,
        ignore=ignore_patterns(*dir_name_exclude),
        dirs_exist_ok=True,
    )
