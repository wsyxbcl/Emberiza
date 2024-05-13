import argparse
import os
import shutil

# Flatten directiory with given name in given path
def flatten_dir(root_dir, dir_name):
    for root, dirs, files in os.walk(root_dir):
        if os.path.basename(root) == dir_name:
            for file in files:
                shutil.move(os.path.join(root, file), os.path.join(os.path.dirname(root), file))
                print("Move {} to {}".format(os.path.join(root, file), os.path.join(os.path.dirname(root), file)))
            shutil.rmtree(root)
            print("Remove {}".format(root))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('dir_name')
    args = parser.parse_args()
    flatten_dir(args.root_dir, args.dir_name)