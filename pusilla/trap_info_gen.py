from datetime import date, time
import csv

import xlsxwriter

workbook = xlsxwriter.Workbook("../test/trap_info_template.xlsx")
worksheet = workbook.add_worksheet()

# Add a format for the header cells.

# Set up layout of the worksheet.
worksheet.set_column("A:A", 68)
worksheet.set_column("B:B", 15)
worksheet.set_column("D:D", 15)
worksheet.set_row(0, 36)

with open("./trap_info_header.csv") as csvfile:
    reader = csv.reader(csvfile)
    for i, heading in enumerate(reader):
        worksheet.write(xlsxwriter.utility.xl_col_to_name(i)+"1", heading[0])
        worksheet.write(xlsxwriter.utility.xl_col_to_name(i)+"2", heading[1])

workbook.close()