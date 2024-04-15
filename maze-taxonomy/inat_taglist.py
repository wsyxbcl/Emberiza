from pyinaturalist import *
import polars as pl

# Only search for taxa under species
df_maze_taglist = pl.read_csv("./data/maze_taglist.csv").filter(pl.col("rank").is_in(["species", "subspecies"]))

scientific_names = df_maze_taglist.select("scientificName").to_series().to_list()
ranks = df_maze_taglist.select("rank").to_series().to_list()

inat_name_en = []
inat_name_cn = []
inat_scientific_names = []
inat_conservations = []
inat_id = []

# Search for taxa
for i, scientific_name in enumerate(scientific_names):
    # response = get_taxa(q=latin_name, rank=['species'], is_active=True, all_names=True, taxon_id=355675, locale=['zh-CN'])
    response = get_taxa(q=scientific_name, rank=['species', 'subspecies'], is_active=True, all_names=True, taxon_id=355675, locale=['zh-CN'])
    taxa = Taxon.from_json_list(response)
    # filter wrong ranks
    taxa = [t for t in taxa if t.rank == ranks[i]]

    if len(taxa) == 0:
        print(f"Taxon not found: {scientific_name}")
        inat_name_en.append("")
        inat_name_cn.append("")
        inat_conservations.append("")
        inat_id.append("")
        inat_scientific_names.append("")
        continue
    elif len(taxa) > 1:
        try:
            taxon = [t for t in taxa if t.matched_term == scientific_name][0]
        except IndexError:
            print(f"Multiple taxa found: {scientific_name}")
            pprint(taxa)
            inat_name_en.append("")
            inat_name_cn.append("")
            inat_conservations.append("")
            inat_id.append("")
            inat_scientific_names.append("")
            continue
    else: 
        taxon = taxa[0]
        print(f"Taxon found: {scientific_name}")
        pprint(taxon)
    inat_name_cn.append(taxon.preferred_common_name)
    inat_scientific_names.append(taxon.name)
    try:
        inat_name_en.append([n['name'] for n in taxon.names if (n['locale'] == 'en')][0])
    except IndexError:
        print(f"English name not found?")
        print(taxon.names)
        inat_name_en.append("")
    inat_conservations.append(str(taxon.conservation_status))
    inat_id.append(str(taxon.id))

# Save
df_maze_taglist = df_maze_taglist.with_columns(
    pl.Series("inatNameEn", inat_name_en),
    pl.Series("inatNameCn", inat_name_cn),
    pl.Series("inatConservationStatus", inat_conservations),
    pl.Series("inatID", inat_id),
    pl.Series("inatScientificName", inat_scientific_names)
)

print(df_maze_taglist)
df_maze_taglist.write_csv("../test/maze_taglist_patched.csv")