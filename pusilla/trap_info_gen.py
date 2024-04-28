# Generate a template for trap_info.xlsx for each collections
# Usage: python trap_info_gen.py <dir> [options]
#   <dir> is the directory containing the collections
#   [options] are optional arguments
#       -p, --project: if the directory is a project directory
#       -h, --help: show this help message and exit

import argparse
from datetime import date, time
import os
import csv

import xlsxwriter

TRAP_INFO_HEADER = [
    ["相机位点名称","deploymentName"], 
    ["监测员","setupBy"], 
    ["纬度","latitude"], 
    ["经度","longitude"], 
    ["位点来源","locationSource"], 
    ["相机工作日时长","cameraWorkingDays"], 
    ["开始时间","deploymentStart"], 
    ["结束时间","deploymentEnd"], 
    ["备注","deploymentComments"], 
    ["照片时间是否有问题","timestampProblem"], 
    ["参考年份","timestampRef"], 
    ["其它问题1","otherProblem1"], 
    ["其它问题1开始时间","otherProblem1Start"], 
    ["其它问题1结束时间","otherProblem1End"], 
    ["时间跳错1开始时间","exifTimeProblem1Start"], 
    ["时间跳错1结束时间","exifTimeProblem1End"], 
    ["时间跳错1是否经过校正","exifTimeProblem1Revised"],
    ["时间跳错1参考年份","exifTimeProblem1Ref"],
    ["其它问题2","otherProblem2"],
    ["其它问题2开始时间","otherProblem2Start"],
    ["其它问题2结束时间","otherProblem2End"],
    ["时间跳错2开始时间","exifTimeProblem2Start"],
    ["时间跳错2结束时间","exifTimeProblem2End"],
    ["时间跳错2是否经过校正","exifTimeProblem2Revised"],
    ["时间跳错2参考年份","exifTimeProblem2Ref"],
]

def trap_info_gen(collection_dir, force=False):
    workbook = xlsxwriter.Workbook(os.path.join(collection_dir, "trap_info_template.xlsx"))
    # check if the file already exists
    if not force:
        if os.path.exists(os.path.join(collection_dir, "trap_info_template.xlsx")):
            overwrite = input("File already exists. Overwrite? (y/n): ")
            if overwrite.lower() != "y":
                return
    worksheet = workbook.add_worksheet()
    print("Opening "+collection_dir+" as collection")
    num_dir_ignored = 0
    for (deployment_idx, deployment) in enumerate(next(os.walk(collection_dir))[1]):
        if "精选" in deployment or deployment == ".dtrash":
            print("\tSkipping "+deployment)
            num_dir_ignored += 1
            continue
        print("\tAdding "+deployment+" to trap_info")
        col_idx = {}
        for header_idx, header in enumerate(TRAP_INFO_HEADER):
            index = xlsxwriter.utility.xl_col_to_name(header_idx)
            worksheet.write(index+'1', header[0])
            worksheet.write(index+'2', header[1])
            worksheet.set_column(index+":"+index, 20) # Set up layout of the worksheet.
            col_idx[header[1]] = index

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
    print("Saved to "+os.path.join(collection_dir, "trap_info_template.xlsx"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('dir')
    parser.add_argument('-p', '--project', action='store_true', help='if the directory is a project directory')
    parser.add_argument('-f', '--force', action='store_true', help='force overwrite')
    args = parser.parse_args()
    if args.project:
        collection_list = next(os.walk(args.dir))[1]
        for collection in collection_list:
            collection_dir = os.path.join(args.dir, collection)
            trap_info_gen(collection_dir)
    else:
        trap_info_gen(args.dir)

    # Freeze the terminal
    if os.name == 'nt':
        os.system("pause")
    else:
        os.system("read -n 1 -s -p \"Press any key to continue...\"")