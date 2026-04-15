import torch
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
from datasets import Dataset
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
DATA_PATH = "dataset/final_hindi_dataset.csv"
MODEL_NAME = "google/muril-base-cased"
OUTPUT_DIR = "./muril_fake_news_model"

# Hyperparameters
MAX_LEN = 256
BATCH_SIZE = 16  # Reduce to 8 if you get CUDA Out of Memory errors
EPOCHS = 3
# ==========================================

def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='binary')
    acc = accuracy_score(labels, preds)
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }

def main():
    print(f"🚀 Initializing MuRIL Fine-Tuning Pipeline...")
    
    # 1. Hardware Check
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🖥️  Training on device: {device.type.upper()}")
    if device.type == "cpu":
        print("⚠️ WARNING: You are training on a CPU. This will be excruciatingly slow.")

    # 2. Load and Split Data
    print("📂 Loading dataset...")
    df = pd.read_csv(DATA_PATH)
    
    # Drop any stray nulls
    df = df.dropna(subset=['text', 'label'])
    
    # 80/20 Train-Test Split
    train_df, eval_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['label'])
    print(f"📊 Training samples: {len(train_df)} | Evaluation samples: {len(eval_df)}")

    # Convert pandas dataframes to HuggingFace Dataset objects
    train_dataset = Dataset.from_pandas(train_df)
    eval_dataset = Dataset.from_pandas(eval_df)

    # 3. Tokenization
    print(f"🔤 Loading Tokenizer: {MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=MAX_LEN)

    print("⚙️ Tokenizing datasets...")
    tokenized_train = train_dataset.map(tokenize_function, batched=True)
    tokenized_eval = eval_dataset.map(tokenize_function, batched=True)

    # Remove string columns so PyTorch doesn't crash
    tokenized_train = tokenized_train.remove_columns(["text", "__index_level_0__"])
    tokenized_eval = tokenized_eval.remove_columns(["text", "__index_level_0__"])
    tokenized_train.set_format("torch")
    tokenized_eval.set_format("torch")

    # 4. Load Base Model
    print(f"🧠 Loading Base Model: {MODEL_NAME}...")
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)

    # 5. Training Arguments
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        learning_rate=2e-5,  # Standard learning rate for fine-tuning BERT variants
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        num_train_epochs=EPOCHS,
        weight_decay=0.01,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        fp16=torch.cuda.is_available(), # Use mixed precision only if GPU is present
        logging_dir='./logs',
        logging_steps=100,
    )

    # 6. Initialize Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_eval,
        compute_metrics=compute_metrics,
    )

    # 7. Execute Training
    print("🔥 Starting Training Loop...")
    trainer.train()

    # 8. Save Final Model
    print("💾 Saving final model and tokenizer...")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print("✅ Training Complete!")

if __name__ == "__main__":
    main()