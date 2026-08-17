---
mtime: 2024-12-27
title: 文本处理_导入面试问题到Anki
date: 2024-12-27
categories: 文本处理
tags: 归档笔记/生活经验/数字经验
author: 自己
---

1. 把看到的题目通过记录的方式, 半自动的导入到 Anki 中
2. 注意, 本方法适合一次导入, 不适合在导入文件上再做修改

## 1. 导入题目到 Anki

- 脚本文件夹: Anki 题目收集和导入 Obisidian

### 1. 把题目标题收集到 1.txt 中

- `1.txt`

```
43. 了解主从复制的原理吗？
```

### 2. 通过脚本把前缀添加上

```python
# 前缀字典
prefix_list = [
    "01·面试小抄·",
    "02·JavaGuide·",
    "03·10万字总结·",
    "04·Docker面试题·",
    "05·K8S面试题·",
    "06·Netty面试题·",
    "07·分布式面试题·"
]

# 选择需要的前缀，通过调整索引来选择
prefix_index = 6 # 根据需要调整为 0, 1, 或 2
prefix_name = prefix_list[prefix_index]

# 文件路径定义
input_file = "1.txt"
output_file = "1_output.txt"

# 读取并处理文件内容
with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

# 重写输出文件
with open(output_file, "w", encoding="utf-8") as f:
    for line in lines:
        line = line.strip()
        if line:
            f.write(f"### {prefix_name}{line} #card\n")
            f.write("\n\n")

print(f"处理完成，结果已保存到 {output_file}")

```

较早的一个版本, 主要是在格式上把 '### ' 改成了 '- '

```python
# 前缀字典
prefix_list = [
    "01·面试小抄·",
    "02·JavaGuide·",
    "03·10万字总结·",
    "04·Docker面试题·",
    "05·K8S面试题·",
    "06·Netty面试题·",
    "07·分布式面试题·"
]

# 选择需要的前缀，通过调整索引来选择
prefix_index = 6 # 根据需要调整为 0, 1, 或 2
prefix_name = prefix_list[prefix_index]

# 文件路径定义
input_file = "1.txt"
output_file = "1_output.txt"

# 读取并处理文件内容
with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

# 重写输出文件, 另一个'- '版本
with open(output_file, "w", encoding="utf-8") as f:
    for line in lines:
        line = line.strip()
        if line:
            f.write(f"- {prefix_name}{line} #card\n")
            f.write("    \n\n")

print(f"处理完成，结果已保存到 {output_file}")
```

结果如下:

```
### 07·分布式面试题·43. 了解主从复制的原理吗？ #card
```java
public class Singleton{  
    private static Singleton instance = null;  
    private Singleton(){}  
    public Singleton getInstance(){  
        if(instance == null){  
            synchronized (Singleton.class){  
                if(instance == null){  
                    this.instance = new Singleton();  
                }  
            }  
        }  
        return instance;  
    }  
}
```

也可以添加代码答案

### 3. 复制到 Obisdian 中, 通过 FlashCard 导入到 Anki

## 复习时候如何将问题再次导出

- 脚本文件夹: Anki 复习截图 OCR 处理

### 手机端

1. 截图: 注意, 需要把主题调成黑色, 否则在 iphone 端看不出图片在哪
2. 导入到电脑中
3. 通过下面的脚本完成识别

```python
import os
from PIL import Image
import easyocr

# 创建存储处理后图片的文件夹
def create_processed_folder():
    if not os.path.exists('processed'):
        os.mkdir('processed')

# 裁剪图片
def crop_image(image_path):
    image = Image.open(image_path)
    width, height = image.size

    top_crop = int(height * 0.102)
    bottom_crop = int(height * 0.15)

    cropped_image = image.crop((0, top_crop, width, height - bottom_crop))
    return cropped_image

# 保存处理后的图片
def save_processed_image(image, original_path):
    processed_path = os.path.join('processed', os.path.basename(original_path).replace('.png', '_processed.png'))
    image.save(processed_path)
    return processed_path

# 识别文字并保存到 1.txt
def append_text_to_file(text):
    with open('1.txt', 'a', encoding='utf-8') as f:
        f.write(text.replace('\n', ' ') + '\n')

# 检查并记录处理过的文件
def append_to_log(file_name):
    with open('log.txt', 'a', encoding='utf-8') as log_file:
        log_file.write(file_name + '\n')

def is_file_processed(file_name):
    if not os.path.exists('log.txt'):
        return False
    with open('log.txt', 'r', encoding='utf-8') as log_file:
        processed_files = log_file.read().splitlines()
    return file_name in processed_files

# 主函数
if __name__ == "__main__":
    create_processed_folder()
    reader = easyocr.Reader(['en', 'ch_sim'])  # 初始化easyocr阅读器，支持英文和简体中文

    for file in os.listdir():
        if file.lower().endswith('.png'):
            if is_file_processed(file):
                print(f"{file} has already been processed.")
                continue
            try:
                # 裁剪图片
                cropped_image = crop_image(file)

                # 保存处理后的图片
                processed_image_path = save_processed_image(cropped_image, file)

                # 使用easyocr识别文字
                text = reader.readtext(processed_image_path, detail=0)
                text = ' '.join(text)  # 将识别出的文字合并为单行

                # 保存文字到1.txt
                append_text_to_file(text)

                # 记录已处理文件
                append_to_log(file)

                print(f"Processed and extracted text from {file}")

            except Exception as e:
                print(f"Error processing {file}: {e}")

```

### 电脑端

1. 用脚本截图

```python
import pyautogui
from datetime import datetime
import os
from pynput import keyboard

def screenshot_and_save():
    # 获取当前时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}.png"  # 保存为 PNG 格式

    # 截取屏幕
    screenshot = pyautogui.screenshot()

    # 保存到脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    save_path = os.path.join(script_dir, filename)
    screenshot.save(save_path, "PNG")  # 使用 PNG 格式保存

    print(f"Screenshot saved as {filename} in {script_dir}")

def on_press(key):
    try:
        # 检测是否按下 F2 键
        if key == keyboard.Key.f2:
            screenshot_and_save()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Press F2 to capture the screen (saved as PNG). Press ESC to exit.")
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

```

2. 识别 ocr

```python
import os
from PIL import Image
import easyocr

# 创建存储处理后图片的文件夹
def create_processed_folder():
    if not os.path.exists('processed'):
        os.mkdir('processed')

# 裁剪图片
def crop_image(image_path):
    image = Image.open(image_path)
    width, height = image.size

    top_crop = int(height * 0.086)
    bottom_crop = int(height * 0.875)

    cropped_image = image.crop((0, top_crop, width, height - bottom_crop))
    return cropped_image

# 保存处理后的图片
def save_processed_image(image, original_path):
    processed_path = os.path.join('processed', os.path.basename(original_path).replace('.png', '_processed.png'))
    image.save(processed_path)
    return processed_path

# 识别文字并保存到 1.txt
def append_text_to_file(text):
    with open('1.txt', 'a', encoding='utf-8') as f:
        f.write(' '.join(text.replace('\n', ' ').split()) + '\n')

# 检查并记录处理过的文件
def append_to_log(file_name):
    with open('log.txt', 'a', encoding='utf-8') as log_file:
        log_file.write(file_name + '\n')

def is_file_processed(file_name):
    if not os.path.exists('log.txt'):
        return False
    with open('log.txt', 'r', encoding='utf-8') as log_file:
        processed_files = log_file.read().splitlines()
    return file_name in processed_files

# 主函数
if __name__ == "__main__":
    create_processed_folder()
    reader = easyocr.Reader(['en', 'ch_sim'])  # 初始化easyocr阅读器，支持英文和简体中文

    for file in os.listdir():
        if file.lower().endswith('.png'):
            if is_file_processed(file):
                print(f"{file} has already been processed.")
                continue
            try:
                # 裁剪图片
                cropped_image = crop_image(file)

                # 保存处理后的图片
                processed_image_path = save_processed_image(cropped_image, file)

                # 使用easyocr识别文字
                text = reader.readtext(processed_image_path, detail=0)
                text = ' '.join(text)  # 将识别出的文字合并为单行

                # 保存文字到1.txt
                append_text_to_file(text)

                # 记录已处理文件
                append_to_log(file)

                print(f"Processed and extracted text from {file}")

            except Exception as e:
                print(f"Error processing {file}: {e}")

```
