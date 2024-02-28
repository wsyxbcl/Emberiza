import exiftool

def xmp_to_taglist(input_file):
    with exiftool.ExifToolHelper() as et:
        metadata = et.get_metadata(input_file)
    taglist = [tag.split("/")[1] for tag in metadata[0]["XMP:TagsList"]]
    return taglist