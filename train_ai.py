import pandas as pd
import numpy as np
import torch
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from torch.utils.data import Dataset
import shutil
import os

# --- CONFIGURATION ---
MODEL_NAME = "google/muril-base-cased"
DATA_PATH = "dataset/train_ready.csv"
SAVE_PATH = "./model_output"
DEBUG_MODE = False  

# --- 1. PREPARE DATASET CLASS ---
class NewsDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

# --- 2. LOAD DATA ---
print("--- LOADING DATA ---")
df = pd.read_csv(DATA_PATH)
df = df.dropna()

if DEBUG_MODE:
    # AUTO-ADJUST: Takes 50 rows OR however many you have if less than 50
    sample_size = min(len(df), 50)
    print(f"\n[DEBUG MODE ON] Training on {sample_size} rows.")
    df = df.sample(sample_size)
else:
    print(f"\n[REAL MODE] Training on full {len(df)} rows.")

# Split: 80% Train, 20% Test (with safety for tiny datasets)
if len(df) < 5:
    print("Dataset too small for split. Using all for training.")
    train_texts = df['text'].tolist()
    val_texts = df['text'].tolist()
    train_labels = df['label'].tolist()
    val_labels = df['label'].tolist()
else:
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        df['text'].tolist(), df['label'].tolist(), test_size=0.2
    )

# --- 3. TOKENIZATION ---
print("--- LOADING TOKENIZER ---")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=128)
val_encodings = tokenizer(val_texts, truncation=True, padding=True, max_length=128)

train_dataset = NewsDataset(train_encodings, train_labels)
val_dataset = NewsDataset(val_encodings, val_labels)

# --- 4. TRAINING SETUP ---
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)

training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=1 if DEBUG_MODE else 3,
    per_device_train_batch_size=4,   # Lower batch size for safety
    per_device_eval_batch_size=4,
    gradient_accumulation_steps=2,
    eval_strategy="epoch",           # <--- FIXED THIS LINE (New version requires 'eval_strategy')
    save_strategy="epoch",
    logging_dir='./logs',
    logging_steps=100
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset
)

# --- 5. RUN TRAINING ---
print("\n--- STARTING TRAINING ---")
trainer.train()

# --- 6. SAVE EVERYTHING ---
print("\n--- SAVING MODEL ---")
# Clean old save if exists
if os.path.exists(SAVE_PATH):
    shutil.rmtree(SAVE_PATH)
    
model.save_pretrained(SAVE_PATH)
tokenizer.save_pretrained(SAVE_PATH)
print(f"Model saved to {SAVE_PATH}")

# --- 7. FINAL TEST ---
print("\n--- EVALUATING ---")
predictions = trainer.predict(val_dataset)
preds = np.argmax(predictions.predictions, axis=-1)
print(classification_report(val_labels, preds, target_names=['Real', 'Fake'], zero_division=0))