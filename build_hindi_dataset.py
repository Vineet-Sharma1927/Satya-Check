import os
import glob
import pandas as pd
from tqdm import tqdm

HINDI_FAKE_DIR = 'dataset/zenodo_fake_news_data/Hindi_fake_news'
HINDI_REAL_DIR = 'dataset/zenodo_fake_news_data/Hindi_real_news'
OUTPUT_FILE = 'dataset/final_hindi_dataset.csv'

def compile_data(folder_path, label):
    data = []
    if not os.path.exists(folder_path):
        print(f"❌ ERROR: Folder not found: {folder_path}")
        return data

    files = glob.glob(os.path.join(folder_path, "*.txt"))
    
    for file_path in tqdm(files, desc=f"Compiling Label {label}"):
        try:
            # We use errors='replace' to fix the UnicodeDecodeError safely
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read().strip()
                if content:
                    data.append({'text': content, 'label': label})
        except Exception:
            pass
    return data

def main():
    print("🚀 Compiling Native Hindi Dataset...")
    
    fake_data = compile_data(HINDI_FAKE_DIR, label=1)
    real_data = compile_data(HINDI_REAL_DIR, label=0)
    
    all_data = fake_data + real_data
    df = pd.DataFrame(all_data)
    
    # Shuffle completely to prevent training bias
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    df.to_csv(OUTPUT_FILE, index=False)
    
    print("\n" + "="*40)
    print(f"✅ SUCCESS! Pure Devanagari Dataset Built.")
    print(f"📊 Total Valid Rows: {len(df)}")
    print("="*40)

if __name__ == "__main__":
    main()