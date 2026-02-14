
import streamlit as st
import os
import json
import datetime
import pytz
import re
from google import genai
from google.genai import types
from mistralai import Mistral
from groq import Groq
import streamlit.components.v1 as components
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Configuration & Setup ---
st.set_page_config(
    page_title="Nuestra Bóveda",
    page_icon="🌹",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# --- Helper: Secrets Management (Local vs Streamlit Cloud) ---
def get_secret(key):
    """
    Retrieves secret from Streamlit secrets (Cloud) or os.environ (Local).
    Prioritizes Streamlit secrets.
    """
    # 1. Try Streamlit Secrets
    try:
        if key in st.secrets:
            return st.secrets[key]
    except FileNotFoundError:
        pass # No secrets.toml found
        
    # 2. Try OS Environment (Local .env)
    return os.environ.get(key)

# --- LLM Ensemble Class ---
class LLMEnsemble:
    def __init__(self):
        self.gemini_key = get_secret("GOOGLE_API_KEY")
        self.mistral_key = get_secret("MISTRAL_API_KEY")
        self.groq_key = get_secret("GROQ_API_KEY")
        
        self.gemini_client = None
        self.mistral_client = None
        self.groq_client = None

        self._init_clients()

    def _init_clients(self):
        if self.gemini_key:
            try:
                self.gemini_client = genai.Client(api_key=self.gemini_key)
            except Exception as e:
                st.error(f"Gemini Init Error: {e}")
        else:
            st.warning("GOOGLE_API_KEY not found in secrets.")
        
        if self.mistral_key:
            try:
                self.mistral_client = Mistral(api_key=self.mistral_key)
            except Exception as e:
                st.error(f"Mistral Init Error: {e}")
        
        if self.groq_key:
            try:
                self.groq_client = Groq(api_key=self.groq_key)
            except Exception as e:
                st.error(f"Groq Init Error: {e}")

    def generate_content(self, prompt, system_instruction=None, json_mode=False):
        """
        Tries to generate content using Gemini -> Mistral -> Groq.
        Returns: (text_response, source_model_name)
        """
        errors = []

        # 1. Try Gemini
        if self.gemini_client:
            try:
                model_name = "gemini-2.0-flash"
                config = types.GenerateContentConfig(
                    response_mime_type="application/json" if json_mode else "text/plain",
                    system_instruction=system_instruction
                )
                response = self.gemini_client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config
                )
                return response.text, "Gemini 2.0 Flash"
            except Exception as e:
                errors.append(f"Gemini failed: {e}")

        # 2. Try Mistral
        if self.mistral_client:
            try:
                model_name = "mistral-large-latest"
                messages = []
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                messages.append({"role": "user", "content": prompt})
                
                response_format = {"type": "json_object"} if json_mode else None
                
                chat_response = self.mistral_client.chat.complete(
                    model=model_name,
                    messages=messages,
                    response_format=response_format
                )
                return chat_response.choices[0].message.content, "Mistral Large"
            except Exception as e:
                errors.append(f"Mistral failed: {e}")

        # 3. Try Groq
        if self.groq_client:
            try:
                model_name = "llama-3.3-70b-versatile"
                messages = []
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                messages.append({"role": "user", "content": prompt})

                response_format = {"type": "json_object"} if json_mode else None

                chat_completion = self.groq_client.chat.completions.create(
                    messages=messages,
                    model=model_name,
                    response_format=response_format
                )
                return chat_completion.choices[0].message.content, "Groq Llama 3"
            except Exception as e:
                errors.append(f"Groq failed: {e}")
        
        # If all fail
        return json.dumps({"error": "All LLMs failed", "details": errors}) if json_mode else f"System Malfunction. All AI Cores Unresponsive. Errors: {errors}", "None"

# Initialize Ensemble
llm_ensemble = LLMEnsemble()


# --- Custom CSS (Glassmorphism & Futuristic UI) ---
def render_css():
    st.markdown("""
        <style>
        /* General App Styling */
        .stApp {
            background-color: #000000 !important;
            font-family: 'Inter', sans-serif;
            color: #E0E0E0 !important;
            overflow-x: hidden;
        }
        
        /* Force Text Colors for Readability */
        p, h1, h2, h3, h4, h5, h6, li, span, div {
            color: #E0E0E0 !important;
        }

        /* Hide Streamlit Elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        div[data-testid="stToolbar"] {visibility: hidden;}
        
        /* 3D Background Grid Animation */
        .stApp::before {
            content: '';
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: 
                linear-gradient(rgba(0, 210, 255, 0.1) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 210, 255, 0.1) 1px, transparent 1px);
            background-size: 50px 50px;
            transform-origin: center top;
            transform: perspective(500px) rotateX(60deg) translateY(-100px) scale(3);
            animation: gridMove 20s linear infinite;
            z-index: -1;
            pointer-events: none;
            opacity: 0.3;
        }

        @keyframes gridMove {
            0% { transform: perspective(500px) rotateX(60deg) translateY(0) scale(3); }
            100% { transform: perspective(500px) rotateX(60deg) translateY(50px) scale(3); }
        }
        
        /* Glassmorphism Card Style */
        .glass-card {
            background: rgba(10, 20, 30, 0.6);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-radius: 16px;
            border: 1px solid rgba(0, 210, 255, 0.2);
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 0 20px rgba(0, 210, 255, 0.1), inset 0 0 20px rgba(0, 210, 255, 0.05);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .glass-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 0 40px rgba(0, 210, 255, 0.3), inset 0 0 30px rgba(0, 210, 255, 0.1);
            border-color: rgba(0, 210, 255, 0.5);
        }

        /* Identity Cards */
        .identity-btn {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 200px;
            width: 100%;
            cursor: pointer;
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
        }
        
        /* Input Field Styling */
        div[data-testid="stTextInput"] input {
             background-color: rgba(5, 5, 5, 0.8) !important;
             border: 1px solid rgba(0, 210, 255, 0.3) !important;
             color: #00d2ff !important;
             font-family: 'Courier New', monospace;
             border-radius: 4px;
             text-align: center;
             font-size: 0.9rem;
             letter-spacing: 2px;
             box-shadow: inset 0 0 10px rgba(0,0,0,0.8);
        }
        div[data-testid="stTextInput"] input:focus {
             border-color: #00d2ff !important;
             box-shadow: 0 0 25px rgba(0, 210, 255, 0.4);
             outline: none;
        }
        
        /* Tab Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
            border-bottom: 1px solid rgba(0, 210, 255, 0.2);
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: transparent;
            border-radius: 4px 4px 0 0;
            color: rgba(0, 210, 255, 0.5) !important;
            font-size: 1.1rem;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: rgba(0, 210, 255, 0.1);
            color: #00d2ff !important;
            border-bottom: 2px solid #00d2ff;
            text-shadow: 0 0 10px rgba(0, 210, 255, 0.8);
        }
        
        </style>
    """, unsafe_allow_html=True)

render_css()

# --- Session State Management ---
if 'unlocked' not in st.session_state:
    st.session_state.unlocked = False
if 'identified' not in st.session_state:
    st.session_state.identified = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'target_persona' not in st.session_state:
    st.session_state.target_persona = None
if 'ghost_messages' not in st.session_state:
    st.session_state.ghost_messages = []


# --- Helper Functions ---
@st.cache_data
def load_memories():
    try:
        with open('assets/memories.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

@st.cache_data
def load_chat_history():
    try:
        with open('whatsapp_chat.txt', 'r', encoding='utf-8') as f:
            # OPTIMIZATION: Read only the last 15,000 characters to prevent Context Window overflow
            text = f.read()
            return text[-15000:] 
    except FileNotFoundError:
        return ""


# --- Security Layer (Rate Limiting & Anti-Automation) ---
class SecurityLayer:
    def __init__(self):
        # Persistent storage for failed attempts (Global)
        if 'failed_attempts' not in st.session_state:
            st.session_state.failed_attempts = [] # List of timestamps
        
        # Last request timestamp for automation check (Session-based)
        if 'last_request_time' not in st.session_state:
            st.session_state.last_request_time = 0

    def check_automation(self):
        """
        Discourage automation: Reject requests < 0.5s apart.
        """
        current_time = datetime.datetime.now().timestamp()
        last_time = st.session_state.last_request_time
        
        # Update last request time
        st.session_state.last_request_time = current_time
        
        if (current_time - last_time) < 0.5:
            return False, "Automation Detected. Slow down."
        return True, ""

    def check_rate_limit(self):
        """
        Global-ish Rate Limit: Max 10 failed attempts per hour per session.
        (Note: In a real app this would be IP based via DB/Redis)
        """
        now = datetime.datetime.now()
        # Filter attempts within the last hour
        st.session_state.failed_attempts = [t for t in st.session_state.failed_attempts if (now - t).total_seconds() < 3600]
        
        if len(st.session_state.failed_attempts) >= 10:
            return False, "System Locked. Too many attempts. Try again later."
        return True, ""

    def log_failure(self):
        """Log a failed attempt timestamp."""
        st.session_state.failed_attempts.append(datetime.datetime.now())

security = SecurityLayer()


# --- Decryption Service ---
from cryptography.fernet import Fernet
import io

@st.cache_resource
def get_cipher():
    key = get_secret("VAULT_KEY")
    if key:
        return Fernet(key)
    return None

def decrypt_data(file_path, is_json=False, is_text=False):
    """
    Decrypts a file and returns its content.
    If VAULT_KEY is invalid or file not encrypted, tries to read as plain text backup.
    """
    cipher = get_cipher()
    
    # Try Encrypted Path first
    enc_path = file_path + ".enc"
    
    if os.path.exists(enc_path) and cipher:
        try:
            with open(enc_path, "rb") as f:
                encrypted_data = f.read()
            decrypted_data = cipher.decrypt(encrypted_data)
            
            if is_json:
                return json.loads(decrypted_data.decode('utf-8'))
            if is_text:
                return decrypted_data.decode('utf-8')
            return decrypted_data # Return bytes for media
            
        except Exception as e:
            st.error(f"Decryption Error for {file_path}: {e}")
            return None

    # Fallback: Read plaintext file (for local dev or if not encrypted)
    if os.path.exists(file_path):
        if is_json:
            with open(file_path, 'r') as f: return json.load(f)
        if is_text:
            with open(file_path, 'r', encoding='utf-8') as f: return f.read()
        with open(file_path, 'rb') as f: return f.read()
        
    return None

# --- Helper Functions (Updated for Encryption) ---
@st.cache_data
def load_memories():
    data = decrypt_data('assets/memories.json', is_json=True)
    return data if data else []

@st.cache_data
def load_chat_history():
    # Only read last 15000 chars even from encrypted data
    text = decrypt_data('whatsapp_chat.txt', is_text=True)
    if text:
        return text[-15000:]
    return ""

def parser_date_input(input_str):
    """
    Robustly parses flexible date strings into (YYYY, MM, DD) tuple.
    Accepts: 1/1/26, 01-01-2026, 1 jan 2026, 1st jan 26, etc.
    """
    if not input_str:
        return None
    
    # 1. Anti-Automation Check
    is_human, auth_msg = security.check_automation()
    if not is_human:
        st.toast(auth_msg, icon="🤖")
        return None

    # 2. Rate Limit Check
    is_allowed, limit_msg = security.check_rate_limit()
    if not is_allowed:
        st.error(limit_msg)
        return None

    input_str = input_str.lower().strip()
    
    # Check for Year 2026
    if "26" not in input_str:
        security.log_failure()
        return None
        
    # Check for Jan/01/1
    if not any(x in input_str for x in ["jan", "01", "1"]):
        security.log_failure()
        return None
        
    # Valid patterns for 1st Jan 2026
    clean = re.sub(r'st|nd|rd|th|/|-|,|\s', '', input_str)
    
    # Possible permutations for 1st Jan 2026
    valid_fingerprints = [
        "1jan2026", "1jan26", "jan12026", "jan126",
        "01012026", "010126", "1126", "112026"
    ]
    
    if clean in valid_fingerprints:
        return True
    
    # Log failure if regex matches didn't pass
    security.log_failure()
    return False

# --- State 1: The Cover (The Trojan Horse) ---
def render_cover():
    
    # Premium Dashboard Header with Glitch Effect
    st.markdown("""
        <div style="text-align: center; margin-bottom: 40px; position: relative;">
            <div style="font-size: 0.9rem; letter-spacing: 6px; color: #00d2ff; text-transform: uppercase; margin-bottom: 10px; text-shadow: 0 0 10px rgba(0,210,255,0.5);">Secure Vault System</div>
            <h1 style="font-size: 4.5rem; letter-spacing: 12px; margin: 0; background: linear-gradient(to bottom, #fff, #aaa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 0 30px rgba(255,255,255,0.3);">NUESTRA BÓVEDA</h1>
            <div style="display: flex; justify-content: center; gap: 40px; font-size: 0.7rem; color: #666; margin-top: 15px;">
                <span style="border: 1px solid #333; padding: 5px 10px; border-radius: 4px;">STATUS: <span style="color: #0f0;">CONNECTED</span></span>
                <span style="border: 1px solid #333; padding: 5px 10px; border-radius: 4px;">PROTOCOL: <span style="color: #00d2ff;">V.9.0</span></span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    
    # CLIENT-SIDE JS CLOCK & DASHBOARD VISUALS (Added Delhi, 3D Canvas)
    dashboard_html = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body { margin: 0; background: transparent; font-family: 'Inter', sans-serif; overflow: hidden; }
        
        .container {
            display: flex;
            justify-content: center;
            gap: 20px;
            align-items: center;
            flex-wrap: wrap;
        }

        .clock-card {
            background: rgba(0, 10, 20, 0.8);
            border: 1px solid rgba(0, 210, 255, 0.3);
            border-radius: 8px;
            width: 140px;
            padding: 15px;
            text-align: center;
            position: relative;
            box-shadow: 0 0 20px rgba(0,0,0,0.8), inset 0 0 20px rgba(0, 210, 255, 0.05);
            transition: all 0.3s ease;
        }
        
        .clock-card:hover {
            border-color: #00d2ff;
            box-shadow: 0 0 30px rgba(0, 210, 255, 0.4);
            transform: scale(1.05);
        }
        
        .clock-card::after {
            content: '';
            position: absolute;
            bottom: 0; left: 20%; right: 20%; height: 2px;
            background: #00d2ff;
            box-shadow: 0 0 10px #00d2ff;
        }

        .city { 
            font-size: 0.7rem; 
            color: #00d2ff; 
            margin-bottom: 5px; 
            text-transform: uppercase; 
            letter-spacing: 2px;
            font-weight: 600;
        }
        
        .time { 
             font-family: 'Courier New', monospace;
            font-size: 1.5rem; 
            font-weight: 700; 
            color: #fff;
            text-shadow: 0 0 10px rgba(0, 210, 255, 0.8);
        }
        
        .date { font-size: 0.6rem; color: #555; margin-top: 5px; text-transform: uppercase; }

        /* Fake Graph CSS */
        .graph-container {
            display: flex;
            justify-content: space-between;
            margin-top: 40px;
            padding: 0 20px;
        }
        .stat-block {
            flex: 1;
            height: 80px;
            background: rgba(0,0,0,0.5);
            border: 1px solid #222;
            border-radius: 4px;
            position: relative;
            overflow: hidden;
            margin: 0 10px;
        }
        
        /* Laser Beam Animation */
        .laser-beam {
            position: absolute;
            top: 50%; left: 0; width: 100%; height: 2px;
            background: red;
            box-shadow: 0 0 10px red;
            opacity: 0.5;
            animation: laserScan 3s infinite linear;
        }
        @keyframes laserScan {
            0% { top: 10%; opacity: 0; }
            10% { opacity: 1; }
            90% { opacity: 1; }
            100% { top: 90%; opacity: 0; }
        }
        
        .stat-label {
            position: absolute;
            top: 5px; left: 5px;
            font-size: 0.5rem; color: #00d2ff; letter-spacing: 1px;
        }

    </style>
    </head>
    <body>
        <div class="container">
            <div class="clock-card">
                <div class="city">Montreal</div>
                <div class="time" id="time-montreal">--:--:--</div>
                <div class="date" id="date-montreal"></div>
            </div>
            <div class="clock-card">
                <div class="city">Paris</div>
                <div class="time" id="time-paris">--:--:--</div>
                <div class="date" id="date-paris"></div>
            </div>
            <div class="clock-card">
                <div class="city">Dubai</div>
                <div class="time" id="time-dubai">--:--:--</div>
                <div class="date" id="date-dubai"></div>
            </div>
             <div class="clock-card">
                <div class="city">Delhi</div>
                <div class="time" id="time-delhi">--:--:--</div>
                <div class="date" id="date-delhi"></div>
            </div>
            <div class="clock-card">
                <div class="city">Beijing</div>
                <div class="time" id="time-beijing">--:--:--</div>
                <div class="date" id="date-beijing"></div>
            </div>
        </div>

        <div class="graph-container">
             <div class="stat-block">
                <div class="stat-label">QUANTUM MEMORY LINK</div>
                <canvas id="canvas1" style="width: 100%; height: 100%;"></canvas>
             </div>
             <div class="stat-block">
                 <div class="laser-beam"></div>
                <div class="stat-label">BIOMETRIC SCAN</div>
             </div>
             <div class="stat-block">
                <div class="stat-label">TEMPORAL DRIFT</div>
                 <canvas id="canvas2" style="width: 100%; height: 100%;"></canvas>
             </div>
        </div>

        <script>
            function updateClocks() {
                const now = new Date();
                
                const options = { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' };
                const dateOptions = { weekday: 'short', month: 'short', day: 'numeric' };

                // Montreal (America/Montreal)
                const montrealTime = new Date(now.toLocaleString("en-US", {timeZone: "America/Montreal"}));
                document.getElementById('time-montreal').textContent = montrealTime.toLocaleTimeString('en-GB', options);
                document.getElementById('date-montreal').textContent = montrealTime.toLocaleDateString('en-GB', dateOptions);

                // Paris (Europe/Paris)
                const parisTime = new Date(now.toLocaleString("en-US", {timeZone: "Europe/Paris"}));
                document.getElementById('time-paris').textContent = parisTime.toLocaleTimeString('en-GB', options);
                document.getElementById('date-paris').textContent = parisTime.toLocaleDateString('en-GB', dateOptions);

                // Dubai (Asia/Dubai)
                const dubaiTime = new Date(now.toLocaleString("en-US", {timeZone: "Asia/Dubai"}));
                document.getElementById('time-dubai').textContent = dubaiTime.toLocaleTimeString('en-GB', options);
                document.getElementById('date-dubai').textContent = dubaiTime.toLocaleDateString('en-GB', dateOptions);

                // Delhi (Asia/Kolkata)
                const delhiTime = new Date(now.toLocaleString("en-US", {timeZone: "Asia/Kolkata"}));
                document.getElementById('time-delhi').textContent = delhiTime.toLocaleTimeString('en-GB', options);
                document.getElementById('date-delhi').textContent = delhiTime.toLocaleDateString('en-GB', dateOptions);

                // Beijing (Asia/Shanghai)
                const beijingTime = new Date(now.toLocaleString("en-US", {timeZone: "Asia/Shanghai"}));
                document.getElementById('time-beijing').textContent = beijingTime.toLocaleTimeString('en-GB', options);
                document.getElementById('date-beijing').textContent = beijingTime.toLocaleDateString('en-GB', dateOptions);
            }

            setInterval(updateClocks, 1000);
            updateClocks();
            
            // Simple Sine Wave Animation for Graphs
            function drawSine(canvasId, speed) {
                const canvas = document.getElementById(canvasId);
                const ctx = canvas.getContext('2d');
                let width = canvas.width = canvas.offsetWidth;
                let height = canvas.height = canvas.offsetHeight;
                let phase = 0;
                
                function animate() {
                    ctx.clearRect(0, 0, width, height);
                    ctx.beginPath();
                    ctx.moveTo(0, height/2);
                    for(let i=0; i<width; i++) {
                        ctx.lineTo(i, height/2 + Math.sin(i * 0.05 + phase) * 20);
                    }
                    ctx.strokeStyle = '#00d2ff';
                    ctx.lineWidth = 1.5;
                    ctx.stroke();
                    phase += speed;
                    requestAnimationFrame(animate);
                }
                animate();
            }
            
            drawSine('canvas1', 0.1);
            drawSine('canvas2', 0.15);
        </script>
    </body>
    </html>
    """
    
    components.html(dashboard_html, height=450)

    # Input Logic (Minimized and Obscure)
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.5, 1, 1.5])
    with c2:
        # Minimized Input
        system_sync = st.text_input("PROTOCOL", placeholder=":: ACCESS KEY ::", help="Enter Timeline Origin", label_visibility="collapsed")
        
        if system_sync:
            if parser_date_input(system_sync):
                st.session_state.unlocked = True
                st.rerun()
            elif len(system_sync) > 0:
                st.toast("Access Denied.", icon="🔒")

# --- State 2: The Identity Gateway ---
def render_identity():
    st.markdown("<div style='height: 15vh;'></div>", unsafe_allow_html=True)
    st.markdown("<h1 class='glow-text' style='text-align: center; font-size: 3rem; letter-spacing: 5px; text-shadow: 0 0 40px #00d2ff;'>IDENTITY GATEWAY</h1>", unsafe_allow_html=True)
    st.markdown("<div style='width: 100px; height: 100px; margin: 0 auto 50px auto; border-radius: 50%; border: 2px solid #00d2ff; box-shadow: 0 0 50px #00d2ff; animation: pulse 2s infinite;'></div>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns([1, 2, 2, 1])
    
    with c2:
        if st.button("🙎‍♀️ I am Anghily", use_container_width=True, type="primary"):
            st.session_state.current_user = "Anghily"
            st.session_state.target_persona = "Armaan"
            st.session_state.identified = True
            st.rerun()
            
    with c3:
        if st.button("🙎‍♂️ I am Armaan", use_container_width=True, type="primary"):
            st.session_state.current_user = "Armaan"
            st.session_state.target_persona = "Anghily"
            st.session_state.identified = True
            st.rerun()

# --- State 3: The Vault (Main App) ---
def render_vault():
    st.markdown(f"<div style='text-align: center; margin-bottom: 20px;'><span style='color: #00d2ff; letter-spacing: 2px;'>USER AUTHENTICATED:</span> <span style='color: #fff; font-weight: bold;'>{st.session_state.current_user.upper()}</span></div>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔮 MEMORY ORACLE", "👻 GHOST WRITER"])
    
    # --- Tab 1: Memory Oracle ---
    with tab1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        mood = st.text_input("CURRENT EMOTIONAL STATE", placeholder="Analyze mood parameters...", label_visibility="visible")
        st.markdown("</div>", unsafe_allow_html=True)
        
        if mood:
            with st.spinner("Accessing Neural Archives..."):
                memories = load_memories()
                if not memories:
                    st.error("Memory banks are empty (assets/memories.json not found).")
                else:
                    try:
                        prompt = f"""
                        You are the magical curator of a couple's love story.
                        User ({st.session_state.current_user}) is feeling: '{mood}'.
                        Target Persona (Author of message): {st.session_state.target_persona}.
                        
                        Here are the available memories:
                        {json.dumps(memories)}
                        
                        Task:
                        1. Analyze the user's mood ('{mood}') deeply.
                        2. Select the ONE memory from the provided list that BEST resonates with this mood. Do NOT just pick the first one.
                        3. Write a short, poetic, loving message.
                        
                        Return STRICT JSON format:
                        {{
                            "reasoning": "Why I chose this memory for this mood...",
                            "file_path": "assets/Filename.ext",
                            "poetic_message": "Your message here..."
                        }}
                        """
                        
                        response_text, model_used = llm_ensemble.generate_content(
                            prompt=prompt,
                             json_mode=True
                        )
                        
                        try:
                            result = json.loads(response_text)
                            
                            c1, c2 = st.columns([1, 1])
                            with c1:
                                 # Decrypt and display image/video
                                 file_path = result.get("file_path", "")
                                 
                                 # Try to decrypt data
                                 file_data = decrypt_data(file_path)
                                 
                                 if file_data:
                                     st.markdown(f"<div style='border-radius: 12px; overflow: hidden; box-shadow: 0 0 30px rgba(0,210,255,0.3); border: 1px solid rgba(0,210,255,0.5);'>", unsafe_allow_html=True)
                                     if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                                         st.image(file_data, use_container_width=True)
                                     elif file_path.lower().endswith(('.mp4', '.mov')):
                                         # Streamlit video needs file path or bytes/io
                                         st.video(io.BytesIO(file_data))
                                     st.markdown("</div>", unsafe_allow_html=True)
                                 else:
                                     st.warning(f"Memory artifact missing or locked: {file_path}")

                            with c2:
                                st.markdown(f"""
                                <div class='glass-card' style='height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center;'>
                                    <div style='font-size: 1.3rem; font-style: italic; line-height: 1.6; color: #fff; text-shadow: 0 0 10px rgba(255,255,255,0.3);'>
                                        "{result.get('poetic_message', '')}"
                                    </div>
                                    <div style='margin-top: 20px; font-size: 0.8rem; color: #00d2ff;'>
                                        AI MODEL: {model_used}
                                    </div>
                                    <div style='margin-top: 10px; font-size: 0.7rem; color: #555;'>
                                        SELECTION LOGIC: {result.get('reasoning', 'N/A')}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                        except json.JSONDecodeError:
                            st.error(f"Oracle returned gibberish ({model_used}): {response_text}")
                            
                    except Exception as e:
                        st.error(f"The Oracle is clouded: {e}")

    # --- Tab 2: Ghost Writer ---
    with tab2:
        st.markdown("<p style='text-align: center; color: #00d2ff; font-family: monospace; letter-spacing: 2px;'>[ CONSCIOUSNESS UPLOAD COMPLETE ]</p>", unsafe_allow_html=True)
        
        # Display persistent chat history
        for msg in st.session_state.ghost_messages:
            with st.chat_message(msg["role"]):
                st.markdown(f"<span style='color: {'#fff' if msg['role']=='assistant' else '#aaa'};'>{msg['content']}</span>", unsafe_allow_html=True)
        
        # Chat Input
        if prompt := st.chat_input(f"Transmit to {st.session_state.target_persona}..."):
            # Add user message to history
            st.session_state.ghost_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate AI Response
            if llm_ensemble:
                chat_history_text = load_chat_history()
                
                system_instruction = f"""
                You are simulating {st.session_state.target_persona} in a WhatsApp conversation with {st.session_state.current_user}.
                
                Here is the COMPLETE chat history between them:
                {chat_history_text}
                
                RULES:
                1. Analyze the history DEEPLY. Mimic {st.session_state.target_persona}'s exact slang, emoji usage, sentence length, and tone.
                2. Reply directly to the user's last message.
                3. Do NOT sound like an AI. Be the person.
                4. Reply ONLY with the message text.
                """
                
                try:
                    with st.spinner(f"Intercepting neural pathway..."):
                        
                        bot_reply, model_used = llm_ensemble.generate_content(
                            prompt=f"User ({st.session_state.current_user}) says: {prompt}",
                            system_instruction=system_instruction
                        )
                        
                        # Add bot reply to history
                        st.session_state.ghost_messages.append({"role": "assistant", "content": bot_reply})
                        with st.chat_message("assistant"):
                            st.markdown(bot_reply)
                            st.caption(f"Thought from: {model_used}")
                            
                except Exception as e:
                    st.error(f"Connection lost to ghost realm: {e}")

# --- Main App Controller ---
if not st.session_state.unlocked:
    render_cover()
elif not st.session_state.identified:
    render_identity()
else:
    render_vault()
