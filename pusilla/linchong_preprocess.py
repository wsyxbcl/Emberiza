# Workaround for marking all images in given directory as favorite in Photoprism
# Based on https://github.com/photoprism/photoprism/pull/1873

import argparse
import polars as pl
import yaml
import os
import shutil
from pathlib import Path


def mark_favorite(image_dir):
    """
    create xmp files (favorite) for all images in the directory recursively
    """
    xmp_file_path = Path(__file__).parent / "assets/fstop-favorite.xmp"
    for root, dirs, files in os.walk(image_dir):
        for file in files:
            if file.endswith((".jpg", ".jpeg", ".png", ".gif")):
                xmp_file = os.path.join(root, file + ".xmp")
                shutil.copyfile(xmp_file_path, xmp_file)
                print(f"Created {xmp_file}")


def gen_xmp_template(favorite, datetime):
    if favorite:
        favorite_str = """<rdf:Description rdf:about=""
            xmlns:fstop="http://www.fstopapp.com/xmp/"
            fstop:favorite="1"/>"""
    else:
        favorite_str = ""
    xmp_template = """<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>
    <x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="XMP Core 4.4.0-Exiv2">
    <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    {favorite}
    <rdf:Description rdf:about=''
        xmlns:photoshop='http://ns.adobe.com/photoshop/1.0/'>
        <photoshop:DateCreated>{datetime}</photoshop:DateCreated>
    </rdf:Description>
    </rdf:RDF>      
    </x:xmpmeta>
    <?xpacket end="w"?>
    """.format(favorite=favorite_str, datetime=datetime)
    return xmp_template


def find_occurred_deployment(csv_file):
    """
    find deployments for each individual
    """
    df_individual = (
        pl.read_csv(csv_file, infer_schema_length=0)
        .select("path", "individual")
        .filter(~pl.col("individual").is_in(["Blur", ""]))
        .filter(~pl.col("individual").str.starts_with("UN"))
        .filter(~pl.col("individual").str.starts_with("Unknown"))
        .with_columns(pl.col("individual").str.split("with").list.first())
        .with_columns(pl.col("individual").str.split("以及").list.first())
        .with_columns(pl.col("individual").str.split("及").list.first())
        .with_columns(pl.col("individual").str.strip_suffix(" "))
    )
    path_sample = df_individual[0]["path"].to_list()[0]
    delimeter = "/" if "/" in path_sample else "\\"
    for i, directory in enumerate(path_sample.split(delimeter)):
        print(f"{i}: {directory}")
    deployment_idx = input("Deployment index:")
    deployment_idx = int(deployment_idx)
    df_deployment = df_individual.with_columns(
        pl.col("path").str.split(delimeter).list.get(deployment_idx).alias("deployment")
    )
    df_individual_deployment = df_deployment.group_by("individual").agg(
        pl.col("deployment")
    )
    df_individual_deployment.with_columns(
        pl.col("deployment").list.unique().list.join(";")
    ).write_csv("individual_deployment.csv", include_bom=True)
    print("Output to individual_deployment.csv")


def update_last_recorded_time(csv_file, image_dir, favorite):
    """
    read tags.csv and write last_recorded_time to xmp files
    """
    schema_overrides = {"individual": pl.String}
    df_individual = (
        pl.read_csv(csv_file, try_parse_dates=True, schema_overrides=schema_overrides)
        .select(
            pl.col("datetime_original").alias("datetime"),
            pl.col("individual").alias("label"),
        )
        .drop_nulls()
        .filter(~pl.col("label").is_in(["Blur", ""]))
        .filter(~pl.col("label").str.starts_with("UN"))
        .filter(~pl.col("label").str.starts_with("Unknown"))
        # Temporary fix for "with*cub" related issue
        .with_columns(pl.col("label").str.split("with").list.first())
        # Temporary fix for "及" issue
        .with_columns(pl.col("label").str.split("以及").list.first())
        .with_columns(pl.col("label").str.split("及").list.first())
        # trim ending whitespace
        .with_columns(pl.col("label").str.strip_suffix(" "))
    )
    df_individual_extremum = (
        df_individual.lazy()
        .sort("datetime", descending=True)
        .group_by("label")
        .agg(
            pl.col("datetime").first().alias("latest_capture_time"),
            pl.col("datetime").last().alias("first_capture_time"),
        )
        .collect()
    )
    df_individual_extremum.write_csv(
        "individual_capture_extremum.csv", include_bom=True
    )
    print("Output to individual_capture_extremum.csv")

    individual_xmp_dict = {}
    for root, dirs, files in os.walk(image_dir):
        for file in files:
            if file.endswith((".jpg", ".jpeg", ".png", ".gif")):
                side_car_file = os.path.join(root, Path(file).stem + ".yml")
                try:
                    with open(side_car_file, "r") as f:
                        data = yaml.safe_load(f)
                        title = data["Title"]
                except FileNotFoundError:
                    # print(f"File {side_car_file} not found")
                    continue
                if len(title.split("-")) == 3:
                    _, _, label = title.split("-")
                elif len(title.split("-")) == 2:
                    _, label = title.split("-")
                xmp_file = os.path.join(root, file + ".xmp")
                if label not in individual_xmp_dict:
                    individual_xmp_dict[label] = [xmp_file]
                else:
                    individual_xmp_dict[label].append(xmp_file)

    for label, latest_capture_time, _ in df_individual_extremum.rows():
        if label in individual_xmp_dict:
            for xmp_file in individual_xmp_dict[label]:
                xmp_template = gen_xmp_template(favorite, latest_capture_time)
                with open(xmp_file, "w") as f:
                    f.write(xmp_template)
                # print(f"Updated {xmp_file} with {latest_capture_time}")
        else:
            if (
                label.startswith("UN")
                or label.startswith("Unknown")
                or label.startswith("Cub")
                or label.startswith("u")
                or ("Cub of" in label)
            ):
                continue
            print(f"Not in Linchong database, label: {label}")


def remove_xmp(image_dir):
    """
    remove all xmp files in the directory recursively
    """
    for root, dirs, files in os.walk(image_dir):
        for file in files:
            if file.endswith(".xmp"):
                xmp_file = os.path.join(root, file)
                os.remove(xmp_file)
                print(f"Removed {xmp_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--image-dir", dest="image_dir")
    # two subcommands: favorite and rmxmp
    parser.add_argument(
        "subcommand",
        choices=["favorite", "rmxmp", "time_init", "time_update", "find_deployments"],
    )
    # add another argument for time_init and time_update
    parser.add_argument("--tags-csv", dest="tags_csv")

    args = parser.parse_args()
    if args.subcommand == "favorite":
        mark_favorite(args.image_dir)
    elif args.subcommand == "rmxmp":
        remove_xmp(args.image_dir)
    elif args.subcommand == "time_init":
        update_last_recorded_time(args.tags_csv, args.image_dir, favorite=True)
    elif args.subcommand == "time_update":
        update_last_recorded_time(args.tags_csv, args.image_dir, favorite=False)
    elif args.subcommand == "find_deployments":
        find_occurred_deployment(args.tags_csv)
