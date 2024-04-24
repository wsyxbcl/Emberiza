# Extract individual information from linchong photoprism sidecar files (yaml)
# Usage: python linchong_individual_extract.py <directory> <output_file>

import os
import csv
import argparse
import yaml
import pandas as pd

# walk through the directory and find all yaml files
def find_yaml_files(directory):
    yaml_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.yml'):
                yaml_files.append(os.path.join(root, file))
    return yaml_files

def extract_individual_info(yaml_files):
    title_list = []
    individual_list = []
    for yaml_file in yaml_files:
        with open(yaml_file, "r") as f:
            data = yaml.safe_load(f)
        title = data["Title"]
        print(title)
        try:
            description = data['Description']
        except KeyError:
            continue
        if title in title_list:
            continue
        if len(title.split('-')) == 3:
            location, name, label = title.split('-')
        elif len(title.split('-')) == 2:
            location, label = title.split('-')
            name = ""
        else:
            print(f"Invalid title format: {title}")
            continue
        if "adult" in data['Details']['Keywords']:
            age = "adult"
        elif "cub" in data['Details']['Keywords']:
            age = "cub"
        if "雪豹" in data['Description']:
            species = "雪豹"
        elif "金钱豹" in data['Description']:
            species = "金钱豹"
        else:
            species = ""
        individual_list.append([title, location, name, label, age, species, description])
    return individual_list

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract individual info from linchong photoprism sidecar files (yaml)")
    parser.add_argument('directory')
    parser.add_argument('output_file')
    args = parser.parse_args()
    
    yaml_files = find_yaml_files(args.directory)
    individual_list = extract_individual_info(yaml_files)
    df = pd.DataFrame(individual_list, columns=["Title", "Location", "Name", "Label", "Age", "Species", "Description"])
    df.to_csv(args.output_file, index=False)
    print(f"Individual info written to {args.output_file}")
