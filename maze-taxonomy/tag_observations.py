# Tagging observation table with tags.csv
# Usage: python tag_observation.py -i observations.csv -m media.csv -t tags.csv -o observation_tagged.csv

import argparse
import polars as pl
from pathlib import Path

TAGLIST = Path(__file__).parent / "data/maze_taglist.csv"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Tagging observation table with tags.csv"
    )
    parser.add_argument(
        "-i", "--input", type=str, help="Input observation table", required=True
    )
    parser.add_argument(
        "-t", "--tags", type=str, help="Input tags table", required=True
    )
    parser.add_argument(
        "-m", "--media", type=str, help="Input media table", required=True
    )
    parser.add_argument(
        "-o", "--output", type=str, help="Output observation table", required=True
    )

    args = parser.parse_args()

    # Get filenames from media table
    df_observations = pl.read_csv(args.input).select(["mediaID", "_id"])
    df_media = pl.read_csv(args.media).select(["mediaID", "fileName"])
    df_observations = df_observations.join(df_media, on="mediaID")

    # Patching tags.csv
    df_tags = pl.read_csv(args.tags)
    df_tags = df_tags.select(
        [
            pl.col("filename")
            .str.split_exact(".", 1)
            .struct.rename_fields(["fileName", "extension"]),
            "species",
            "individual",
            pl.col("rating").replace("", "0"),
        ]
    ).unnest("filename")
    df_taglist = pl.read_csv(TAGLIST).select(
        [pl.col("tag").alias("species"), "scientificName"]
    )
    df_tags = df_tags.join(df_taglist, on="species", how="left").drop_nulls()

    # Tagging observations
    df_observations_tagged = df_observations.join(df_tags, on="fileName")
    df_observations_tagged = df_observations_tagged.select(
        [
            "_id",
            "scientificName",
            pl.lit("animal").alias("observationType"),
            pl.lit("1").alias("count"),
            pl.lit("human").alias("classificationMethod"),
            pl.concat_str(
                pl.lit("eng: "), pl.col("species"), pl.lit("|Rating:"), pl.col("rating")
            ).alias("observationTags"),
            pl.col("individual").alias("individualID"),
        ]
    )

    # Save
    df_observations_tagged.write_csv(args.output)
