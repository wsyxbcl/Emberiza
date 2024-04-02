from pathlib import Path

import polars as pl

if __name__ == '__main__':
    LATITUDE_PLACEHOLDER = 0
    LONGITUDE_PLACEHOLDER = 0
    COLLECTION_NAME = "AS202201-202203"
    BATCH = 0

    filename = Path("trap_info.csv")
    trap_info_path = Path("/mnt/data/AngSai/AS202201-202203")
    if BATCH:
        trap_infos = trap_info_path.glob('*/YunTa*.csv')
        trap_info_raw = pl.concat(
            [
                pl.read_csv(f, 
                    encoding='GBK', 
                    skip_rows=1, 
                    dtypes={"deploymentName": pl.Utf8,
                        "timestampProblem": pl.Boolean,
                        "coordinateUncertainty": pl.Utf8,})
                        .with_columns(pl.lit(Path(f).parent.name).alias("collectionName"))
                for f in trap_infos
            ],
            how="diagonal"
        )
    else:
        trap_info_raw = pl.read_csv(trap_info_path.joinpath(filename),
            # encoding='GBK',
            skip_rows=1).with_columns(pl.lit(COLLECTION_NAME).alias("collectionName"))

    # Drop nulls (for some reason there're empty rows in csv)
    trap_info_cleaned = trap_info_raw.filter(~pl.all_horizontal(pl.col("deploymentName").is_null())) 
    trap_info_cleaned = trap_info_cleaned.select(
        pl.col("deploymentName",
            "setupBy",
            "latitude",
            "longitude",
            "locationSource",
            "cameraWorkingDays",
            "deploymentComments",
            "exifTimeProblem1Start",
            "otherProblem1",
            "otherProblem2",
            "timestampProblem",
            "collectionName"),
        # ISO 8601 / RFC 3339 date & time format
        pl.col("deploymentStart", "deploymentEnd")
            .str.to_datetime(format="%m/%d/%Y")
            .dt.replace_time_zone(time_zone="Asia/Shanghai")
            .dt.to_string("%Y-%m-%dT%H:%M:%S%:z"))

    trap_info_tags = trap_info_cleaned.with_columns( 
        pl.when(pl.col("locationSource").eq("精确GPS"))
            .then(pl.lit("coordinate:GPS"))
            .when(pl.col("locationSource").eq("估计GPS"))
            .then(pl.lit("coordinate:guess"))
            .otherwise(pl.lit("coordinate:null"))
            .alias("coordinateSource"),
        pl.when(pl.col("otherProblem1").eq("照片损坏"))
            .then(pl.lit("照片损坏"))
            .when(pl.col("otherProblem1").eq("未有效工作"))
            .then(pl.lit("未有效工作"))
            .when(pl.col("otherProblem1").eq("相机位置移动"))
            .then(pl.lit("相机位置移动"))
            .when(pl.col("locationSource").eq("其它(在备注中注明)"))
            .then(pl.lit("问题见备注"))
            .otherwise(pl.lit(""))
            .alias("otherIssue1"),
        pl.when(pl.col("otherProblem2").is_not_null())
            .then(pl.lit("其它问题"))
            .otherwise(pl.lit(""))
            .alias("otherIssues"),
        pl.when(pl.col("exifTimeProblem1Start").is_not_null())
            .then(pl.lit("EXIF问题"))
            .otherwise(pl.lit(""))
            .alias("exifIssues"),
        pl.when(pl.col("timestampProblem").is_not_null())
            .then(pl.lit("true"))
            .otherwise(pl.lit("false"))
            .alias("timestampIssues"),
    )
    # print(trap_info_tags)

    # Patch location
    trap_info_patch = trap_info_tags.with_columns(
        pl.col("latitude").fill_null(pl.lit(LATITUDE_PLACEHOLDER)), 
        pl.col("longitude").fill_null(pl.lit(LONGITUDE_PLACEHOLDER)),
    )
    # print(trap_info_patch)

    deployments = trap_info_patch.select(
        pl.concat_str([
            pl.col("deploymentName"),
            pl.col("collectionName")
        ], separator='_').alias("deploymentID"), 

        pl.col("latitude",
            "longitude",
            "deploymentStart",
            "deploymentEnd",
            "setupBy", 
            "timestampIssues"),
        pl.concat_str([
            pl.lit("有效工作"),
            pl.col("cameraWorkingDays"),
            pl.lit("日; "),
            pl.col("deploymentComments"),
        ], separator="", ignore_nulls=True)
            .alias("deploymentComments"),
        pl.concat_str([
            pl.col("coordinateSource"),
            pl.col("exifIssues"),
            pl.col("otherIssue1"),
            pl.col("otherIssues")
        ], separator=" | ")
            .alias("deploymentTags"),
        pl.concat_str([
            pl.col("latitude"),
            pl.col("longitude")
        ], separator="/")
            .alias("locationID"),
    )
    print(deployments)
    if BATCH:
        deployments.write_csv(trap_info_path.joinpath('deployments.csv'))
        print("deployment table saved as: ", trap_info_path.joinpath('deployments.csv'))
    else:
        deployments.write_csv(Path("./").joinpath(filename.stem+'_deployments.csv'))