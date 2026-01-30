import pandas as pd

def clean_text(text:str) -> list[str]:
    lines = text.splitlines()
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    return cleaned_lines

def load_text_to_file(csv_path:str, text:str, output_path:str) -> None:
    df = pd.read_csv(csv_path, header=None, names=["index", "original_text", "translated_text"])
    cleaned_lines = clean_text(text)
    if len(cleaned_lines) != len(df):
        raise ValueError(f"The number of cleaned lines does not match the number of rows in the CSV file ({len(cleaned_lines)} != {len(df)}).")
    df['translated_text'] = cleaned_lines
    df.to_csv(output_path, index=False, header=False)