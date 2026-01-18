# 🛡️ Satya-Check: AI-Powered Misinformation Detection System

![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen)
![Python](https://img.shields.io/badge/Python-3.9-blue)
![Next.js](https://img.shields.io/badge/Frontend-Next.js_14-black)
![AI Model](https://img.shields.io/badge/Model-BERT%20%2B%20Sentence--Transformers-orange)
![Docker](https://img.shields.io/badge/Deployment-Docker-2496ED)

**Satya-Check** is a sophisticated, multimodal (Text + Image) misinformation detection system designed specifically for the Indian context. Unlike standard detectors, it features a **Hybrid Architecture** that combines Deep Learning (MuRIL/BERT) with Real-Time Semantic Search to verify claims against live news sources, offering robust support for **Hinglish (Code-Mixed)** content.

---

## 🚀 Key Features (USP)

### 1. 🧠 Hybrid "Dual-Brain" Verification
* **Layer 1 (The Judge):** A fine-tuned BERT-based classifier detects linguistic patterns of fake news (clickbait, emotional manipulation).
* **Layer 2 (The Truth Serum):** Integrates **Google Custom Search API** to fetch real-time facts.
* **Layer 3 (Semantic Logic):** Uses **Sentence-Transformers (`all-MiniLM-L6-v2`)** to calculate Cosine Similarity between user claims and verified news. *This solves semantic ambiguity (e.g., distinguishing "Plays IN Pakistan" vs. "Plays FOR Pakistan").*

### 2. 🇮🇳 Native Hinglish Support
* Optimized for the Indian digital ecosystem.
* Accurately processes code-mixed text (e.g., *"Modi ji ne kaha..."*) using a custom tokenizer and phonetic search verification.

### 3. 📸 Multimodal Analysis (OCR)
* Integrates **EasyOCR** to extract and analyze text from images/screenshots (supporting Devanagari script).

### 4. 📲 WhatsApp Bot Integration
* A real-world integration using **Twilio API**.
* Users can forward suspicious messages or images directly to the bot for instant verification.

### 5. 🔍 Explainable AI (XAI)
* Doesn't just flag content; highlights **"Risk Keywords"** (e.g., *viral, miracle, forward*) to explain *why* content is suspicious.

### 6. 📊 Admin "Command Center"
* A comprehensive Dashboard (built with **Recharts**) to track misinformation trends, scan history, and model performance metrics in real-time.

---

## 🛠️ Tech Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Backend** | Python, Flask | Core API & Logic handling |
| **AI Models** | PyTorch, Transformers | Fake News Classification (MuRIL/BERT) |
| **NLP** | Sentence-Transformers | Semantic Similarity & Context Matching |
| **Vision** | EasyOCR, OpenCV | Extracting text from Images |
| **Frontend** | Next.js, TailwindCSS | Responsive User Interface |
| **Database** | SQLite | Lightweight logging for Analytics |
| **External APIs** | Google CSE, Twilio | Live Web Search & WhatsApp Integration |
| **DevOps** | Docker, Ngrok | Containerization & Tunneling |

---

## 📂 Installation Guide

### Prerequisites
* Python 3.8+
* Node.js & npm
* Google Cloud API Key (Custom Search JSON API)

### 1. Setup Backend (The Brain)
```bash
# Clone repository
git clone [https://github.com/Vineet-Sharma1927/Satya-Check.git](https://github.com/Vineet-Sharma1927/Satya-Check.git)
cd SatyaCheck_Project

# Create Virtual Environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install Dependencies
pip install -r requirements.txt

# Download Model Weights
Download the pre-trained model from Google Drive:
🔗 Model Download Link: [https://drive.google.com/file/d/12MwDgXl3dJBKHI9Yn2M6nWNhUPlkD_bL/view?usp=sharing]
Extract the 'model_output' folder to the project root directory