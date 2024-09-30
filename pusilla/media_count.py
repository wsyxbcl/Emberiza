# Count media file in a directory recursively and output the result to a csv file
# Usage: python media_count.py <directory> <output_file>

import os
import csv
import argparse


def count_media_files(directory):
    result = {}
    for root, _, files in os.walk(directory):
        media_count = len(
            [
                f
                for f in files
                if f.lower().endswith((".jpg", ".jpeg", ".png", ".mp4", ".avi", ".mov"))
            ]
        )
        if media_count > 0:
            result[root] = media_count
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory")
    parser.add_argument("output_file")
    args = parser.parse_args()

    media_count = count_media_files(args.directory)
    with open(args.output_file, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Directory", "Media Count"])
        for k, v in media_count.items():
            writer.writerow([k, v])
    print(f"Media count written to {args.output_file}")
