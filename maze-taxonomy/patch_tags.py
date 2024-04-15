# Patch tags.csv with tagdict and taglist
# Usage: python patch_tags.py tags.csv -o tags_patched.csv

import argparse
import polars as pl

# exclude_tags = []

df_maze_taglist = pl.read_csv("./data/maze_taglist.csv")

df_maze_tagdict = pl.read_csv("./data/maze_tagdict.csv", has_header=False)
df_maze_tagdict = df_maze_tagdict.select([
    pl.col("column_1").alias("tag"),
    pl.concat_list([f"column_{i}" for i in range(2, 10)]).alias("synonym").list.drop_nulls()
])
maze_tagdict = dict(df_maze_tagdict.iter_rows())
maze_synonyms_dict = {}
for k in maze_tagdict.keys():
    for v in maze_tagdict[k]:
        maze_synonyms_dict[v] = k

df_tags_csv = pl.read_csv("/home/wsyxbcl/AngSai/batch2-align/tags.csv").drop_nulls()


# Analyze tags and add case sensitivity to tagdict
tags_taglist = df_maze_taglist.select("tag").to_series().to_list()
tags_tagdict = df_maze_tagdict.select("tag").to_series().to_list()
tags_csv = df_tags_csv.select("species").unique().to_series().to_list()
for tag in tags_csv:
    if tag in tags_taglist:
        continue
    # elif tag in exclude_tags:
    #     print(f"EXCLUDE: {tag}")
        maze_synonyms_dict.setdefault(tag, []).append("")
    elif tag.lower() in (tags_taglist_lower := [t.lower() for t in tags_taglist]):
        tag_corrected = tags_taglist[tags_taglist_lower.index(tag.lower())]
        print(f"CASE INSENSITIVE: {tag} -> {tag_corrected}")
        maze_synonyms_dict.setdefault(tag, []).append(tag_corrected)
    elif tag in maze_synonyms_dict:
        tag_corrected = maze_synonyms_dict[tag]
        print(f"SYNONYM: {tag} -> {tag_corrected}")
    elif tag.lower() in (maze_synonyms_dict_lower := {k.lower(): v for k, v in maze_synonyms_dict.items()}):
        tag_corrected = maze_synonyms_dict_lower[tag.lower()]
        maze_synonyms_dict[tag] = tag_corrected
        print(f"SYNONYM CASE INSENSITIVE: {tag} -> {tag_corrected}")
    else:
        print(f"NEW TAG: {tag}")

# Patch tags
df_tags_csv = df_tags_csv.with_columns(
    pl.col("species").replace(maze_synonyms_dict).alias("tags")
)
df_tags_csv.write_csv("../test/tags_patched.csv")
