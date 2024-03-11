# Workaround for serval capture on unaligned AS data
import pandas as pd

tags_csv_path = "~/Downloads/tags.csv"
output_csv_path = "~/Downloads/tags_path_split.csv"

df = pd.read_csv(tags_csv_path)

# Path splitting
split_values = df["path"].str.split("\\", expand=True)
df["path"] = '/' + split_values[5] + '/' + split_values[6] + '/dummy.jpg'

# Save
df.to_csv(output_csv_path, index=False)
