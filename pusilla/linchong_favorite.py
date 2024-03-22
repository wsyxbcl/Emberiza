# Workaround for marking all images in given directory as favorite in Photoprism
# Based on https://github.com/photoprism/photoprism/pull/1873

import argparse
import os
import shutil

def mark_favorite(image_dir):
    '''
    create xmp files (favorite) for all images in the directory recursively
    '''
    xmp_file_path = "./assets/fstop-favorite.xmp"
    for root, dirs, files in os.walk(image_dir):
        for file in files:
            if file.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                xmp_file = os.path.join(root, file+".xmp")
                shutil.copyfile(xmp_file_path, xmp_file)
                print(f"Created {xmp_file}")

def remove_xmp(image_dir):
    '''
    remove all xmp files in the directory recursively
    '''
    for root, dirs, files in os.walk(image_dir):
        for file in files:
            if file.endswith('.xmp'):
                xmp_file = os.path.join(root, file)
                os.remove(xmp_file)
                print(f"Removed {xmp_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('image_dir')
    # two subcommands: favorite and rmxmp
    parser.add_argument('subcommand', choices=['favorite', 'rmxmp'])
    args = parser.parse_args()
    if args.subcommand == 'favorite':
        mark_favorite(args.image_dir)
    elif args.subcommand == 'rmxmp':
        remove_xmp(args.image_dir)


