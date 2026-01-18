import pandas as pd
import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset

print("--- STARTING QUICK UPDATE (INCREMENTAL TRAINING) ---")

# 1. LOAD DATA
# A. Load the NEW Real News you just scraped
try:
    df_new = pd.read_csv('dataset/live_real_news.csv')
    df_new['label'] = 0  # Ensure they are marked Real
    print(f"Loaded {len(df_new)} new REAL news articles.")
except:
    print("[ERROR] Could not find 'dataset/live_real_news.csv'. Did you run the scraper?")
    exit()

# B. Load a sample of OLD Fake News (to maintain balance)
try:
    df_old = pd.read_csv('dataset/train_ready.csv')
    # Filter only Fake news (Label 1)
    df_fake = df_old[df_old['label'] == 1].sample(n=len(df_new)) # Pick same amount as new real news
    print(f"Loaded {len(df_fake)} old FAKE news articles for balance.")
except:
    print("[ERROR] Could not find 'dataset/train_ready.csv'.")
    exit()

# C. Combine
df_final = pd.concat([df_new, df_fake]).sample(frac=1).reset_index(drop=True)
print(f"Total Training Data for Update: {len(df_final)} rows.")

# 2. CONVERT TO HUGGINGFACE DATASET
dataset = Dataset.from_pandas(df_final)
MODEL_PATH = "./model_output"

# 3. LOAD YOUR *EXISTING* TRAINED MODEL
print(f"Loading existing brain from {MODEL_PATH}...")
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
except:
    print("[CRITICAL ERROR] Could not load your trained model. Do you have the 'model_output' folder?")
    exit()

def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=512)

tokenized_datasets = dataset.map(tokenize_function, batched=True)

# 4. FAST TRAINING CONFIGURATION
training_args = TrainingArguments(
    output_dir='./model_output_v2', # Save to a new folder just in case
    num_train_epochs=2,             # Only 2 passes (Very fast)
    per_device_train_batch_size=4,
    save_strategy="no",             # Don't waste time saving checkpoints
    logging_steps=50
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets,
)

# 5. TRAIN
print("--- UPDATING BRAIN (This will take ~10 mins) ---")
trainer.train()



# 6. SAFE SAVE (Avoids Windows Error 1224)
NEW_MODEL_PATH = "./model_output_updated"

print(f"Saving new brain to {NEW_MODEL_PATH}...")
model.save_pretrained(NEW_MODEL_PATH)
tokenizer.save_pretrained(NEW_MODEL_PATH)

print("\n[SUCCESS] Training Complete!")
print("ACTION REQUIRED:")
print(f"1. Go to your project folder.")
print(f"2. Delete the old 'model_output' folder.")
print(f"3. Rename '{NEW_MODEL_PATH}' to 'model_output'.")
print("4. Restart app.py.")