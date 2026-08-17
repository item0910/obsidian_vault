---
title: 数字经验_导出Calibre书单
date: 2024-11-08
categories: 数字经验
tags: 归档笔记/生活经验/数字经验
author: 自己
mtime: 2024-12-27
---

## **主要流程总结：**

1. **导出 Calibre 书单：** 在 Calibre 中使用工具栏的"转换书籍"->"编制书目" 功能，导出书单为 CSV 格式。
2. **使用脚本处理 CSV：** 通过 `8calibre书单处理.py` 脚本将 CSV 文件转换为 Excel 文件，并进行一系列处理：
    - 插入新列并处理图片路径（插入图片并调整大小）。
    - 格式化日期列为 `YYYY-MM-DD` 格式。
    - 更新表头，调整列宽，设置单元格字体（如设置为 `Courier New`）并添加边框。
3. **调整格式：** 设置全局字体、冻结首行，调整列宽，并为第一行应用特定格式（如加粗、居中）。
4. **保存输出：** 将处理后的 Excel 文件保存在桌面，文件名带有时间戳。

## 导出 calibre 书单

1. 在 calibre 内: 主工具栏: 转换书籍内
2. 用 `8calibre书单处理.py` 脚本, 基本上已经都调好了, 文件名也可以按照默认的 1.csv 来操作, 注意不要更改 calibre 里的导出项即可
3. 移一下图片, 漏出线
4. 全选, 设置单元格格式, 字体:Courier New(不知为何双击会改变字体, 这样设置不会)

```python
import openpyxl
import pandas as pd
import os
from io import BytesIO
from datetime import datetime
from openpyxl.drawing.image import Image
from openpyxl.styles import NamedStyle, Font, Border, Side, Alignment




# CSV 文件路径
csv_file = 'C://Users//Administrator//Desktop//1.csv'
image_column_index = 7  # 图片路径在第七列（0开始计数）
insert_after_column_index = 3  # 在 D 列（索引 3）后插入新列

# Step 1: 将 CSV 文件转换为内存中的 Excel 文件
try:
    df = pd.read_csv(csv_file)
    buffer = BytesIO()
    df.to_excel(buffer, index=False)  # 将Excel文件写入内存
    buffer.seek(0)
    print(f"CSV file '{csv_file}' successfully converted to in-memory Excel.")
except Exception as e:
    print(f"Failed to convert CSV to Excel: {e}")
    exit()

# 调整列宽度
def adjust_column_width(ws):
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter  # 获取列字母
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column].width = adjusted_width
        print(f"Adjusted width of column {column} to {adjusted_width}")

# 为单元格设置边框

def freeze_first_row(ws):
    """
    冻结工作表的第一行。
    
    Parameters:
    - ws (Worksheet): 要冻结首行的工作表
    """
    ws.freeze_panes = 'A2'
    print("First row frozen.")


def set_borders(ws, thin_border_width=1, thick_border_width=2):
    """
    为工作表中的单元格设置边框。
    
    Parameters:
    - ws (Worksheet): 要设置边框的工作表
    - thin_border_width (int): 细边框的宽度，默认为1
    - thick_border_width (int): 粗边框的宽度，默认为2
    """
    # 创建细边框和粗边框，根据传入的样式
    thin_border = Border(left=Side(style='thin'),
                         right=Side(style='thin'),
                         top=Side(style='thin'),
                         bottom=Side(style='thin'))
    
    thick_border = Border(left=Side(style='thick'),
                          right=Side(style='thick'),
                          top=Side(style='thick'),
                          bottom=Side(style='thick'))

    # 遍历所有单元格并设置边框
    for row in ws.iter_rows():
        for cell in row:
            if cell.row == 1:  # 第一行加粗边框(太粗暂时放弃)
                cell.border = thin_border
            else:  # 其他行加细边框
                cell.border = thin_border

    print(f"Borders set for all cells with thin border style 'thin' and thick border style 'thick'.")



# 创建或获取 date_style 一次，避免重复创建错误
def get_or_create_date_style(wb):
    # Check if date_style already exists, ensuring `named_styles` entries are style objects
    for style in wb.named_styles:
        if isinstance(style, NamedStyle) and style.name == "date_style":
            print("Using existing date style.")
            return style
    # Create date_style if it does not exist
    date_style = NamedStyle(name="date_style", number_format="YYYY-MM-DD")
    wb.add_named_style(date_style)
    print("Created new date style.")
    return date_style



# 应用日期格式
def format_date_column(ws, col_index, date_style):
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=col_index, max_col=col_index):
        for cell in row:
            if isinstance(cell.value, str) and len(cell.value) >= 10:
                cell.value = cell.value[:10]
                cell.style = date_style
                print(f"Formatted date in cell {cell.coordinate} as YYYY-MM-DD")

def set_global_font(ws, font_name='Courier New', bold_first_row=False, enlarge_first_row=False, center_first_row=False):
    """
    设置工作表中所有单元格的字体，并可选地修改第一行的字体，居中设置。
    
    Parameters:
    - ws (Worksheet): 要设置字体的工作表
    - font_name (str): 要设置的字体名称，默认为 'Courier New'
    - bold_first_row (bool): 是否加粗第一行字体，默认为 False
    - enlarge_first_row (bool): 是否将第一行字体大小设置为 14，默认为 False
    - center_first_row (bool): 是否将第一行文字居中，默认为 False
    """
    # 设置全局字体
    font = Font(name=font_name)
    
    # 遍历所有单元格并设置字体
    for row in ws.iter_rows():
        for cell in row:
            # 第一行加粗字体和调整字体大小
            if cell.row == 1:
                font_kwargs = {'name': font_name}
                if bold_first_row:
                    font_kwargs['bold'] = True
                if enlarge_first_row:
                    font_kwargs['size'] = 14  # 设置第一行字体大小为 14
                
                # 创建合并后的字体对象
                cell.font = Font(**font_kwargs)
                
                # 设置首行字体居中
                if center_first_row:
                    cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.font = font

    print(f"Set all cell fonts to {font_name}. First row bold: {bold_first_row}. First row enlarged: {enlarge_first_row}. First row centered: {center_first_row}.")

def insert_images(ws, image_column_index, insert_after_column_index, image_width=100, image_height=135):
    """
    插入图片到指定列后，并设置图片大小和行高。
    
    Parameters:
    - ws (Worksheet): 要操作的工作表
    - image_column_index (int): 图片路径所在的列索引（从0开始）
    - insert_after_column_index (int): 图片插入的列索引（从0开始）
    - image_width (int): 设置图片的宽度，默认为 100
    - image_height (int): 设置图片的高度，默认为 135
    """
    for row in ws.iter_rows(min_row=2):
        image_path = row[image_column_index].value
        if image_path and os.path.exists(image_path):
            try:
                img = Image(image_path)
                print(f"Loaded image from '{image_path}'")

                # 设置图片大小
                img.width = image_width
                img.height = image_height

                # 插入图片
                cell_coordinate = ws.cell(row=row[0].row, column=insert_after_column_index + 1).coordinate
                img.anchor = cell_coordinate
                ws.add_image(img)
                print(f"Inserted image at {cell_coordinate}")

                # 增加行高以适应图片
                ws.row_dimensions[row[0].row].height = image_height - 30 # 留出一些间距
            except Exception as e:
                print(f"Failed to insert image '{image_path}' at row {row[0].row}: {e}")
        else:
            print(f"No image path or file does not exist for row {row[0].row}")


try:
    # 打开内存中的工作簿
    wb = openpyxl.load_workbook(buffer)
    ws = wb.active
    print("Successfully loaded workbook from in-memory buffer.")

    # 插入空白列
    ws.insert_cols(insert_after_column_index + 1)
    print("Inserted new column successfully.")

    # 插入图片
    insert_images(ws, image_column_index=7, insert_after_column_index=3)
    
    # 获取或创建日期格式样式
    date_style = get_or_create_date_style(wb)


    # 删除图片路径列
    ws.delete_cols(image_column_index + 1)
    print(f"Deleted image path column at index {image_column_index + 1}")

    # 格式化日期列
    format_date_column(ws, 6, date_style)  # F 列
    format_date_column(ws, 8, date_style)  # H 列
    format_date_column(ws, 13, date_style)  # N 列

    # 更新列标题
    new_headers = ["id", "书名", "作者", "封面", "出版社", "首次出版日期", "字数", "日期", "标签", "推荐则值为1","译者", "语言", "阅读完成时间"]
    for col_num, header in enumerate(new_headers, start=1):
        ws.cell(row=1, column=col_num, value=header)
    print("Updated header row with new column names.")

    # 调整列宽
    adjust_column_width(ws)

    # 设置 D 列的列宽约为 105 像素
    ws.column_dimensions['B'].width = 50
    ws.column_dimensions['D'].width = 14
    ws.column_dimensions['F'].width = 16
    ws.column_dimensions['I'].width = 29
    ws.column_dimensions['J'].width = 15
    ws.column_dimensions['M'].width = 16
    
    print("Set columns width to approximately pixels.")

    # 设置所有单元格边框
    set_borders(ws, 1, 1)  # 设置细边框宽度为 1，粗边框宽度为 1

    # 设置全局字体为 Courier New
    set_global_font(ws, font_name='Courier New', bold_first_row=True, enlarge_first_row=True, center_first_row=True)

    # 冻结首行
    freeze_first_row(ws)
    
    # 获取桌面路径
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

    # 保存文件，使用时间戳，并指定路径为桌面
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    updated_file = os.path.join(desktop_path, f'updated_1_{timestamp}.xlsx')


    # 保存工作簿
    wb.save(updated_file)
    print(f"Workbook saved as '{updated_file}'")

except Exception as e:
    print(f"An error occurred: {e}")


```
