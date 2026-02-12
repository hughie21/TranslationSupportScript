import os
import traceback
import zipfile
import pandas as pd
import re
from docx import Document
import win32com.client as win32
from win32com.client import constants

def get_all_chatpers_from_zip(zip_path):
    data_dirs = set()
    
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        file_list = zip_file.namelist()

        for file in file_list:
            if file.startswith('utf8/') and '/' in file[5:]:
                parts = file[5:].split('/')
                if parts[0]:
                    data_dirs.add(parts[0])
    return sorted(list(data_dirs))

def get_trans_from_zip(zip_path, data_dir):
    translated_text = []
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        file_list = zip_file.namelist()
        target_prefix = f'utf8/{data_dir}/'
        csv_files = [f for f in file_list if f.startswith(target_prefix) and f.endswith('.csv')]

        for csv_file in csv_files:
            with zip_file.open(csv_file) as file:
                df = pd.read_csv(file, header=None, names=["index",'original_text', 'translated_text'])
                translated_text += df['translated_text'].tolist()

    return translated_text

def get_single_chapter(zip_path, data_dir, chapter):
    translated_text = []
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        file_list = zip_file.namelist()
        target_prefix = f'utf8/{data_dir}/'
        csv_files = [f for f in file_list if f.startswith(target_prefix) and f.endswith('.csv')]

        for csv_file in csv_files:
            if csv_file == chapter:
                with zip_file.open(csv_file) as file:
                    df = pd.read_csv(file, header=None, names=["index",'original_text', 'translated_text'])
                    translated_text += df['translated_text'].tolist()
                break

    return translated_text

def find_continuous_segments(nums):
    if not nums:
        return []
    result = []
    start = end = nums[0]
    for num in nums[1:]:
        if num == end + 1:
            end = num
        else:
            if start == end:
                result.append((start,))
            else:
                result.append((start, end))
            start = end = num
    if start == end:
        result.append((start,))
    else:
        result.append((start, end))
    return result

def parse_ruby(text):
    pattern = r'<([^>]*)>{([^}]*)}'
    matches = re.findall(pattern, text)
    if not matches:
        return f"<p>{text}</p>"
    for match in matches:
        full_match = f"<{match[0]}>{{{match[1]}}}"
        ruby_html = f"<ruby><rb>{match[0]}</rb><rp>({match[1]})</rp><rt>{match[1]}</rt><rp>({match[1]})</rp></ruby>"
        text = text.replace(full_match, ruby_html)

    return f"<p>{text}</p>"

def format_translated_text(translated_text, output_path):
    conversation_pos = []
    translated_text = [line.strip() for line in translated_text if isinstance(line, str)]

    for i, line in enumerate(translated_text):
        if re.match(r'^[【|「|『](.+?)[】|」|』]$', line):
            conversation_pos.append(i)

    segments = find_continuous_segments(conversation_pos)

    for i in range(len(translated_text)):
        if translated_text[i].startswith("##"):
            translated_text[i] = f"<h1>{translated_text[i].lstrip('#')}</h1>"
            continue
        translated_text[i] = parse_ruby(translated_text[i])

    for segment in segments:
        if len(segment) == 2:
            _, end = segment
            translated_text[end] = f"{translated_text[end]}<p></p>"
        else:
            idx = segment[0]
            translated_text[idx] = f"{translated_text[idx]}<p></p>"
    
    not_conversation = set([i for i in range(1, len(translated_text) - 1)]) - set(conversation_pos)
    for idx in not_conversation:
        translated_text[idx] = f"{translated_text[idx]}<p></p>"

    text = "\n".join(translated_text)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    
if __name__ == "__main__":
    zip_path = "2026_02_05_21_12_28_1f9c28.zip"
    data_dirs = get_all_chatpers_from_zip(zip_path)

    format_translated_text(get_trans_from_zip(zip_path, data_dirs[0]), "formatted_translated_text.html")
