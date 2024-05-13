# Convert trapper-client generated yaml file to csv
# Usage: python trapper-yaml2csv.py <input_yaml> <output_csv>

import sys
import yaml
import csv
from zoneinfo import ZoneInfo
from datetime import datetime


def yaml2csv(input_yaml, output_csv):
    with open(input_yaml, "r") as f:
        data = yaml.safe_load(f)
    with open(output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        for collection in data["collections"]:
            for deployment in collection["deployments"]:
                for resource in deployment["resources"]:
                    trapper_datetime = (
                        datetime.fromisoformat(resource["date_recorded"])
                        .astimezone(ZoneInfo("Asia/Shanghai"))
                        .strftime("%Y-%m-%d %H:%M:%S")
                    )
                    writer.writerow(
                        [
                            collection["name"],
                            deployment["deployment_id"],
                            resource["file"],
                            trapper_datetime,
                        ]
                    )


if __name__ == "__main__":
    yaml2csv(sys.argv[1], sys.argv[2])
