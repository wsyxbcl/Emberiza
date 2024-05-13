# Randomly sample resource listed in tags.csv
# based on given set of species its ratio

import polars as pl

#### Configurations ####
# 采样时，若某个物种的资源数量不足，会全部采样
# tags.csv 中不包含目标物种资源时，会跳过

TAGS_CSV_PATH = "/home/wsyxbcl/AngSai/tags_patched_new.csv"
RAMDOM_SEED = 42
NUM_SAMPLES = 750

SPECIES_RATIO = {
    "Snow leopard": 0.2,
    "Blank": 0.5,
    "Human": 0.3,
    "test": 0.2,
}

USE_CSV = True  # 是否从 csv 文件中读取物种比例，若为 False 则使用上面的 SPECIES_RATIO
SPECIES_RATIO_CSV = "/home/wsyxbcl/Downloads/tencent_sample_ratio.csv"
########################


output_csv_path = TAGS_CSV_PATH.replace(".csv", "_sampled.csv")
if USE_CSV:
    df_species_ratio = pl.read_csv(SPECIES_RATIO_CSV, new_columns=["species", "ratio"])
    SPECIES_RATIO = dict(
        zip(df_species_ratio["species"].to_list(), df_species_ratio["ratio"].to_list())
    )
df = pl.read_csv(TAGS_CSV_PATH).select(["path", "species"])
samples = []
for species, ratio in SPECIES_RATIO.items():
    num_resource = int(NUM_SAMPLES * ratio)
    df_species = df.filter(pl.col("species") == species)
    try:
        df_species_sample = df_species.sample(num_resource, seed=RAMDOM_SEED)
    except pl.exceptions.ShapeError:
        df_species_sample = df_species
    print(
        f"Species: {species}, Aimed: {num_resource}, Sampled: {len(df_species_sample)}/{len(df_species)}"
    )
    samples.append(df_species_sample)

df_sample = pl.concat(samples, how="vertical")
df_sample.write_csv(output_csv_path, include_bom=True)
