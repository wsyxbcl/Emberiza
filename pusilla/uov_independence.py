# Perform temporal independence test on UOV generated csv files

import os
import sys
import subprocess

from pathlib import Path
import polars as pl

if __name__ == '__main__':
    # # Check serval
    # script_path = Path(os.path.realpath(__file__)).parent
    # if os.name == 'nt':
    #     serval_path = script_path.joinpath("serval.exe")
    # else:
    #     serval_path = script_path.joinpath("serval")
    # if not serval_path.exists():
    #     raise FileNotFoundError("serval not found")

    # Traverse the directory and read all csv files
    csv_dir = Path(sys.argv[1])
    uov_dfs = [pl.read_csv(f, encoding='GBK') for f in csv_dir.glob("*.csv")]
    uov_filenames = [Path(f).stem for f in csv_dir.glob("*.csv")]
    print(uov_filenames)
    # Concatinate
    for i, df in enumerate(uov_dfs):
        df = df.with_columns(pl.lit(uov_filenames[i]).alias("path"))
        if i == 0:
            uov_data = df
        else:
            uov_data = pl.concat([uov_data, df], how="vertical")
    # Clean
    uov_data = uov_data.select([
        pl.col("path"),
        pl.col("照片名").alias("filename"),
        pl.col("物种名称").alias("species"),
        pl.col("时间").alias("datetime_original")])
    # Create output directory and write to csv
    output_dir = csv_dir.joinpath("result")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_csv_path = output_dir.joinpath("tags.csv")
    uov_data.write_csv(output_csv_path)
    # Encode to GBK
    with open(output_csv_path, 'r', encoding='utf-8') as f:
        with open(output_dir.joinpath("tags_gbk.csv"), 'w', encoding='GBK') as f_out:
            f_out.write(f.read())
            
    # Temporal independence analysis
    df_cleaned = uov_data.lazy().select([
        pl.col("path").alias("deployment"),
        pl.col("datetime_original").str.strptime(pl.Datetime).alias("time"),
        pl.col("filename"),
        pl.col("species")]).drop_nulls().unique(subset=["deployment", "time", "species"], maintain_order=True).collect()
        # pl.col("species")]).collect()
    df_cleaned.write_csv(output_dir.joinpath("cleaned.csv"))

    df_sorted = df_cleaned.lazy().sort("time").sort("species").sort("deployment").collect()
    df_independent = df_sorted.rolling(
        index_column="time",
        by=["deployment", "species"],
        period="30m",
        check_sorted=False
    ).agg([
        pl.count("species").alias("count"),
        pl.last("filename"),
    ]).filter(
        pl.col("count") == 1
    )
    df_independent.write_csv(output_dir.joinpath("independence.csv"))
