from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F
import easyocr
import requests
from sentence_transformers import SentenceTransformer, util
import numpy as np
import sqlite3
from datetime import datetime
import cv2
import re
import os
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)
CORS(app)

MODEL_PATH = "./model_output_zip/model_output"

# --- ⚠️ CONFIGURATION: USE ENVIRONMENT VARIABLES ---
# NEVER hardcode API keys. Set these in your terminal or .env file.
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.environ.get("GOOGLE_CSE_ID")

# --- 1. SYSTEM INITIALIZATION ---
print("--- LOADING SYSTEMS... ---")

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
    model.eval()
    print("[SUCCESS] Fake News Detector Loaded.")
except Exception as e:
    print(f"[CRITICAL FAIL] Could not load model: {e}")
    exit()

print("--- LOADING SEMANTIC ENGINE... ---")
similarity_model = SentenceTransformer('all-MiniLM-L6-v2') 
print("[SUCCESS] Semantic Engine Ready.")

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

def extract_keywords(text):
    """Strips stop words and conversational noise for the Search API."""
    stop_words = {"is", "am", "are", "was", "were", "a", "an", "the", "in", "on", "at", "to", "for", "of", "and", "or", "but", "it", "this", "that", "i", "you", "he", "she", "we", "they", "have", "has", "had", "do", "does", "did", "can", "could", "will", "would"}
    
    # Remove non-alphanumeric characters and lowercase
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Filter out stop words
    keywords = [w for w in words if w not in stop_words]
    
    # Rejoin and limit length to avoid maxing out Google API query limits
    return " ".join(keywords)[:100]

def verify_news_with_google(user_text):
    if not GOOGLE_API_KEY or "PASTE" in GOOGLE_API_KEY:
        print("[WARNING] Missing Google API Key.")
        return "NO_MATCH", []

    # Optimize the search query by extracting core keywords
    search_query = extract_keywords(user_text)
    print(f"--- 🔍 SEMANTIC SEARCH TRIGGERED ---")
    print(f"    Original: {user_text[:50]}...")
    print(f"    Query   : {search_query}")
    
    # INCREASE THE NET: Change 'num' from 5 to 10
    url = "https://www.googleapis.com/customsearch/v1"
    params = {'key': GOOGLE_API_KEY, 'cx': GOOGLE_CSE_ID, 'q': search_query, 'num': 10}

    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'items' not in data: 
            print("    [API] No results returned from Google.")
            return "NO_RESULTS_FOUND", []

        # EXPAND THE SOURCES
        trusted_sources = [
            "ndtv.com", "timesofindia", "thehindu", "bbc.com", 
            "indianexpress.com", "zeenews", "aajtak", "news18", 
            "hindustantimes", "ani_news", "pib.gov.in", "businesstoday",
            "livemint", "espncricinfo", "cricbuzz", "sportskeeda", "icc-cricket"
        ]
        
        fact_check_sites = ["altnews.in", "boomlive.in", "vishvasnews", "factcheck"]

        verified_links = []
        user_embedding = similarity_model.encode(user_text, convert_to_tensor=True)

        for item in data['items']:
            link = item['link']
            title = item['title']
            snippet = item.get('snippet', '')
            full_news_text = f"{title}. {snippet}"

            # FORCE LOGGING: See what Google is actually finding
            print(f"    [FETCHED] {link}")

            # 1. Fact Check Debunk
            for fc in fact_check_sites:
                if fc in link:
                    return "DEBUNKED_FAKE", [{"source": fc, "link": link}]

            # 2. Semantic Similarity Check
            for source in trusted_sources:
                if source in link:
                    news_embedding = similarity_model.encode(full_news_text, convert_to_tensor=True)
                    score = util.pytorch_cos_sim(user_embedding, news_embedding).item()
                    
                    if score > 0.55:
                        verified_links.append({"source": source, "link": link})
                        print(f"   [ACCEPTED] Match Found in {source} (Score: {round(score, 2)})")
                    else:
                        print(f"   [REJECTED] {source} Match too low (Score: {round(score, 2)})")
                    if score > 0.55:
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
    risk_lexicon = [
        "viral", "forward", "share", "guaranteed", "miracle", "cure", "secret", 
        "shocking", "exposed", "truth", "hidden", "whatsapp", "banned", "alert", 
        "warning", "magic", "ayurveda", "home remedy", "modi", "government", 
        "free", "money", "click", "claim", "conspiracy", "leak"
    ]
    words_found = [word for word in risk_lexicon if word in text.lower()]
    return list(set(words_found))

def predict_logic(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
    with torch.no_grad():
        logits = model(**inputs).logits
    probs = F.softmax(logits, dim=-1)
    fake_score = probs[0][1].item() 
    real_score = probs[0][0].item()
    
    search_verdict, evidence = verify_news_with_google(text)
    
    final_verdict = "UNCERTAIN"
    color = "orange"
    
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

    elif search_verdict in ["NO_RESULTS_FOUND", "NO_CONTEXT_MATCH"]:
        final_verdict = "SUSPICIOUS (Context Mismatch) ⚠️"
        color = "red"
        fake_score = 0.90
        real_score = 0.10

    else:
        if fake_score >= 0.30:
            final_verdict = "LIKELY FAKE (AI) 🚨"
            color = "red"
        else:
            final_verdict = "LIKELY REAL (AI) ✅"
            color = "green"

    highlights = get_explanation_highlights(text)

    return {
        "fake_score": round(fake_score * 100, 1),
        "real_score": round(real_score * 100, 1),
        "verdict": final_verdict,
        "color": color,
        "evidence": evidence,
        "highlights": highlights
    }

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
            
            img_resp = requests.get(image_url)
            
            if img_resp.status_code == 200:
                nparr = np.frombuffer(img_resp.content, np.uint8)
                img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if img_np is None:
                    print("   [ERROR] Downloaded data is not a valid image.")
                    final_text_to_analyze = "INVALID_IMAGE_DATA"
                else:
                    result_list = reader.readtext(img_np, detail=0, paragraph=True)
                    extracted_text = " ".join(result_list)
                    print(f"   [OCR SUCCESS] Extracted: {extracted_text[:50]}...")
                    
                    if extracted_text.strip():
                        final_text_to_analyze = extracted_text
                    else:
                        final_text_to_analyze = "NO_TEXT_FOUND_IN_IMAGE"
            else:
                print(f"   [ERROR] Download Failed with Status: {img_resp.status_code}")
                final_text_to_analyze = "DOWNLOAD_PERMISSION_DENIED"

        except Exception as e:
            print(f"   [ERROR] OCR Failed: {e}")
            final_text_to_analyze = "ERROR_PROCESSING_IMAGE"

    error_keywords = ["ERROR", "INVALID", "DENIED", "NO_TEXT"]
    if any(k in final_text_to_analyze for k in error_keywords) or len(final_text_to_analyze) < 5:
        resp = MessagingResponse()
        msg = resp.message()
        msg.body(f"🤖 *Satya-Check Error*\n\nI couldn't read the image. \nReason: {final_text_to_analyze}\n\nPlease type the text directly.")
        return str(resp)

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