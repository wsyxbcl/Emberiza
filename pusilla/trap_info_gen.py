import argparse
from datetime import date, time
import os
import csv

import xlsxwriter

parser = argparse.ArgumentParser()
parser.add_argument('project_dir')
args = parser.parse_args()

collection_list = next(os.walk(args.project_dir))[1]

for collection in collection_list:
    collection_dir = os.path.join(args.project_dir, collection)
    workbook = xlsxwriter.Workbook(os.path.join(collection_dir, "trap_info_template.xlsx"))
    worksheet = workbook.add_worksheet()
    print("Opening "+collection_dir+" as collection")
    num_dir_ignored = 0
    for (deployment_idx, deployment) in enumerate(next(os.walk(collection_dir))[1]):
        if "精选" in deployment or deployment == ".dtrash":
            print("\tSkipping "+deployment)
            num_dir_ignored += 1
            continue
        print("\tAdding "+deployment)
        col_idx = {}
        with open("./assets/trap_info_header.csv", encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for heading_idx, heading in enumerate(reader):
                index = xlsxwriter.utility.xl_col_to_name(heading_idx)
                worksheet.write(index+'1', heading[0])
                worksheet.write(index+'2', heading[1])
                worksheet.set_column(index+":"+index, 20) # Set up layout of the worksheet.
                col_idx[heading[1]] = index

        row_idx = str(deployment_idx - num_dir_ignored + 3)
        # Deployment_names
        worksheet.write('A'+row_idx, deployment)
        # Drop-down lists
        worksheet.data_validation(
            col_idx["locationSource"]+row_idx, 
            {"validate": "list", "source": ["估计GPS", "精确GPS"]}
        )
        worksheet.data_validation(
            col_idx["timestampProblem"]+row_idx, 
            {"validate": "list", "source": ["有问题", "无问题", "有问题但已精确校正"]}
        )
        worksheet.data_validation(
            col_idx["exifTimeProblem1Revised"]+row_idx, 
            {"validate": "list", "source": ["已校正", "未校正"]}
        )
        worksheet.data_validation(
            col_idx["exifTimeProblem2Revised"]+row_idx, 
            {"validate": "list", "source": ["已校正", "未校正"]}
        )
        worksheet.data_validation(
            col_idx["otherProblem1"]+row_idx, 
            {"validate": "list", "source": ["照片损坏", "未有效工作", "相机位置移动", "其它(在备注中注明)"]}
        )
        worksheet.data_validation(
            col_idx["otherProblem2"]+row_idx, 
            {"validate": "list", "source": ["照片损坏", "未有效工作", "相机位置移动", "其它(在备注中注明)"]}
        )
    workbook.close()