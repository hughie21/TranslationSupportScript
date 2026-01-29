import zipfile
import pandas as pd

def get_all_chaters_from_zip(zip_path):
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

def format_translated_text(translated_text, output_path):
    translated_text = [line.strip() for line in translated_text if isinstance(line, str)]
    text = "\n".join(translated_text)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    
if __name__ == "__main__":
    zip_path = "2026_01_29_10_45_10_253e3a.zip"
    data_dirs = get_all_chaters_from_zip(zip_path)

    format_translated_text(get_trans_from_zip(zip_path, data_dirs[0]), "formatted_translated_text.md")
