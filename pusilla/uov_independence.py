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

    # Concatinate
    for i, df in enumerate(uov_dfs):
        df = df.with_columns(pl.lit(os.sep+uov_filenames[i]+os.sep+"dummy").alias("path"))
        if i == 0:
            uov_data = df
        else:
            uov_data = pl.concat([uov_data, df], how="vertical")
    # Clean
    uov_data = uov_data.select([
        pl.col("path"),
        pl.col("照片名").alias("filename"),
        pl.col("物种名称").alias("species"),
        pl.col("时间").str.strptime(pl.Datetime).alias("datetime_original"),
        pl.col("数量"),
        pl.col("行为"),
        pl.col("相机编号")
        ])
    print(uov_data)
    # Create output directory and write to csv
    output_dir = csv_dir.joinpath("result")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_csv_path = output_dir.joinpath("tags.csv")
    uov_data.write_csv(output_csv_path, datetime_format=r"%Y-%m-%d %H:%M:%S")
    # Encode to GBK
    with open(output_csv_path, 'r', encoding='utf-8') as f:
        with open(output_dir.joinpath("tags_gbk.csv"), 'w', encoding='GBK') as f_out:
            f_out.write(f.read())
            
    # Temporal independence analysis
    df_cleaned = uov_data.lazy().with_columns([
        pl.col("path").alias("deployment"),
        pl.col("datetime_original").alias("time")]).drop_nulls(["species", "time", "deployment"]).unique(subset=["deployment", "time", "species"], maintain_order=True).collect()

    df_sorted = df_cleaned.lazy().sort("time").sort("species").sort("deployment").collect()
    df_independent = df_sorted.rolling(
        index_column="time",
        by=["deployment", "species"],
        period="30m",
        check_sorted=False
    ).agg([
        pl.count("species").alias("count"),
        pl.last("filename"),
        pl.last("数量"),
        pl.last("行为"),
        pl.last("相机编号")
    ]).filter(
        pl.col("count") == 1
    )
    print(df_independent)
    df_independent.write_csv(output_dir.joinpath("独立捕获.csv"), datetime_format=r"%Y-%m-%d %H:%M:%S")
