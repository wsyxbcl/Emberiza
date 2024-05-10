# Randomly sample resource listed in tags.csv
# based on given set of species its ratio

import polars as pl

### Configuration
RAMDOM_SEED = 42
NUM_SAMPLES = 10000000
SPECIES_RATIO = {
    "Snow leopard": 0.2,
    "Blank": 0.5,
    "Human": 0.3
}
TAGS_CSV_PATH = "/home/wsyxbcl/AngSai/batch_202304/tags.csv"


output_csv_path = TAGS_CSV_PATH.replace(".csv", "_sampled.csv")
df = pl.read_csv(tags_csv_path)
samples = []
for species, ratio in SPECIES_RATIO.items():
    df_species = df.filter(pl.col("species") == species)
    num_resource = int(NUM_SAMPLES * ratio)
    df_species_sample = df_species.sample(num_resource, seed=RAMDOM_SEED)
    samples.append(df_species_sample)

df_sample = pl.concat(samples, how="vertical")
df_sample.write_csv(output_csv_path, include_bom=True)