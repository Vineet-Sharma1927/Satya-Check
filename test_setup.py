import pandas as pd
import pytesseract
from transformers import AutoTokenizer

print("--- SYSTEM CHECK STARTING ---")

# 1. Check Data
try:
    # Try different encodings
    for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
        try:
            df = pd.read_csv('dataset/master_data.csv', encoding=encoding)
            print(f"[SUCCESS] Dataset loaded with {encoding} encoding! Found {len(df)} rows.")
            print("Sample Headlines:", df.iloc[0]['Text'][:50] if 'Text' in df.columns else "Column 'Text' not found")
            break
        except UnicodeDecodeError:
            continue
    else:
        raise Exception("Could not decode with any common encoding")
except Exception as e:
    print(f"[FAIL] Could not load dataset: {e}")

# 2. Check OCR (Windows Path Fix included)
# If you are on Windows, uncomment the line below and point to your exe
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

try:
    print(f"[SUCCESS] Tesseract Version: {pytesseract.get_tesseract_version()}")
except Exception as e:
    print(f"[FAIL] Tesseract not found. Did you install the .exe? Error: {e}")

# 3. Check BERT
try:
    tokenizer = AutoTokenizer.from_pretrained("google/muril-base-cased")
    print("[SUCCESS] MuRIL (Indic BERT) Tokenizer loaded successfully!")
except Exception as e:
    print(f"[FAIL] Could not download BERT model: {e}")

print("--- SYSTEM CHECK DONE ---")