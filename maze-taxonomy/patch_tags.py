# Patch tags.csv with tagdict and taglist
# Usage: python patch_tags.py tags.csv -o tags_patched.csv

import argparse
import polars as pl
from pathlib import Path

# exclude_tags = [""]
TAGLIST_PATH = Path(__file__).parent / "data/maze_taglist.csv"
TAGDICT_PATH = Path(__file__).parent / "data/maze_tagdict.csv"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Patch tags.csv with tagdict and taglist"
    )
    parser.add_argument("tags", type=str, help="Input tags csv file")
    parser.add_argument(
        "-o", "--output", type=str, help="Output (patched) tags csv file", required=True
    )

    args = parser.parse_args()

    df_maze_taglist = pl.read_csv(TAGLIST_PATH)
    df_maze_tagdict = pl.read_csv(TAGDICT_PATH, has_header=False)
    df_maze_tagdict_concat = df_maze_tagdict.select(
        [
            pl.col("column_1").alias("tag"),
            pl.concat_list(df_maze_tagdict.columns[1:])
            .alias("synonym")
            .list.drop_nulls(),
        ]
    )
    maze_tagdict = dict(df_maze_tagdict_concat.iter_rows())
    maze_synonym_dict = {}
    for k in maze_tagdict.keys():
        for v in maze_tagdict[k]:
            maze_synonym_dict[v] = k

    df_tags_csv = (
        pl.read_csv(args.tags)
        # .drop_nulls()
        .with_columns(pl.col("species").alias("species_old"))
    )
    # Analyze tags and add case sensitivity to tagdict
    tags_taglist = df_maze_taglist.select("tag").to_series().to_list()
    tags_tagdict = df_maze_tagdict_concat.select("tag").to_series().to_list()
    tags_csv = df_tags_csv.select("species_old").unique().to_series().to_list()
    for tag in tags_csv:
        if tag in tags_taglist:
            continue
        # elif tag in exclude_tags:
        #     print(f"EXCLUDE: {tag}")
        elif tag.lower() in (tags_taglist_lower := [t.lower() for t in tags_taglist]):
            tag_corrected = tags_taglist[tags_taglist_lower.index(tag.lower())]
            print(f"CASE INSENSITIVE: {tag} -> {tag_corrected}")
            maze_synonym_dict[tag] = tag_corrected
        # space or '-' miss match
        elif tag.replace("-", "").replace(" ", "") in (tags_taglist_strip := [t.replace("-", "").replace(" ", "") for t in tags_taglist]):
            tag_corrected = tags_taglist[tags_taglist_strip.index(tag.replace("-", "").replace(" ", ""))]
            print(f"SPACE/HYPHEN: {tag} -> {tag_corrected}")
            maze_synonym_dict[tag] = tag_corrected
        elif tag.lower() in (
            maze_synonym_dict_lower := {    
                k.lower(): v for k, v in maze_synonym_dict.items()
            }
        ):
            tag_corrected = maze_synonym_dict_lower[tag.lower()]
            maze_synonym_dict[tag] = tag_corrected
            print(f"SYNONYM: {tag} -> {tag_corrected}")
        else:
            print(f"UNKNOWN: {tag}")

    # Patch tags
    df_tags_csv = df_tags_csv.with_columns(
        pl.col("species_old").replace(maze_synonym_dict).alias("species"),
    )
    df_tags_csv.write_csv(args.output)
