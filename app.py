import streamlit as st
import time
import os
import io
import base64
import requests
from PIL import Image

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="VoiceVision — by Shivam Dave",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  AZURE CREDENTIALS (from your notebook)
# ─────────────────────────────────────────────
CV_ENDPOINT = "https://cv97898657.cognitiveservices.azure.com/"
CV_API_KEY  = "3rjI2tJgEjvUS9ve9DnwGTdgu0JW5B5i0u2mE8QpRzgaCPh4l1AwJQQJ99CEACYeBjFXJ3w3AAAFACOG0FxE"
SPEECH_KEY    = "2LNcNfQUrK6f0jj3eZ1ssHm1qALaeiXmn1foajdEdGGo9bxH06i5JQQJ99CEACYeBjFXJ3w3AAAYACOGrjDr"
SPEECH_REGION = "eastus"

# ─────────────────────────────────────────────
#  VOICES
# ─────────────────────────────────────────────
VOICES = {
    "🇺🇸 Jenny (US Female)"       : "en-US-JennyNeural",
    "🇺🇸 Guy (US Male)"           : "en-US-GuyNeural",
    "🇺🇸 Aria (US Female)"        : "en-US-AriaNeural",
    "🇺🇸 Davis (US Male)"         : "en-US-DavisNeural",
    "🇬🇧 Sonia (UK Female)"       : "en-GB-SoniaNeural",
    "🇬🇧 Ryan (UK Male)"          : "en-GB-RyanNeural",
    "🇮🇳 Neerja (Indian Female)"  : "en-IN-NeerjaNeural",
    "🇮🇳 Prabhat (Indian Male)"   : "en-IN-PrabhatNeural",
    "🇦🇺 Natasha (AU Female)"     : "en-AU-NatashaNeural",
    "🇦🇺 William (AU Male)"       : "en-AU-WilliamNeural",
}

# ─────────────────────────────────────────────
#  CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

:root {
    --bg:       #050508;
    --surface:  #0d0d14;
    --border:   #1e1e2e;
    --accent:   #7c5cfc;
    --accent2:  #e05fff;
    --gold:     #f5c842;
    --text:     #e8e8f0;
    --muted:    #6b6b80;
    --success:  #3dffc0;
    --danger:   #ff4d6d;
}

* { box-sizing: border-box; margin: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg);
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    top: -40%;
    left: -20%;
    width: 80vw;
    height: 80vw;
    background: radial-gradient(circle, rgba(124,92,252,0.12) 0%, transparent 65%);
    pointer-events: none;
    z-index: 0;
}
[data-testid="stAppViewContainer"]::after {
    content: '';
    position: fixed;
    bottom: -40%;
    right: -20%;
    width: 70vw;
    height: 70vw;
    background: radial-gradient(circle, rgba(224,95,255,0.08) 0%, transparent 65%);
    pointer-events: none;
    z-index: 0;
}

[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { background: var(--surface); border-right: 1px solid var(--border); }

/* ── HERO ── */
.hero {
    text-align: center;
    padding: 3.5rem 1rem 2rem;
    position: relative;
}
.hero-badge {
    display: inline-block;
    background: linear-gradient(135deg, rgba(124,92,252,0.2), rgba(224,95,255,0.2));
    border: 1px solid rgba(124,92,252,0.4);
    border-radius: 999px;
    padding: 0.35rem 1.1rem;
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #b39dfd;
    margin-bottom: 1.4rem;
    font-family: 'Syne', sans-serif;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.8rem, 6vw, 5.2rem);
    font-weight: 800;
    line-height: 1.05;
    background: linear-gradient(135deg, #fff 30%, #b39dfd 65%, #e05fff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.8rem;
}
.hero-sub {
    font-size: 1.05rem;
    color: var(--muted);
    max-width: 540px;
    margin: 0 auto 0.6rem;
    font-weight: 300;
    line-height: 1.65;
}
.byline {
    font-size: 0.78rem;
    color: #4a4a60;
    letter-spacing: 0.08em;
    font-family: 'Syne', sans-serif;
}
.byline span { color: var(--gold); }

/* ── DIVIDER ── */
.grad-line {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent), var(--accent2), transparent);
    margin: 0.5rem 0 2.5rem;
    opacity: 0.5;
}

/* ── MODE CARDS ── */
.mode-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    gap: 1rem;
    margin-bottom: 2.5rem;
}
.mode-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.4rem 1.2rem;
    cursor: pointer;
    transition: all 0.25s ease;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.mode-card::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(124,92,252,0.08), rgba(224,95,255,0.06));
    opacity: 0;
    transition: opacity 0.25s;
}
.mode-card:hover::before, .mode-card.active::before { opacity: 1; }
.mode-card.active {
    border-color: var(--accent);
    box-shadow: 0 0 0 1px rgba(124,92,252,0.4), 0 8px 32px rgba(124,92,252,0.15);
}
.mode-icon { font-size: 2rem; margin-bottom: 0.5rem; display: block; }
.mode-label { font-family: 'Syne', sans-serif; font-size: 0.82rem; font-weight: 600; color: var(--text); }
.mode-desc { font-size: 0.72rem; color: var(--muted); margin-top: 0.25rem; line-height: 1.4; }

/* ── PANELS ── */
.panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    position: relative;
}
.panel-title {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    color: var(--text);
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ── RESULT BOX ── */
.result-box {
    background: #09090f;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    font-size: 0.95rem;
    line-height: 1.75;
    color: var(--text);
    white-space: pre-wrap;
    word-break: break-word;
    min-height: 80px;
    margin-top: 1rem;
}

/* ── VOICE PILL ── */
.voice-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1rem;
}
.voice-pill {
    padding: 0.4rem 0.9rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-family: 'Syne', sans-serif;
    border: 1px solid var(--border);
    background: var(--surface);
    cursor: pointer;
    transition: all 0.18s;
    color: var(--muted);
}
.voice-pill:hover { border-color: var(--accent); color: var(--text); }
.voice-pill.active { border-color: var(--accent); background: rgba(124,92,252,0.15); color: #b39dfd; }

/* ── BUTTONS ── */
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    padding: 0.75rem 1.5rem !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 20px rgba(124,92,252,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(124,92,252,0.45) !important;
}

/* ── SELECT / TEXT ── */
.stSelectbox > div > div, .stTextArea > div > div > textarea {
    background: #09090f !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(124,92,252,0.2) !important;
}

/* ── AUDIO PLAYER ── */
audio { width: 100%; border-radius: 10px; margin-top: 1rem; }

/* ── STATS ROW ── */
.stat-row {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-top: 1rem;
}
.stat-chip {
    background: rgba(124,92,252,0.1);
    border: 1px solid rgba(124,92,252,0.25);
    border-radius: 8px;
    padding: 0.35rem 0.75rem;
    font-size: 0.75rem;
    color: #b39dfd;
    font-family: 'Syne', sans-serif;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {
    border: 2px dashed var(--border) !important;
    border-radius: 16px !important;
    background: #09090f !important;
    transition: border-color 0.2s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
}

/* ── SUCCESS / ERROR ── */
.stAlert { border-radius: 12px !important; }

/* ── FOOTER ── */
.footer {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    color: #333345;
    font-size: 0.75rem;
    font-family: 'Syne', sans-serif;
    letter-spacing: 0.06em;
}
.footer span { color: var(--accent); }

/* ── TABS ── */
[data-baseweb="tab-list"] { gap: 0.5rem !important; background: transparent !important; }
[data-baseweb="tab"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--muted) !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.82rem !important;
}
[aria-selected="true"] {
    background: rgba(124,92,252,0.18) !important;
    border-color: var(--accent) !important;
    color: var(--text) !important;
}

/* ── SPINNER ── */
[data-testid="stSpinner"] { color: var(--accent) !important; }

/* hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  HERO SECTION
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">Azure · OCR · TTS · AI Pipeline</div>
    <h1>VoiceVision</h1>
    <p class="hero-sub">Transform any image into spoken words. Extract, read, and listen — powered by Azure Cognitive Services.</p>
    <p class="byline">Developed by <span>Shivam Dave</span></p>
</div>
<div class="grad-line"></div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  MODE SELECTOR
# ─────────────────────────────────────────────
st.markdown("""
<div class="panel-title" style="justify-content:center; font-size:0.82rem; color:var(--muted); letter-spacing:0.1em; text-transform:uppercase; margin-bottom:1rem;">
  ⚡ Select a Mode
</div>""", unsafe_allow_html=True)

MODES = {
    "🖼️ Image → Speech": ("Full Pipeline", "Upload image → OCR → Speech"),
    "🔍 Image → Text":   ("OCR Only",      "Extract text from any image"),
    "🔊 Text → Speech":  ("TTS Only",      "Type or paste text, hear it"),
}

mode = st.radio(
    "Mode",
    list(MODES.keys()),
    horizontal=True,
    label_visibility="collapsed",
)

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  VOICE SELECTOR (shown when TTS needed)
# ─────────────────────────────────────────────
def voice_selector():
    st.markdown('<div class="panel-title">🎙️ Choose Voice</div>', unsafe_allow_html=True)
    selected = st.selectbox(
        "Voice",
        list(VOICES.keys()),
        index=6,   # default: Neerja Indian
        label_visibility="collapsed",
    )
    return VOICES[selected], selected

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def run_ocr(image_bytes):
    headers = {
        "Ocp-Apim-Subscription-Key": CV_API_KEY,
        "Content-Type": "application/octet-stream",
    }
    poll_headers = {"Ocp-Apim-Subscription-Key": CV_API_KEY}
    base = CV_ENDPOINT.rstrip("/")

    # Try v3.2 first, then v3.1 as fallback
    for api_ver in ["v3.2", "v3.1"]:
        read_url = f"{base}/vision/{api_ver}/read/analyze"
        resp = requests.post(read_url, headers=headers, data=image_bytes)

        if resp.status_code == 202:          # accepted — proceed
            operation_url = resp.headers["Operation-Location"]
            break
        elif resp.status_code == 404:        # wrong version, try next
            continue
        else:
            # Show the real Azure error message on screen
            try:
                err_body = resp.json()
                err_msg  = err_body.get("error", {}).get("message", resp.text)
            except Exception:
                err_msg = resp.text
            st.error(f"❌ Azure OCR Error {resp.status_code}: {err_msg}")
            return ""
    else:
        st.error("❌ Azure endpoint not reachable. Check your CV_ENDPOINT.")
        return ""

    # Poll until complete
    for _ in range(30):
        time.sleep(1)
        poll      = requests.get(operation_url, headers=poll_headers)
        poll_data = poll.json()
        status    = poll_data.get("status", "")
        if status not in ["notStarted", "running"]:
            break

    # Extract text
    text = ""
    if status == "succeeded":
        for read_result in poll_data.get("analyzeResult", {}).get("readResults", []):
            for line in read_result.get("lines", []):
                text += line.get("text", "") + " "
    elif status == "failed":
        st.error(f"❌ OCR processing failed: {poll_data}")
    return text.strip()


def run_tts(text, voice_name, out_path="output_audio.wav"):
    import azure.cognitiveservices.speech as speechsdk

    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    speech_config.speech_synthesis_voice_name = voice_name
    audio_config  = speechsdk.audio.AudioOutputConfig(filename=out_path)
    synthesizer   = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    result = synthesizer.speak_text_async(text).get()
    return result.reason.name == "SynthesizingAudioCompleted", out_path


def audio_player(path):
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    st.markdown(
        f'<audio controls autoplay><source src="data:audio/wav;base64,{b64}" type="audio/wav"></audio>',
        unsafe_allow_html=True,
    )
    with open(path, "rb") as f:
        st.download_button("⬇️  Download Audio", f, file_name="voicevision_output.wav",
                           mime="audio/wav", use_container_width=True)


# ─────────────────────────────────────────────
#  MODE: IMAGE → SPEECH  (Full Pipeline)
# ─────────────────────────────────────────────
if mode == "🖼️ Image → Speech":
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">📤 Upload Image</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader("Upload image", type=["png","jpg","jpeg","bmp","tiff"],
                                    label_visibility="collapsed")
        if uploaded:
            img = Image.open(uploaded)
            st.image(img, use_container_width=True)
            st.markdown(f'<div class="stat-row"><div class="stat-chip">📐 {img.size[0]}×{img.size[1]}</div><div class="stat-chip">🗂 {uploaded.type}</div></div>',
                        unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="panel">', unsafe_allow_html=True)
        voice_name, voice_label = voice_selector()
        st.markdown('</div>', unsafe_allow_html=True)

        go = st.button("🚀 Extract & Speak", use_container_width=True)

    with col2:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">📄 Extracted Text</div>', unsafe_allow_html=True)

        if go and uploaded:
            with st.spinner("🔍 Running Azure OCR…"):
                img_bytes = uploaded.read()
                extracted = run_ocr(img_bytes)

            if extracted:
                st.session_state["ocr_text"] = extracted
                st.success(f"✅ Extracted {len(extracted)} characters")
                st.markdown(f'<div class="result-box">{extracted}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="stat-row"><div class="stat-chip">🔤 {len(extracted.split())} words</div><div class="stat-chip">🎙️ {voice_label}</div></div>',
                            unsafe_allow_html=True)
            else:
                st.error("❌ No text detected. Try a clearer image.")
        elif "ocr_text" in st.session_state:
            extracted = st.session_state["ocr_text"]
            st.markdown(f'<div class="result-box">{extracted}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="result-box" style="color:var(--muted)">Extracted text will appear here…</div>',
                        unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">🔊 Audio Output</div>', unsafe_allow_html=True)

        if go and uploaded and "ocr_text" in st.session_state:
            with st.spinner("🎙️ Synthesising speech…"):
                ok, path = run_tts(st.session_state["ocr_text"], voice_name)
            if ok:
                audio_player(path)
            else:
                st.error("❌ TTS failed. Check your Azure Speech credentials.")
        else:
            st.markdown('<p style="color:var(--muted); font-size:0.85rem">Audio will appear after processing…</p>',
                        unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  MODE: IMAGE → TEXT  (OCR Only)
# ─────────────────────────────────────────────
elif mode == "🔍 Image → Text":
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">📤 Upload Image</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader("Upload image", type=["png","jpg","jpeg","bmp","tiff"],
                                    label_visibility="collapsed")
        if uploaded:
            st.image(Image.open(uploaded), use_container_width=True)
        go = st.button("🔍 Extract Text", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">📄 Extracted Text</div>', unsafe_allow_html=True)

        if go and uploaded:
            with st.spinner("🔍 Running Azure OCR…"):
                extracted = run_ocr(uploaded.read())
            if extracted:
                st.success(f"✅ Done — {len(extracted)} characters, {len(extracted.split())} words")
                st.markdown(f'<div class="result-box">{extracted}</div>', unsafe_allow_html=True)
                st.download_button("⬇️  Download as .txt", extracted,
                                   file_name="extracted_text.txt", mime="text/plain",
                                   use_container_width=True)
            else:
                st.error("❌ No text detected.")
        else:
            st.markdown('<div class="result-box" style="color:var(--muted)">Upload an image and click Extract…</div>',
                        unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  MODE: TEXT → SPEECH  (TTS Only)
# ─────────────────────────────────────────────
elif mode == "🔊 Text → Speech":
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">✍️ Enter Text</div>', unsafe_allow_html=True)
        user_text = st.text_area("Text input", height=220,
                                  placeholder="Paste or type any text here…",
                                  label_visibility="collapsed")
        if user_text:
            st.markdown(f'<div class="stat-row"><div class="stat-chip">🔤 {len(user_text.split())} words</div><div class="stat-chip">📝 {len(user_text)} chars</div></div>',
                        unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="panel">', unsafe_allow_html=True)
        voice_name, voice_label = voice_selector()
        st.markdown('</div>', unsafe_allow_html=True)

        go = st.button("🔊 Speak Text", use_container_width=True)

    with col2:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">🔊 Audio Output</div>', unsafe_allow_html=True)

        if go and user_text.strip():
            with st.spinner(f"🎙️ {voice_label} is speaking…"):
                ok, path = run_tts(user_text.strip(), voice_name)
            if ok:
                st.success(f"✅ Synthesised with {voice_label}")
                audio_player(path)
            else:
                st.error("❌ TTS failed. Check your Azure Speech credentials.")
        elif go:
            st.warning("⚠️ Please enter some text first.")
        else:
            st.markdown('<p style="color:var(--muted); font-size:0.85rem">Audio will appear after processing…</p>',
                        unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div class="footer">
  VoiceVision &nbsp;·&nbsp; Developed by <span>Shivam Dave</span> &nbsp;·&nbsp; Powered by Azure Cognitive Services
</div>
""", unsafe_allow_html=True)
