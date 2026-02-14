
# 🌹 Nuestra Bóveda (Our Vault)

> *A futuristic, AI-powered digital time capsule and communication interface.*

**Nuestra Bóveda** is a private, secure web application designed to preserve shared memories and simulate cross-time communication. Built with a "Mission Control" aesthetic, it utilizes advanced prompt engineering and an ensemble of Large Language Models (LLMs) to create a deeply personal and immersive user experience.

## 🚀 Features

### 1. The Chronos Terminal (Trojan Horse Cover)
-   **Security Through Obscurity**: Masquerades as a global time zone dashboard.
-   **Futuristic UI**: Custom CSS/JS animations including 3D grid backgrounds, floating laser effects, and neon-glassmorphism styling.
-   **Secure Access**: A hidden, minimized protocol input that requires a specific date-key to unlock the core system.

### 2. The Identity Gateway
-   **Dual-Persona Authentication**: A branching identity verification system that adapts the UI and context based on who is logging in.

### 3. The Vault (Core Application)
-   **🔮 Memory Oracle**: An AI-augmented retrieval system. Users input their current emotional state, and the system uses **Google Gemini 2.0 Flash** (via a fail-safe ensemble) to select the perfect memory from a private JSON database and generate a poetic reflection.
-   **👻 Ghost Writer**: A context-aware chat simulation. The system ingests historical chat logs (e.g., WhatsApp) to mimic the tone, slang, and personality of a specific user, allowing for "simulated" conversations with a partner's digital twin.

## 🛠️ Technical Architecture

This project pushes the boundaries of standard Python web frameworks by injecting custom frontend code into the backend logic.

-   **Frontend**: Streamlit (Python) with heavy custom CSS3 & JavaScript injection for 3D effects and animations.
-   **AI Engine (The Ensemble)**: A robust `LLMEnsemble` class that manages failover between multiple providers:
    1.  **Primary**: Google Gemini 2.0 Flash
    2.  **Fallback**: Mistral Large
    3.  **Emergency**: Groq (Llama 3)
-   **Security**: 
    -   **Rate Limiting**: Global limit of 10 failed unlock attempts per hour.
    -   **Anti-Automation**: Minimum 0.5s delay between requests to discourage brute-force scripts.
    -   **Environment Variables**: API keys managed securely via `.env`.

## 📦 Installation & Setup

This repository contains the source code *engine*. You must provide your own private data assets.

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/NuestraBoveda.git
    cd NuestraBoveda
    ```

2.  **Set Up Virtual Environment**
    ```bash
    python3 -m venv environ
    source environ/bin/activate
    pip install -r requirements.txt
    ```

3.  **Configure Environment**
    Copy `.env.example` to `.env` and add your API keys:
    ```bash
    cp .env.example .env
    # Edit .env with your keys for Google, Mistral, and Groq
    ```

4.  **Add Private Assets (Encrypted or Plain)**
    *   **Option A (Local)**: Place your `whatsapp_chat.txt` and `assets/*` files normally. The app reads them as plaintext if no `.enc` version exists.
    *   **Option B (Public Repo - Recommended)**: Run `python encrypt_vault.py` to encrypt your assets.
        *   Commit the `.enc` files.
        *   Add `VAULT_KEY` to your `.env` (local) or Streamlit Secrets (Cloud).

5.  **Launch**
    ```bash
    streamlit run app.py
    ```

## ☁️ Deployment on Streamlit Cloud

1.  Push your code to GitHub (ensure `.env`, `whatsapp_chat.txt` and unencrypted assets are IGNORED).
2.  Go to [share.streamlit.io](https://share.streamlit.io) and deploy the repo.
3.  **Advanced Settings -> Secrets**:
    Copy the contents of your `.env` file here. It should look like this:
    ```toml
    GOOGLE_API_KEY = "..."
    VAULT_KEY = "..."
    # etc...
    ```
4.  The app will auto-detect the cloud secrets and decrypt your assets!

## 🔒 Privacy Notice

This project is open-source, but it is designed to host **highly private data**.
*   **Code**: The logic is public.
*   **Data**: 
    *   **Git-Ignored**: Plaintext `whatsapp_chat.txt` and `assets/*` are ignored.
    *   **Encrypted**: You can safely commit `*.enc` files. They are AES-256 encrypted and unreadable without the `VAULT_KEY`.
    *   **Secrets**: API keys and `VAULT_KEY` live in `.env` (never committed).

---
*Created by Armaan Sidhu*
