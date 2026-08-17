---
title: 文件处理_将问题列表Anki化
date: 2024-11-24
categories: 脚本
tags: 电子经验
author: 自己
mtime: 2024-11-25
---

1. 将问题都整成 `- **问 010: 巴拉巴拉**` 这样的格式 (这一步还没有脚本化)

### 1. 重排序问题脚本:

```python
import re

# 文件路径
input_file_path = "1.md"
output_file_path = "2.txt"

# 读取文件内容
with open(input_file_path, "r", encoding="utf-8") as file:
    lines = file.readlines()

# 自增变量和日志列表
counter = 1
log = []
matched_lines = []  # 用于存储匹配到的行

# 正则表达式匹配：支持所有可能的缩进格式
pattern = re.compile(r"(\s*- \*\*问 )(\d{3})([:：])")

# 更新匹配的数字
def replace_with_increment(match):
    global counter
    old_number = match.group(2)
    new_number = f"{counter:03}"
    matched_line = match.group(0)
    log.append(f"匹配行: '{matched_line}' -> 修改为: '{match.group(1)}{new_number}{match.group(3)}'")
    matched_lines.append(matched_line.strip())  # 去掉多余的空白符保存到列表
    counter += 1
    return f"{match.group(1)}{new_number}{match.group(3)}"

# 更新内容
updated_lines = []
for line in lines:
    updated_line = pattern.sub(replace_with_increment, line)
    updated_lines.append(updated_line)

# 将更新后的内容写回原始文件
with open(input_file_path, "w", encoding="utf-8") as file:
    file.writelines(updated_lines)

# 将匹配到的行写入 2.txt
with open(output_file_path, "w", encoding="utf-8") as file:
    for matched_line in matched_lines:
        file.write(matched_line + "\n")

# 打印日志
for entry in log:
    print(entry)

print(f"处理完成，编号已重新排序，匹配到的行已保存到 '{output_file_path}'。")

```

输出日志

```
匹配行: '- **问 114:' -> 修改为: '- **问 114:'
匹配行: '- **问 115:' -> 修改为: '- **问 115:'
匹配行: '- **问 116:' -> 修改为: '- **问 116:'
匹配行: '- **问 117:' -> 修改为: '- **问 117:'
匹配行: '- **问 118:' -> 修改为: '- **问 118:'
匹配行: '- **问 119:' -> 修改为: '- **问 119:'
匹配行: '- **问 120:' -> 修改为: '- **问 120:'
匹配行: '- **问 121:' -> 修改为: '- **问 121:'
匹配行: '- **问 122:' -> 修改为: '- **问 122:'
匹配行: '- **问 123:' -> 修改为: '- **问 123:'
匹配行: '- **问 124:' -> 修改为: '- **问 124:'
匹配行: '- **问 125:' -> 修改为: '- **问 125:'
匹配行: '- **问 126:' -> 修改为: '- **问 126:'
匹配行: '- **问 127:' -> 修改为: '- **问 127:'
匹配行: '- **问 128:' -> 修改为: '- **问 128:'
匹配行: '- **问 129:' -> 修改为: '- **问 129:'
匹配行: '- **问 130:' -> 修改为: '- **问 130:'
```

### 2. 问题导出脚本

```python
import re

# 文件路径
input_file_path = "1.md"
output_file_path = "2.txt"

# 读取文件内容
with open(input_file_path, "r", encoding="utf-8") as file:
    lines = file.readlines()

# 正则表达式匹配：支持所有可能的缩进格式
pattern = re.compile(r"(\s*- \*\*问 )(\d{3})([:：])")

# 用于存储匹配到的行
matched_lines = []

# 遍历文件内容，寻找匹配行
for line in lines:
    if pattern.search(line):  # 如果匹配
        matched_lines.append(line.strip())  # 保存完整行

# 将匹配到的行写入 2.txt
with open(output_file_path, "w", encoding="utf-8") as file:
    for matched_line in matched_lines:
        file.write(matched_line + "\n")

print(f"匹配到的行已保存到 '{output_file_path}'，共匹配到 {len(matched_lines)} 行。")

```

### 3. 去除成对的星号并 anki 化脚本

```python
import re

# 文件路径
file_path = "2.txt"

# 读取文件内容
with open(file_path, "r", encoding="utf-8") as file:
    lines = file.readlines()

# 处理逻辑：删除成对的 **，添加 `#card`，并插入 `回答`
processed_lines = []
for line in lines:
    # 删除成对的 **
    line = re.sub(r"\*\*(.*?)\*\*", r"\1", line)
    # 添加 `#card` 和换行后的 `回答`
    processed_lines.append(f"{line.strip()} #card \n\t回答\n")

# 将更新后的内容覆盖写入文件
with open(file_path, "w", encoding="utf-8") as file:
    file.writelines(processed_lines)

print(f"文件 '{file_path}' 已按需求处理完成。")


```

### 一步完成 `1.md` 到问题列表的过程

```python

```
