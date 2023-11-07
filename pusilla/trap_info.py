import pathlib

import polars as pl


if __name__ == '__main__':
    #TODO Batch trap_info converting
    trap_info_path = pathlib.Path("")
    trap_info_raw = pl.read_csv(trap_info_path.joinpath(""),
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
            "deploymentComments"),
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

    trap_info_patch = trap_info_tags.with_columns(
        pl.col("latitude").fill_null(pl.lit(33.6)), 
        pl.col("longitude").fill_null(pl.lit(96.4))
    )
    # print(trap_info_patch)

    deployments = trap_info_patch.select(
        pl.col("deploymentID",
            "latitude",
            "longitude",
            "deploymentStart",
            "deploymentEnd",
            "setupBy",
            "cameraModel",
            "deploymentComments"),
        pl.concat_str(
            [
                pl.col("coordinateSource"),
                pl.col("exifIssue"),
            ],
            separator=" | "
        ).alias("deploymentTags")
    )
    print(deployments)
    