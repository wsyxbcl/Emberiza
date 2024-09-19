# get independent trigger event from tags.csv
# Usage: python get_encounter.py <input_tags_csv> <output_dir>

import sys
import polars as pl
from pathlib import Path
import os

def get_trigger(tags_csv, output_dir):
    df = pl.read_csv(tags_csv, try_parse_dates=True).select("filename", "datetime_original", "species")
    df = df.with_columns(pl.col("filename").str.split("_").list.first().alias("deployment"))
    df = df.sort("datetime_original")
    df = df.sort("deployment")
    df = df.with_columns((pl.col("datetime_original").diff().cast(pl.Int64) / 1_000_000 / 60).alias("delta_time"))
    df = df.with_columns((pl.col("delta_time") > 30).cast(pl.Int32).alias("exceed_threshold"))
    df = df.with_columns(pl.cum_sum("exceed_threshold").alias("trigger_event_id"))

    # fill the first trigger event id with 0
    df = df.with_columns(pl.col("trigger_event_id").fill_null(0))

    df.write_csv(Path(output_dir).joinpath("trigger.csv"), include_bom=True)

if __name__ == "__main__":
    get_trigger(sys.argv[1], sys.argv[2])