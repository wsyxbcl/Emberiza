# Perform temporal independence test on UOV generated csv files

import os
import sys

from pathlib import Path
import polars as pl


def utf8_to_gbk(input_path: Path, output_path: Path):
    with open(input_path, "r", encoding="utf-8") as f:
        with open(output_path, "w", encoding="GBK") as f_out:
            f_out.write(f.read())


if __name__ == "__main__":
    # # Check serval
    # script_path = Path(os.path.realpath(__file__)).parent
    # if os.name == 'nt':
    #     serval_path = script_path.joinpath("serval.exe")
    # else:
    #     serval_path = script_path.joinpath("serval")
    # if not serval_path.exists():
    #     raise FileNotFoundError("serval not found")

    # Traverse the directory and read all csv files
    try:
        csv_dir = Path(sys.argv[1])
    except IndexError:
        csv_dir = input("Please input the directory of UOV csv files: ")
        csv_dir = Path(csv_dir)

    uov_dfs = [pl.read_csv(f, encoding="GBK") for f in csv_dir.glob("*.csv")]
    if not uov_dfs:
        print("No csv file found in the directory")
        sys.exit(1)
    uov_filenames = [Path(f).stem for f in csv_dir.glob("*.csv")]

    # Concatinate
    for i, df in enumerate(uov_dfs):
        df = df.with_columns(
            pl.lit(os.sep + uov_filenames[i] + os.sep + "dummy").alias("path")
        )
        if i == 0:
            uov_data = df
        else:
            uov_data = pl.concat([uov_data, df], how="vertical")
    # Clean
    uov_data = uov_data.select(
        [
            pl.col("path"),
            pl.col("照片名").alias("filename"),
            pl.col("物种名称").alias("species"),
            pl.col("时间").str.strptime(pl.Datetime).alias("datetime_original"),
            pl.col("数量"),
            pl.col("行为"),
            pl.col("相机编号"),
        ]
    )

    # Output (serval compatible csv file)
    output_dir = csv_dir.joinpath("result")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_csv_path = output_dir.joinpath("tags.csv")
    uov_data.write_csv(output_csv_path, datetime_format=r"%Y-%m-%d %H:%M:%S")
    # Encode to GBK
    utf8_to_gbk(output_csv_path, output_dir.joinpath("tags_gbk.csv"))

    # Temporal independence analysis
    df_cleaned = (
        uov_data.lazy()
        .with_columns(
            [
                pl.col("path").str.split(os.sep).list.get(1).alias("deployment"),
                pl.col("datetime_original").alias("time"),
            ]
        )
        .drop_nulls(["species", "time", "deployment"])
        .unique(subset=["deployment", "time", "species"], maintain_order=True)
        .collect()
    )
    df_sorted = df_cleaned.sort("time").sort("species").sort("deployment")
    df_independent = (
        df_sorted.rolling(
            index_column="time",
            group_by=["deployment", "species"],
            period="30m",
            offset="0",
            closed="left",
        )
        .agg(
            [
                pl.count("species").alias("count"),
                pl.last("filename"),
                pl.last("数量"),
                pl.last("行为"),
                pl.last("相机编号"),
            ]
        )
        .filter(pl.col("count") == 1)
    )
    print(df_independent)
    indenpendent_csv_path = output_dir.joinpath("独立捕获.csv")
    df_independent.write_csv(
        indenpendent_csv_path, datetime_format=r"%Y-%m-%d %H:%M:%S"
    )
    utf8_to_gbk(indenpendent_csv_path, output_dir.joinpath("独立捕获_gbk.csv"))
    print("Saved to " + indenpendent_csv_path.as_posix())

    # Count the number of independent captures
    indenpendent_count_csv_path = output_dir.joinpath("独立捕获统计.csv")
    df_independent_count = df_independent.group_by(
        ["deployment", "species"], maintain_order=True
    ).agg(pl.count("species").alias("count"))
    print(df_independent_count)
    df_independent_count.write_csv(indenpendent_count_csv_path)
    utf8_to_gbk(
        indenpendent_count_csv_path, output_dir.joinpath("独立捕获统计_gbk.csv")
    )
    print("Saved to " + indenpendent_count_csv_path.as_posix())

    # Clean up directory
    os.remove(indenpendent_csv_path)
    os.remove(indenpendent_count_csv_path)

    # Freeze the terminal
    if os.name == "nt":
        os.system("pause")
    else:
        os.system('read -n 1 -s -p "Press any key to continue..."')
