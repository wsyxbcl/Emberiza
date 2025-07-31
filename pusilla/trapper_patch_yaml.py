"""
Combines the functionality of the original three scripts (yaml2csv, patch-time,
csv2yaml) into a single script

Usage:
    python trapper_patch_yaml.py <input_yaml> <tags_csv> <output_yaml>

Example:
    python trapper_patch_yaml.py original_data.yaml tags.csv patched_data.yaml
"""

import argparse
import yaml
import polars as pl
import os
import csv
from datetime import datetime
from zoneinfo import ZoneInfo


def patch_yaml_with_csv(input_yaml_path, tags_csv_path, output_yaml_path):
    print("--- Starting YAML Datetime Patch ---")
    try:
        df_tags = pl.read_csv(tags_csv_path).select(["filename", "datetime"])
        df_tags = df_tags.with_columns(pl.col("filename").str.strip_suffix(".xmp"))
        df_tags = df_tags.with_columns(
            pl.col("filename").str.replace(r"\.(avi|AVI|mov|MOV)$", ".mp4")
        )
        df_tags = df_tags.unique(subset=["filename"], keep="first")
        time_patch_map = dict(zip(df_tags["filename"], df_tags["datetime"]))
        print(f"✅ Successfully processed {len(time_patch_map)} unique filenames from '{tags_csv_path}'")
    except Exception as e:
        print(f"❌ Error processing tags CSV file '{tags_csv_path}': {e}")
        return

    try:
        with open(input_yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        print(f"✅ Successfully loaded YAML data from '{input_yaml_path}'")
    except Exception as e:
        print(f"❌ Error loading YAML file '{input_yaml_path}': {e}")
        return

    patch_count = 0
    log_records = []
    for collection in data.get("collections", []):
        for deployment in collection.get("deployments", []):
            for resource in deployment.get("resources", []):
                filename = resource.get("file")
                if filename and filename in time_patch_map:
                    new_time_str = time_patch_map[filename]
                    if new_time_str:
                        try:
                            original_time = resource.get("date_recorded", "N/A")
                            
                            dt_shanghai = datetime.strptime(
                                new_time_str, "%Y-%m-%d %H:%M:%S"
                            ).replace(tzinfo=ZoneInfo("Asia/Shanghai"))
                            
                            dt_utc = dt_shanghai.astimezone(ZoneInfo("UTC"))
                            
                            new_formatted_time = dt_utc.strftime("%Y-%m-%dT%H:%M:%S%z")
                            
                            resource["date_recorded"] = new_formatted_time
                            
                            if original_time != new_formatted_time:
                                patch_count += 1
                                log_records.append([filename, original_time, new_formatted_time])

                        except (ValueError, TypeError) as e:
                            print(
                                f"⚠️ Warning: Could not parse non-empty datetime '{new_time_str}' for "
                                f"file '{filename}'. Skipping patch for this file. Error: {e}"
                            )

    print(f"✅ Patched {patch_count} resource datetimes where the timestamp differed.")

    try:
        with open(output_yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, sort_keys=False, default_style=None, allow_unicode=True)
        print(f"✅ Successfully wrote updated YAML to '{output_yaml_path}'")
    except Exception as e:
        print(f"❌ Error writing to output YAML file '{output_yaml_path}': {e}")
        return 

    if log_records:
        base_output_name = os.path.splitext(output_yaml_path)[0]
        log_csv_path = f"{base_output_name}_log.csv"
        try:
            with open(log_csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["file", "initial_time", "updated_time"])
                writer.writerows(log_records)
            print(f"✅ Successfully wrote log file to '{log_csv_path}'")
        except Exception as e:
            print(f"❌ Error writing to log file '{log_csv_path}': {e}")

    print("--- YAML Patch Process Finished ---")


def main():
    """Defines the command-line interface for the script."""
    parser = argparse.ArgumentParser(
        description="Patch 'date_recorded' in a trapper YAML file using a CSV file. "
                    "This script combines and improves upon the original three-step process.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("input_yaml", help="Path to the input trapper-generated YAML file.")
    parser.add_argument("tags_csv", help="Path to the input tags.csv file containing filename and corrected datetime.")
    parser.add_argument("output_yaml", help="Path to write the patched YAML file.")
    
    args = parser.parse_args()
    
    patch_yaml_with_csv(args.input_yaml, args.tags_csv, args.output_yaml)


if __name__ == "__main__":
    main()
