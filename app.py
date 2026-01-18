from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F
import easyocr
import requests
from sentence_transformers import SentenceTransformer, util # <--- NEW SPECIALIST
import numpy as np
import sqlite3
from datetime import datetime
import cv2  # <--- NEW
import numpy as np
# ... existing imports ...
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)
CORS(app)

MODEL_PATH = "./model_output"

# --- ⚠️ CONFIGURATION: PASTE YOUR KEYS HERE ---
GOOGLE_API_KEY = "AIzaSyD99jvGtX3pVJg1S_r8GZGxu9J1rmcI5oU"
GOOGLE_CSE_ID = "a5d5259db798c4fc2"

# --- 1. SYSTEM INITIALIZATION ---
print("--- LOADING SYSTEMS... ---")

# A. The Judge (Your Fake News Classifier)
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
    model.eval()
    print("[SUCCESS] Fake News Detector Loaded.")
except Exception as e:
    print(f"[CRITICAL FAIL] Could not load model: {e}")
    exit()

# B. The Librarian (The Semantic Comparator)
# This model is cleaner and smarter at comparing context
print("--- LOADING SEMANTIC ENGINE... ---")
similarity_model = SentenceTransformer('all-MiniLM-L6-v2') 
print("[SUCCESS] Semantic Engine Ready.")

# C. The Eyes (OCR)
reader = easyocr.Reader(['hi', 'en'], gpu=False)
print("[SUCCESS] OCR Ready.")

def init_db():
    conn = sqlite3.connect('satya_logs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY, date TEXT, text TEXT, verdict TEXT, confidence REAL)''')
    conn.commit()
    conn.close()

init_db()

# --- 2. THE LOGIC ---

def verify_news_with_google(user_text):
    if not GOOGLE_API_KEY or "PASTE" in GOOGLE_API_KEY:
        return "NO_MATCH", []

    print(f"--- 🔍 SEMANTIC SEARCH: {user_text[:40]}... ---")
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {'key': GOOGLE_API_KEY, 'cx': GOOGLE_CSE_ID, 'q': user_text, 'num': 5}

    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'items' not in data: return "NO_RESULTS_FOUND", []

        trusted_sources = [
            "ndtv.com", "timesofindia", "thehindu.com", "bbc.com", 
            "indianexpress.com", "zeenews", "aajtak", "news18", 
            "hindustantimes", "ani_news", "pib.gov.in", "businesstoday",
            "livemint", "espncricinfo"
        ]
        
        fact_check_sites = ["altnews.in", "boomlive.in", "vishvasnews", "factcheck"]

        verified_links = []

        # Encode User Query using the SPECIALIST model
        user_embedding = similarity_model.encode(user_text, convert_to_tensor=True)

        for item in data['items']:
            link = item['link']
            title = item['title']
            snippet = item.get('snippet', '')
            full_news_text = f"{title}. {snippet}"

            # 1. Fact Check Debunk
            for fc in fact_check_sites:
                if fc in link:
                    return "DEBUNKED_FAKE", [{"source": fc, "link": link}]

            # 2. Semantic Similarity Check
            for source in trusted_sources:
                if source in link:
                    # Encode News Result
                    news_embedding = similarity_model.encode(full_news_text, convert_to_tensor=True)
                    
                    # Calculate Score
                    score = util.pytorch_cos_sim(user_embedding, news_embedding).item()
                    
                    print(f"   >>> Checking {source}: Score = {round(score, 2)}")

                    # LOGIC:
                    # > 0.80: Same Meaning (Verified)
                    # 0.50 - 0.80: Related Topic but different details (Suspicious)
                    # < 0.50: Irrelevant
                    
                    if score > 0.80:
                        verified_links.append({"source": source, "link": link})
                    else:
                        print(f"   [REJECTED] Context Mismatch (Score: {round(score, 2)})")

        if len(verified_links) > 0:
            return "VERIFIED_REAL", verified_links
            
        return "NO_CONTEXT_MATCH", []

    except Exception as e:
        print(f"[ERROR] Search Failed: {e}")
        return "ERROR", []
    
def get_explanation_highlights(text):
    """
    Identifies 'Trigger Words' that typically indicate clickbait or fake news.
    Returns a list of words to highlight in RED.
    """
    # 1. The "Risk Dictionary" (Built from frequency analysis of Fake News)
    risk_lexicon = [
        "viral", "forward", "share", "guaranteed", "miracle", "cure", "secret", 
        "shocking", "exposed", "truth", "hidden", "whatsapp", "banned", "alert", 
        "warning", "magic", "ayurveda", "home remedy", "modi", "government", 
        "free", "money", "click", "claim", "conspiracy", "leak"
    ]
    
    # 2. Find matches
    words_found = []
    for word in risk_lexicon:
        if word in text.lower():
            words_found.append(word)
            
    return list(set(words_found)) # Remove duplicates

def predict_logic(text):
    # A. Run AI (The Judge)
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = F.softmax(outputs.logits, dim=-1)
    
    fake_score = probs[0][1].item()
    real_score = probs[0][0].item()
    
    # B. Run Google (The Librarian)
    search_verdict, evidence = verify_news_with_google(text)
    
    final_verdict = "UNCERTAIN"
    color = "orange"
    
    # --- FINAL VERDICT LOGIC ---
    
    if search_verdict == "VERIFIED_REAL":
        final_verdict = "VERIFIED REAL ✅"
        color = "green"
        real_score = 0.99
        fake_score = 0.01

    elif search_verdict == "DEBUNKED_FAKE":
        final_verdict = "PROVEN FAKE ❌"
        color = "red"
        fake_score = 0.99
        real_score = 0.01

    elif search_verdict == "NO_RESULTS_FOUND" or search_verdict == "NO_CONTEXT_MATCH":
        # The Semantic Model rejected the match -> So it's Suspicious
        final_verdict = "SUSPICIOUS (Context Mismatch) ⚠️"
        color = "red"
        fake_score = 0.90
        real_score = 0.10

    else:
        # Fallback to AI
        if fake_score > 0.50:
            final_verdict = "LIKELY FAKE (AI)"
            color = "red"
        else:
            final_verdict = "LIKELY REAL (AI)"
            color = "green"

    highlights = get_explanation_highlights(text)

    return {
        "fake_score": round(fake_score * 100, 1),
        "real_score": round(real_score * 100, 1),
        "verdict": final_verdict,
        "color": color,
        "evidence": evidence,
        "highlights": highlights  # <--- NEW FIELD
    }

# --- EXPLAINABLE AI MODULE ---


# --- ROUTES ---

@app.route('/api/analyze', methods=['POST'])
def analyze():
    final_text = ""
    if request.is_json:
        data = request.get_json()
        final_text = data.get('text', '')
    elif 'file' in request.files:
        file = request.files['file']
        try:
            image_bytes = file.read()
            result_list = reader.readtext(image_bytes, detail=0, paragraph=True)
            final_text = " ".join(result_list)
        except Exception as e:
            return jsonify({"error": f"OCR Failed: {str(e)}"}), 500

    if not final_text: return jsonify({"error": "No text detected"}), 400

    result = predict_logic(final_text)
    result['extracted_text'] = final_text
    
    # Log to DB
    try:
        conn = sqlite3.connect('satya_logs.db')
        c = conn.cursor()
        c.execute("INSERT INTO logs (date, text, verdict, confidence) VALUES (?, ?, ?, ?)", 
                  (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), final_text[:50]+"...", result['verdict'], result['fake_score']))
        conn.commit()
        conn.close()
    except: pass

    return jsonify(result)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        conn = sqlite3.connect('satya_logs.db')
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM logs")
        total = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM logs WHERE verdict LIKE '%FAKE%' OR verdict LIKE '%SUSPICIOUS%'")
        fake = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM logs WHERE verdict LIKE '%REAL%'")
        real = c.fetchone()[0]
        c.execute("SELECT date, text, verdict FROM logs ORDER BY id DESC LIMIT 5")
        logs = [{"date": row[0], "text": row[1], "verdict": row[2]} for row in c.fetchall()]
        conn.close()
        return jsonify({"total": total, "fake": fake, "real": real, "logs": logs})
    except:
        return jsonify({"total": 0, "fake": 0, "real": 0, "logs": []})



# --- WHATSAPP BOT ROUTE ---
# --- WHATSAPP BOT ROUTE (TEXT + IMAGE SUPPORT) ---
# --- WHATSAPP BOT ROUTE (FIXED IMAGE DOWNLOAD) ---
@app.route('/whatsapp', methods=['POST'])
def whatsapp_reply():
    num_media = int(request.values.get('NumMedia', 0))
    incoming_text = request.values.get('Body', '').lower()
    
    final_text_to_analyze = incoming_text
    
    print(f"--- 📩 WHATSAPP RECEIVED: {num_media} Images, Text: '{incoming_text}' ---")

    if num_media > 0:
        try:
            image_url = request.values.get('MediaUrl0')
            print(f"   Downloading Image from: {image_url}...")
            
            # FIX: Basic Requests often fail on Twilio Media URLs due to redirects/auth.
            # We try a standard download. If it fails (401/403), it usually prints the error code.
            img_resp = requests.get(image_url)
            
            if img_resp.status_code == 200:
                # FIX: Convert raw bytes to a NumPy array first (Safer for OpenCV)
                nparr = np.frombuffer(img_resp.content, np.uint8)
                img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if img_np is None:
                    print("   [ERROR] Downloaded data is not a valid image.")
                    final_text_to_analyze = "INVALID_IMAGE_DATA"
                else:
                    # Pass the NumPy image to EasyOCR
                    result_list = reader.readtext(img_np, detail=0, paragraph=True)
                    extracted_text = " ".join(result_list)
                    print(f"   [OCR SUCCESS] Extracted: {extracted_text[:50]}...")
                    
                    if extracted_text.strip():
                        final_text_to_analyze = extracted_text
                    else:
                        final_text_to_analyze = "NO_TEXT_FOUND_IN_IMAGE"
            else:
                print(f"   [ERROR] Download Failed with Status: {img_resp.status_code}")
                # This usually happens if 'HTTP Basic Auth' is enabled in Twilio settings
                final_text_to_analyze = "DOWNLOAD_PERMISSION_DENIED"

        except Exception as e:
            print(f"   [ERROR] OCR Failed: {e}")
            final_text_to_analyze = "ERROR_PROCESSING_IMAGE"

    # --- VALIDATION: Don't analyze error messages ---
    error_keywords = ["ERROR", "INVALID", "DENIED", "NO_TEXT"]
    if any(k in final_text_to_analyze for k in error_keywords) or len(final_text_to_analyze) < 5:
        resp = MessagingResponse()
        msg = resp.message()
        msg.body(f"🤖 *Satya-Check Error*\n\nI couldn't read the image. \nReason: {final_text_to_analyze}\n\nPlease type the text directly.")
        return str(resp)

    # --- LOGIC ---
    analysis = predict_logic(final_text_to_analyze)
    verdict = analysis['verdict']
    score = analysis['fake_score'] if "FAKE" in verdict or "SUSPICIOUS" in verdict else analysis['real_score']
    
    resp = MessagingResponse()
    msg = resp.message()
    
    response_text = f"*Satya-Check Analysis* 🇮🇳\n"
    if num_media > 0: response_text += f"📸 *Image Scanned*\n"
    response_text += f"🔎 *Verdict:* {verdict}\n"
    response_text += f"📊 *Confidence:* {score}%\n\n"
    
    if analysis['evidence']:
        response_text += "🌍 *Verified Sources:*\n"
        for item in analysis['evidence'][:1]:
            response_text += f"- {item['source']}: {item['link']}\n"
    elif "SUSPICIOUS" in verdict:
        response_text += "⚠️ No trusted media reports found.\n"
        
    msg.body(response_text)
    return str(resp)

if __name__ == '__main__':
    app.run(debug=True, port=5000)