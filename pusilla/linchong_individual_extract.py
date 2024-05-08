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
    individuals = {}
    def count_body_part(individual, keywords):
        if "模糊" in keywords:
            for keyword in keywords:
                if keyword in body_parts_count:
                    individual[keyword+"模糊"] += 1
        else:
            for keyword in keywords:
                if (keyword in body_parts_count) or (keyword in blurred_body_parts_count):
                    individual[keyword] += 1
    for yaml_file in yaml_files:
        with open(yaml_file, "r") as f:
            data = yaml.safe_load(f)
        title = data["Title"]
        print(f"Processing {title}")        
        try:
            description = data['Description']
        except KeyError:
            continue
        # anaylze keywords
        keywords = [keyword.strip() for keyword in data['Details']['Keywords'].split(',')]
        # remove duplicates and count body parts
        if title in individuals.keys():
            count_body_part(individuals[title], keywords)
            continue
        else:
            body_parts_count = {"左侧图": 0, "右侧图": 0, "面部花纹": 0, "尾巴": 0, "前肢花纹": 0, "补充图": 0}
            blurred_body_parts_count = {"左侧图模糊": 0, "右侧图模糊": 0, "面部花纹模糊": 0, "尾巴模糊": 0, "前肢花纹模糊": 0, "补充图模糊": 0}
        if len(title.split('-')) == 3:
            location, name, label = title.split('-')
        elif len(title.split('-')) == 2:
            location, label = title.split('-')
            name = ""
        else:
            print(f"Invalid title format: {title}")
            continue
        if "adult" in keywords:
            age = "adult"
        elif "cub" in keywords:
            age = "cub"
        if "雪豹" in data['Description']:
            species = "雪豹"
        elif "金钱豹" in data['Description']:
            species = "金钱豹"
        else:
            species = ""
        individuals[title] = {"Title": title, "Location": location, "Name": name, "Label": label, "Age": age, "Species": species, "Description": description, **body_parts_count, **blurred_body_parts_count}
        count_body_part(individuals[title], keywords)
    return individuals

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract individual info from linchong photoprism sidecar files (yaml)")
    parser.add_argument('directory')
    parser.add_argument('output_file')
    args = parser.parse_args()
    
    yaml_files = find_yaml_files(args.directory)
    individuals = extract_individual_info(yaml_files)
    # df = pd.DataFrame(individual_list, columns=["Title", "Location", "Name", "Label", "Age", "Species", "Description", "左侧图", "右侧图", "面部花纹", "尾巴", "前肢花纹", "补充图"])
    df = pd.DataFrame(individuals.values())
    df.to_csv(args.output_file, index=False, encoding="utf-8-sig")
    print(f"Individual info written to {args.output_file}")
