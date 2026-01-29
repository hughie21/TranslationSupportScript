import requests
import pandas as pd
import time
from tqdm import tqdm, trange

def clear_empty_text(text_list):
    return [text.strip() for text in text_list if text.strip() != ""]

def fetch_original_text(chapter, include_trans=False):
    url = f"https://n.novelia.cc/api/novel/syosetu/n7499hd/chapter/{chapter+1}"

    payload = {}
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0',
    'Accept': 'application/json',
    'Accept-Language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8,zh-HK;q=0.7,en-US;q=0.6,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Referer': 'https://n.novelia.cc/novel/syosetu/n7499hd/203',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJodWdoaWUiLCJhdWQiOlsibiJdLCJleHAiOjE3Njk5NDI5NDQsImlhdCI6MTc2OTMzODE0NCwicm9sZSI6Im1lbWJlciIsImNyYXQiOjE3MTM5NjY1NTh9.SPkidNvUnrM89bI7t5nFOVQAHg_Vw3W9TnY9H1ANsUg',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-GPC': '1',
    'Priority': 'u=4',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'TE': 'trailers'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error fetching chapter {chapter}: {e}")
        return [], [], ""
    data = response.json()

    original_text = [f"## {chapter}.{data['titleJp']}"] + clear_empty_text(data["paragraphs"])

    translated_text = [f"## {chapter}.{data['titleZh']}"] + clear_empty_text(data["sakuraParagraphs"])

    if include_trans:
        return original_text, translated_text, data['titleZh']
    else:
        return original_text, [], data['titleZh']


if __name__ == "__main__":
    start = 373
    end = 404

    for chapter in trange(start, end + 1):
        original_text, translated_text, title = fetch_original_text(chapter, include_trans=False)
        
        original_text = clear_empty_text(original_text)

        df = pd.DataFrame({
            "original_text": original_text,
            "translated_text": translated_text
        })

        df.to_csv(f"./chapter/chapter_{chapter}_{title}.csv", index=True, header=False)

        time.sleep(1)
