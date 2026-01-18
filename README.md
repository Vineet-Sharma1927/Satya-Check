# 🛡️ Satya-Check: AI-Powered Misinformation Detection System

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Next.js](https://img.shields.io/badge/Frontend-Next.js_14-black?style=for-the-badge&logo=next.js)
![AI Model](https://img.shields.io/badge/AI-BERT_%2B_MuRIL-orange?style=for-the-badge)
![Docker](https://img.shields.io/badge/Deployment-Docker-2496ED?style=for-the-badge&logo=docker)
![Status](https://img.shields.io/badge/Status-Production_Ready-brightgreen?style=for-the-badge)

> **A Multimodal (Text + Image) Fake News Detection System engineered for the Indian digital ecosystem. It leverages a Hybrid Architecture combining Deep Learning with Real-Time Cross-Verification.**

---

## 🚀 Project Overview

**Satya-Check** is designed to solve the problem of **"Concept Drift"** in fake news detection. Traditional models trained on static datasets fail to detect modern rumors (e.g., 2026 Elections, Deepfakes).

Satya-Check solves this by implementing a **Dual-Brain Architecture**:
1.  **Static Brain:** A fine-tuned **MuRIL/BERT** model that understands linguistic patterns (clickbait, toxicity, emotion).
2.  **Dynamic Brain:** A **Semantic Search Engine** that cross-verifies claims against live Google News results to fact-check in real-time.

---

## 🌟 Key Features (USP)

### 1. 🇮🇳 Native Hinglish Support
* **Problem:** Standard AI models fail on code-mixed text like *"Modi ji ne kaha..."*
* **Solution:** Used **MuRIL (Multilingual Representations for Indian Languages)** and custom tokenizers to accurately process Hindi-English mixed scripts.

### 2. 🧠 Hybrid "Dual-Layer" Verification
* **Layer 1 (Pattern Recognition):** Classifies text based on writing style (Probability of Fake: 85%).
* **Layer 2 (Semantic Fact-Checking):** Uses **Sentence-Transformers (`all-MiniLM-L6-v2`)** to compare the user's claim with verified news sources.
* **Verdict Logic:** A weighted ensemble of both layers ensures high accuracy.

### 3. 📸 Multimodal Analysis (OCR)
* Integrated **EasyOCR** with OpenCV to extract text from images and screenshots, specifically optimized for **Devanagari** and low-quality WhatsApp forwards.

### 4. 📲 WhatsApp Bot Integration
* **Real-World Application:** Users can forward suspicious messages or images directly to a **Twilio-powered WhatsApp Bot**.
* The bot processes the query via the backend API and replies with a verdict and verified sources in seconds.

### 5. 🔍 Explainable AI (XAI)
* **Trust & Safety:** The system doesn't just say "Fake." It uses **LIME-inspired Logic** to highlight specific "Risk Keywords" (e.g., *viral, miracle, guaranteed*) to explain *why* the content was flagged.

---

## 🛠️ Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend** | Python, Flask | REST API Architecture |
| **AI/ML** | PyTorch, Transformers | BERT, MuRIL, Sentence-Transformers |
| **Computer Vision** | OpenCV, EasyOCR, PIL | Image pre-processing & Text Extraction |
| **Frontend** | Next.js, TailwindCSS | Responsive, modern UI with Admin Dashboard |
| **Database** | SQLite | Lightweight logging for analytics & search history |
| **DevOps** | Docker, Ngrok | Containerization and Tunneling for local demo |
| **External APIs** | Google CSE, Twilio | Live Web Search & WhatsApp Webhooks |

---

## ⚡ Installation & Setup

### Prerequisites
* Python 3.9+
* Node.js & npm
* [Optional] Docker Desktop

### 1. Clone the Repository
```bash
git clone https://github.com/Vineet-Sharma1927/Satya-Check.git
cd Satya-Check
```

### 2. Backend Setup (The Brain)
**Note:** The AI model weights are hosted externally due to size. Download `model_output.zip` from [Link provided in Project Report] and place it in the root directory.

```bash
# Create Virtual Environment
python -m venv venv
# Activate it (Windows)
venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt

# Run the Server
python app.py
```

### 3. Frontend Setup (The Interface)
```bash
cd satya-frontend
npm install
npm run dev
```

### 4. One-Click Launch (Windows)
Simply double-click the `LAUNCH_SATYA.bat` file in the root directory to start the entire system automatically.

---

## 🤖 How to Use the WhatsApp Bot

1. Ensure the Backend is running on Port 5000.
2. Start Ngrok tunneling:

```bash
ngrok http 5000
```

3. Copy the forwarding URL (e.g., `https://xyz.ngrok-free.app`) to your Twilio Sandbox settings.
4. Send a text or image to your Twilio Sandbox number!

---

## 🔬 Methodology & Research

This project builds upon the MMIFND (Multimodal Multilingual Indic Fake News Detection) framework.

* **Base Dataset:** 20,000+ samples from Zenodo (Historical Data)
* **Augmentation:** Live scraped data from Google News (2024-2026) to handle recent events
* **Algorithm:** Cosine Similarity thresholding (>0.85) for context verification