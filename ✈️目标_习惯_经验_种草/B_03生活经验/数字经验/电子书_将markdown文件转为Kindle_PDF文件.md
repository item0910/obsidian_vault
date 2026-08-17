---
title: 数字经验_电子书_将markdown文件转为Kindle_PDF文件
date: 2024-11-23
categories: Kindle
tags: 归档笔记/生活经验/数字经验
author: 自己
mtime: 2024-12-27
---

## **主要流程总结：**

1. **Markdown 转 Docx：**
    - 使用 Obsidian 或 Typora 将 Markdown 文件转换为 Docx 格式。
2. **处理 Docx 文件：**
    - 使用 `文字处理_把1docx转化为1pdf.py` 脚本对 Docx 文件进行处理：
        - 调整字体大小：每个段落和表格的字体增加两号。
        - 设置表格内边框：添加表格的垂直和水平边框。
        - 设置窄页边距：调整页面的边距为 0.5 英寸。
        - 调整行距：设置为 1.2 倍行距。
3. **转换为 PDF：**
    - 使用 `comtypes` 和 Microsoft Word 将处理后的 Docx 文件转换为 PDF。
4. **清理：**
    - 删除临时处理后的 Docx 文件，并输出最终的 PDF 文件。

- 目标:
	1. 将字体调整到 kindle 合适的观感 (加两号)
	2. 将 md 的表格内部加上表格线
	3. 将页边距缩小
	4. 将 docx 直接转换为 pdf

1. markdown 转为 docx
	1. obsidian 直接唤醒控制台, pandoc_docx 转换
	2. typora 可以另存为直接转换
2. 然后用 `文字处理_把1docx转化为1pdf.py`, 处理 1.docx, 可以直接转换为 pdf

```python
import os
import comtypes.client
from docx import Document
from docx.shared import Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_LINE_SPACING

# 定义字号与磅值的对应关系
font_sizes = [
    (42, '初号'),
    (36, '小初'),
    (26, '一号'),
    (24, '小一'),
    (22, '二号'),
    (18, '小二'),
    (16, '三号'),
    (15, '小三'),
    (14, '四号'),
    (12, '小四'),
    (10.5, '五号'),
    (9, '小五'),
    (7.5, '六号'),
    (6.5, '小六'),
    (5.5, '七号'),
    (5, '八号'),
]

# 创建一个从磅值到索引的映射
size_to_index = {size: idx for idx, (size, _) in enumerate(font_sizes)}

def increase_font_size(size_pt):
    sizes = [size for size, _ in font_sizes]
    closest_size = min(sizes, key=lambda x: abs(x - size_pt))
    index = size_to_index.get(closest_size, sizes.index(12))  # 默认12pt（小四）
    new_index = max(0, index - 2)  # 增大2号，越往前字号越大
    return font_sizes[new_index][0]

def set_table_inner_borders(table):
    tbl = table._element
    tblPr = tbl.find(qn('w:tblPr'))
    if tblPr is None:
        tblPr = OxmlElement('w:tblPr')
        tbl.append(tblPr)
    tblBorders = tblPr.find(qn('w:tblBorders'))
    if tblBorders is None:
        tblBorders = OxmlElement('w:tblBorders')
        tblPr.append(tblBorders)
    for b in ('insideH', 'insideV'):
        e = tblBorders.find(qn(f'w:{b}'))
        if e is not None:
            tblBorders.remove(e)
    for border_name in ('insideH', 'insideV'):
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), 'single')
        border.set(qn('w:sz'), '4')  # 边框厚度
        border.set(qn('w:space'), '0')
        border.set(qn('w:color'), 'auto')
        tblBorders.append(border)

def set_narrow_margins(doc):
    # 设置窄页边距
    sections = doc.sections
    for section in sections:
        section.top_margin = Pt(14.2)  # 0.5英寸
        section.bottom_margin = Pt(14.2)
        section.left_margin = Pt(14.2)
        section.right_margin = Pt(14.2)

def process_docx(input_file, output_file):
    # 打开 docx 文件
    doc = Document(input_file)

    # 设置窄页边距
    set_narrow_margins(doc)

    # 调整段落字体大小和行距
    for paragraph in doc.paragraphs:
        paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
        paragraph.paragraph_format.line_spacing = 1.2
        for run in paragraph.runs:
            current_size = run.font.size.pt if run.font.size else 12
            new_size = increase_font_size(current_size)
            run.font.size = Pt(new_size)

    # 调整表格字体大小和行距，并添加内边框
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
                    paragraph.paragraph_format.line_spacing = 1.2
                    for run in paragraph.runs:
                        current_size = run.font.size.pt if run.font.size else 12
                        new_size = increase_font_size(current_size)
                        run.font.size = Pt(new_size)
        set_table_inner_borders(table)

    # 保存临时修改后的文件
    doc.save(output_file)

def convert_docx_to_pdf(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"错误：文件未找到 - {input_file}")
        return
    word = comtypes.client.CreateObject('Word.Application')
    word.Visible = False
    doc = None
    try:
        # 打开文档
        doc = word.Documents.Open(os.path.abspath(input_file))
        # 保存为 PDF
        doc.SaveAs(os.path.abspath(output_file), FileFormat=17)
        print(f"PDF 文件已生成：{output_file}")
    except Exception as e:
        print(f"转换失败: {e}")
    finally:
        if doc:
            doc.Close()
        word.Quit()

# 主逻辑：处理文档并直接转换为 PDF
input_docx = r"1.docx"
temp_docx = r"1_temp.docx"
output_pdf = r"1.pdf"

print("正在处理文档...")
process_docx(input_docx, temp_docx)

# 检查临时文件是否生成
if os.path.exists(temp_docx):
    print("正在转换为 PDF...")
    convert_docx_to_pdf(temp_docx, output_pdf)
    os.remove(temp_docx)
    print("临时文件已删除。")
else:
    print("处理文档时出现问题，未生成临时文件。")

print("操作完成！")

```
