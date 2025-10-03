import pandas as pd
from bs4 import BeautifulSoup
import html
import sys
from tqdm import tqdm

# --- 1. CONFIGURATION ---
INPUT_FILE_PATH = './client_files/Reviews.csv'
OUTPUT_FILE_PATH = './output/Cleaned_Reviews.csv'
COLUMN_TO_CLEAN = 'Text'
CHUNK_SIZE = 50000

# --- 2. THE FINAL CLEANING FUNCTION ---
def clean_html(html_text):
    if not isinstance(html_text, str):
        return ""
    text = html.unescape(html_text)
    if ('/' in text or '\\' in text) and '<' not in text:
        return text
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text(separator=' ', strip=True)

# --- 3. MAIN PROCESSING LOGIC ---
def main():
    try:
        print("Calculating total rows for progress bar...")
        total_rows = sum(1 for row in open(INPUT_FILE_PATH, 'r', encoding='utf-8')) - 1
        total_chunks = (total_rows // CHUNK_SIZE) + 1
        print(f"Input file has ~{total_rows:,} rows. Starting processing...")

        is_first_chunk = True
        
        with pd.read_csv(INPUT_FILE_PATH, chunksize=CHUNK_SIZE, engine='python') as reader:
            for chunk in tqdm(reader, total=total_chunks, desc="Cleaning Reviews"):
                
                chunk['CleanedText'] = chunk[COLUMN_TO_CLEAN].apply(clean_html)
                chunk = chunk.drop(columns=[COLUMN_TO_CLEAN])

                if is_first_chunk:
                    chunk.to_csv(OUTPUT_FILE_PATH, index=False, mode='w')
                    is_first_chunk = False
                else:
                    chunk.to_csv(OUTPUT_FILE_PATH, index=False, mode='a', header=False)

        print(f"\n✅ Processing complete!")
        print(f"Cleaned data has been saved to: {OUTPUT_FILE_PATH}")

    except FileNotFoundError:
        print(f"❌ ERROR: The input file was not found at '{INPUT_FILE_PATH}'")
        sys.exit(1)
    except KeyError:
        print(f"❌ ERROR: A column named '{COLUMN_TO_CLEAN}' was not found in the CSV.")
        sys.exit(1)

# --- 4. SCRIPT EXECUTION ---
if __name__ == "__main__":
    main()