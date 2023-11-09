from pathlib import Path

import polars as pl


if __name__ == '__main__':
    LATITUDE_PLACEHOLDER = 0
    LONGITUDE_PLACEHOLDER = 0
    BATCH = 1

    filename = Path("")
    trap_info_path = Path("/mnt/data/Yunta-Axia_revised_raw/Yunta")
    if BATCH:
        trap_infos = trap_info_path.glob('*/YunTa2020*.csv')
        trap_info_raw = pl.concat(
            [
                pl.read_csv(f, 
                    encoding='GBK', 
                    skip_rows=1, 
                    dtypes={"deploymentID": pl.Utf8,
                        "timestampProblem": pl.Boolean,
                        "coordinateUncertainty": pl.Utf8,})
                        .with_columns(pl.lit(Path(f).stem).alias("collectionName")) #TODO just a temporary fix for Yunta
                for f in trap_infos
            ],
            how="diagonal"
        )
    else:
        trap_info_raw = pl.read_csv(trap_info_path.joinpath(filename),
            encoding='GBK',
            skip_rows=1)

    trap_info_cleaned = trap_info_raw.select(
        pl.col("deploymentID",
            "latitude",
            "longitude",
            "setupBy",
            "cameraModel",
            "exifTimeProblem",
            "timestampProblem",
            "deploymentComments",
            "collectionName"),
        # ISO 8601 / RFC 3339 date & time format
        pl.col("deploymentStart", "deploymentEnd")
            .str.to_datetime()
            .dt.replace_time_zone(time_zone="Asia/Shanghai")
            .dt.to_string("%Y-%m-%dT%H:%M:%S%:z"))

    trap_info_tags = trap_info_cleaned.with_columns( 
        # 
        pl.when(pl.col("latitude").is_not_null())
            .then(pl.lit("coordinate:GPS"))
            .otherwise(pl.lit("coordinate:guess"))
            .alias("coordinateSource"),
        pl.when(pl.col("exifTimeProblem"))
            .then(pl.lit("exifIssue"))
            .otherwise(pl.lit(""))
            .alias("exifIssue"),
        pl.when(pl.col("timestampProblem"))
            .then(pl.lit("true"))
            .otherwise(pl.lit("false"))
            .alias("timestampIssue"),
        
    )
    # print(trap_info_tags)

    # Patch location
    trap_info_patch = trap_info_tags.with_columns(
        pl.col("latitude").fill_null(pl.lit(LATITUDE_PLACEHOLDER)), 
        pl.col("longitude").fill_null(pl.lit(LONGITUDE_PLACEHOLDER)),
    )
    # print(trap_info_patch)

    deployments = trap_info_patch.select(
        #TODO just a temporary fix for Yunta
        pl.concat_str([
            pl.col("deploymentID"),
            pl.col("collectionName")
        ], separator='_').alias("deploymentID"), 

        pl.col("latitude",
            "longitude",
            "deploymentStart",
            "deploymentEnd",
            "setupBy",
            "cameraModel",
            "deploymentComments"),
            
        pl.concat_str([
            pl.col("coordinateSource"),
            pl.col("exifIssue"),
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
    else:
        deployments.write_csv(Path("./").joinpath(filename.stem+'_deployments.csv'))