import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F

# --- CONFIGURATION ---
MODEL_PATH = "./model_output"  # Load from where we just saved it

print(f"--- LOADING BRAIN FROM {MODEL_PATH} ---")
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
    model.eval()  # Set to evaluation mode
    print("[SUCCESS] Model loaded!")
except Exception as e:
    print(f"[FAIL] Could not load model: {e}")
    exit()

def predict(text):
    # 1. Prepare Text
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    
    # 2. Predict
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = F.softmax(logits, dim=-1) # Convert to percentage (0.0 to 1.0)
    
    # 3. Interpret
    # Our labels were: 0 = Real, 1 = Fake
    fake_probability = probs[0][1].item()
    real_probability = probs[0][0].item()
    
    print(f"\nAnalysis for: '{text}'")
    print(f"Fake Score: {fake_probability:.4f} ({fake_probability*100:.1f}%)")
    print(f"Real Score: {real_probability:.4f} ({real_probability*100:.1f}%)")
    
    if fake_probability > 0.6:
        print("Verdict: 🚨 FAKE NEWS DETECTED")
    elif real_probability > 0.6:
        print("Verdict: ✅ REAL NEWS")
    else:
        print("Verdict: ❓ UNCERTAIN (Need more context)")

# --- INTERACTIVE LOOP ---
print("\n--- AI IS READY ---")
print("Type a headline (Hindi/English) to check. Type 'exit' to stop.")

while True:
    user_input = input("\nEnter Text: ")
    if user_input.lower() in ['exit', 'quit']:
        break
    
    predict(user_input)