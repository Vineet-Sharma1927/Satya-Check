import pandas as pd
import os
import random

print("--- FINAL DATASET COMPILATION STARTED ---")

# --- PART A: LOAD BASE DATA (ZENODO) ---
base_dir = 'dataset'
fake_dir = os.path.join(base_dir, 'fake') 
real_dir = os.path.join(base_dir, 'real')
# Handle capitalization
if not os.path.exists(fake_dir) and os.path.exists(os.path.join(base_dir, 'Fake')): fake_dir = os.path.join(base_dir, 'Fake')
if not os.path.exists(real_dir) and os.path.exists(os.path.join(base_dir, 'Real')): real_dir = os.path.join(base_dir, 'Real')

def read_folder(folder, label):
    data = []
    if os.path.exists(folder):
        files = os.listdir(folder)
        print(f"Reading {len(files)} files from {folder}...")
        for fname in files:
            if fname.endswith('.txt'):
                try:
                    with open(os.path.join(folder, fname), 'r', encoding='utf-8') as f:
                        text = f.read().strip()
                        if len(text) > 10: data.append({'text': text, 'label': label})
                except: pass
    return data

zenodo_fake = read_folder(fake_dir, 1)
zenodo_real = read_folder(real_dir, 0)
print(f"Base Data: {len(zenodo_fake)} Fake, {len(zenodo_real)} Real")

# --- PART B: INJECT REAL ENGLISH (Anti-Language Gap) ---
print("Injecting 2,500 English Real News samples...")
eng_templates = [
    "The Prime Minister announced a new scheme for {topic} today.",
    "Supreme Court issued a verdict regarding the {topic} case.",
    "ISRO successfully launched the satellite for {topic} monitoring.",
    "The Indian Cricket Team won the match against {country} by {score}.",
    "Sensex jumped {points} points after the budget announcement.",
    "IMD predicts heavy rainfall in {city} for the next 48 hours.",
    "Election Commission declared the results for {state} assembly polls.",
    "Government reduces tax rates on {topic} to boost economy.",
    "Local police arrested the gang involved in {topic} fraud.",
    "The new highway connecting {city} and {city2} is now open.",
    "Schools in {city} will remain closed due to {topic}.",
    "Gold prices dropped by {points} percent in the global market."
]
topics = ["farmers", "education", "healthcare", "pollution", "traffic", "cyber security"]
cities = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Hyderabad", "Pune"]
eng_rows = [{'text': random.choice(eng_templates).format(topic=random.choice(topics), city=random.choice(cities), city2=random.choice(cities), country="Australia", score="50 runs", points="500", state="UP"), 'label': 0} for _ in range(2500)]

# --- PART C: INJECT REAL HINDI (Anti-Topic Bias) ---
print("Injecting 1,500 Hindi Real News samples...")
hin_templates = [
    "पीएम मोदी ने आज {city} में {project} का उद्घाटन किया।",
    "{city} में पुलिस ने सुरक्षा व्यवस्था कड़ी कर दी है।",
    "सुप्रीम कोर्ट ने {topic} मामले में सुनवाई टाल दी है।",
    "मौसम विभाग के अनुसार {city} में भारी बारिश होगी।",
    "चुनाव आयोग ने {state} में चुनाव की तारीखों का ऐलान किया।",
    "सोने के दाम में आज गिरावट दर्ज की गई।",
    "सरकार ने {topic} पर नई गाइडलाइंस जारी की हैं।"
]
hin_rows = [{'text': random.choice(hin_templates).format(city=random.choice(["दिल्ली", "मुंबई", "पटना"]), project="अस्पताल", topic="प्रदूषण", state="बिहार"), 'label': 0} for _ in range(1500)]

# --- PART D: INJECT HINGLISH (Anti-Script Bias) ---
print("Injecting 500 Hinglish samples...")
hinglish_fake = [{'text': "Ye news fake hai ki lockdown lagega. Forward mat karna.", 'label': 1} for _ in range(250)]
hinglish_real = [{'text': "Modi ji ne aaj meeting me naye rules announce kiye.", 'label': 0} for _ in range(250)]

# ... existing code ...

# --- PART E: LOAD LIVE REAL NEWS (NEW) ---
live_news_file = 'dataset/live_real_news.csv'
live_news_data = []
if os.path.exists(live_news_file):
    try:
        df_live = pd.read_csv(live_news_file)
        live_news_data = df_live.to_dict('records')
        print(f"Injecting {len(live_news_data)} Live Real News articles...")
    except Exception as e:
        print(f"Could not load live news: {e}")



# --- MERGE ALL ---
all_data = zenodo_fake + zenodo_real + eng_rows + hin_rows + hinglish_fake + hinglish_real + live_news_data
df = pd.DataFrame(all_data)

# --- FINAL BALANCE CHECK ---
fake_count = len(df[df['label'] == 1])
real_count = len(df[df['label'] == 0])

print(f"\n--- FINAL COMPILED DATASET ---")
print(f"Total Rows: {len(df)}")
print(f"Fake News: {fake_count}")
print(f"Real News: {real_count}")

# Save
df = df.sample(frac=1).reset_index(drop=True)
df.to_csv('dataset/train_ready.csv', index=False)
print("[SUCCESS] Saved to 'dataset/train_ready.csv'. READY TO TRAIN.")