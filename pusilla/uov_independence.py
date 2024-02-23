# Perform temporal independence test on UOV generated csv files
# by combine and clean the data and feed to serval

import os
from pathlib import Path

import polars as pl


def df_concat(df1, df2):
    return pl.concat([df1, df2], how="vertical")

if __name__ == '__main__':
    # Traverse the directory and read all csv files
    csv_path = Path("../test/uov_test_data/")
    uov_dfs = [pl.read_csv(f, encoding='GBK') for f in csv_path.glob("*.csv")]
    uov_filenames = [Path(f).stem for f in csv_path.glob("*.csv")]
    print(uov_filenames)
    # Concatinate
    for i, df in enumerate(uov_dfs):
        df = df.with_columns(pl.lit(os.path.join("dummy", uov_filenames[i], "dummy")).alias("path"))
        if i == 0:
            uov_data = df
        else:
            uov_data = df_concat(uov_data, df)
    # Clean
    uov_data = uov_data.select([
        pl.col("path"),
        pl.col("照片名").alias("filename"),
        pl.col("物种名称").alias("species"),
        pl.col("时间").alias("datetime_original")])
    # Save
    uov_data.write_csv("../test/uov_test_data/tags.csv")




