import streamlit as st
import google.generativeai as genai
import sqlite3
from datetime import datetime
from streamlit_mic_recorder import speech_to_text

# ============================================================
# 1. PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="AI Financial Voice Assistant",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# 2. DESIGN SYSTEM — dark, glassy, gradient-card aesthetic
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500&display=swap');

:root{
  --bg: #08080c;
  --bg-soft: #0e0e15;
  --card: rgba(255,255,255,0.035);
  --card-border: rgba(255,255,255,0.08);
  --card-border-hover: rgba(255,255,255,0.16);
  --text: #f2f2f5;
  --text-dim: #9997a6;
  --text-dimmer: #6b6976;
  --pink-a: #ff2e63;
  --pink-b: #ff6a88;
  --blue-a: #4361ee;
  --blue-b: #4cc9f0;
  --violet-a: #7b2ff7;
  --violet-b: #b76cff;
  --green: #35d68e;
  --radius: 20px;
}

html, body, [class*="css"]  { font-family: 'Inter', -apple-system, sans-serif; }

.stApp {
  background:
    radial-gradient(circle at 15% 0%, rgba(123,47,247,0.16), transparent 40%),
    radial-gradient(circle at 85% 15%, rgba(255,46,99,0.10), transparent 35%),
    var(--bg);
}

#MainMenu, footer, header {visibility: hidden;}
.block-container { padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1100px; }

/* ---------- HERO ---------- */
.hero-wrap{
  display:flex; align-items:center; justify-content:space-between;
  flex-wrap: wrap; gap: 18px; margin-bottom: 28px;
}
.hero-title{
  font-size: 2.1rem; font-weight: 800; color: var(--text); margin:0;
  letter-spacing: -0.02em; display:flex; align-items:center; gap:12px;
}
.hero-badge-row{ display:flex; gap:10px; flex-wrap: wrap; }
.pill{
  padding: 7px 14px; border-radius: 999px; font-size: 0.78rem; font-weight: 600;
  background: var(--card); border: 1px solid var(--card-border); color: var(--text-dim);
  display:inline-flex; align-items:center; gap:6px; white-space: nowrap;
}
.pill .dot{ width:6px; height:6px; border-radius:50%; }

/* ---------- STAT CARDS ---------- */
.stat-row{ display:grid; grid-template-columns: repeat(4, 1fr); gap:14px; margin-bottom: 26px; }
@media (max-width: 900px){ .stat-row{ grid-template-columns: repeat(2, 1fr); } }

.stat-card{
  border-radius: var(--radius); padding: 20px 20px 18px;
  border: 1px solid var(--card-border);
  position: relative; overflow:hidden; min-height: 128px;
}
.stat-card .label{ font-size: 0.74rem; color: rgba(255,255,255,0.75); font-weight:600; letter-spacing:0.02em; }
.stat-card .value{ font-size: 1.85rem; font-weight: 800; color: #fff; margin-top: 10px; font-family:'JetBrains Mono', monospace; }
.stat-card .sub{ font-size: 0.72rem; color: rgba(255,255,255,0.65); margin-top:4px; }

.stat-gradient-1{ background: linear-gradient(135deg, var(--pink-a), var(--pink-b)); }
.stat-gradient-2{ background: linear-gradient(135deg, var(--blue-a), var(--blue-b)); }
.stat-gradient-3{ background: linear-gradient(135deg, var(--violet-a), var(--violet-b)); }
.stat-plain{ background: var(--card); }
.stat-plain .value{ color: var(--text); }
.stat-plain .label{ color: var(--text-dim); }
.stat-plain .sub{ color: var(--text-dimmer); }

.dotgrid{
  position:absolute; right:14px; top:44px; width: 70px; height: 44px;
  background-image: radial-gradient(rgba(255,255,255,0.55) 1.4px, transparent 1.4px);
  background-size: 9px 9px; opacity:0.55;
}

/* ---------- QUICK PROMPT CHIPS ---------- */
.section-label{ font-size:0.78rem; font-weight:700; color: var(--text-dim); text-transform:uppercase; letter-spacing:0.06em; margin: 4px 0 10px 2px;}
div[data-testid="stHorizontalBlock"] .stButton>button{
  background: var(--card); color: var(--text); border: 1px solid var(--card-border);
  border-radius: 999px; padding: 6px 16px; font-size: 0.82rem; font-weight: 600;
  transition: all .15s ease;
}
div[data-testid="stHorizontalBlock"] .stButton>button:hover{
  border-color: var(--card-border-hover); background: rgba(255,255,255,0.07); color:#fff;
}

/* ---------- TABS reskinned as pill nav ---------- */
.stTabs [data-baseweb="tab-list"]{ gap: 6px; background: var(--card); padding:6px; border-radius: 999px; border:1px solid var(--card-border); width: fit-content; }
.stTabs [data-baseweb="tab"]{ border-radius: 999px; padding: 8px 20px; color: var(--text-dim); font-weight:600; }
.stTabs [aria-selected="true"]{ background: #fff !important; color:#0a0a0f !important; }
.stTabs [data-baseweb="tab-highlight"]{ display:none; }
.stTabs [data-baseweb="tab-border"]{ display:none; }

/* ---------- CARD PANEL ---------- */
.panel{
  background: var(--card); border: 1px solid var(--card-border); border-radius: var(--radius);
  padding: 26px 26px 22px; margin-top: 18px;
}
.panel h4{ margin:0 0 4px 0; color: var(--text); font-size:1.05rem; }
.panel p.hint{ color: var(--text-dimmer); font-size: 0.85rem; margin: 0 0 16px 0; }

/* ---------- ANSWER CARD ---------- */
.answer-card{
  border-radius: var(--radius); padding: 22px 24px; margin-top: 18px;
  background: linear-gradient(160deg, rgba(255,46,99,0.16), rgba(123,47,247,0.10));
  border: 1px solid rgba(255,255,255,0.10);
}
.answer-card .tag{ font-size:0.72rem; font-weight:700; color: var(--pink-b); text-transform:uppercase; letter-spacing:0.05em; }
.answer-card p{ color: var(--text); font-size: 0.98rem; line-height:1.55; margin-top:8px; white-space: pre-wrap; }

/* ---------- HISTORY CARDS ---------- */
.hist-card{
  border: 1px solid var(--card-border); background: var(--card); border-radius: 16px;
  padding: 16px 18px; margin-bottom: 12px; transition: border-color .15s ease;
}
.hist-card:hover{ border-color: var(--card-border-hover); }
.hist-top{ display:flex; align-items:center; justify-content:space-between; margin-bottom:6px; }
.hist-method{ font-size:0.72rem; font-weight:700; padding:3px 10px; border-radius:999px; }
.hist-method.voice{ background: rgba(76,201,240,0.18); color:#4cc9f0; }
.hist-method.text{ background: rgba(255,106,136,0.18); color:#ff6a88; }
.hist-time{ font-size:0.72rem; color: var(--text-dimmer); }
.hist-q{ color:#fff; font-weight:600; font-size:0.92rem; margin-bottom:4px; }
.hist-a{ color: var(--text-dim); font-size:0.85rem; line-height:1.5; }

.empty-state{ text-align:center; padding: 50px 20px; color: var(--text-dimmer); }

/* inputs */
.stTextInput input{
  background: rgba(255,255,255,0.04) !important; border:1px solid var(--card-border) !important;
  border-radius: 12px !important; color: #fff !important; padding: 12px 14px !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 3. API CONFIG & MODEL DISCOVERY
# ============================================================
api_ready = False
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        api_ready = True
    else:
        st.error("API Key not found in secrets. Add GEMINI_API_KEY in your app's Settings > Secrets.")
except Exception as e:
    st.error(f"Configuration Error: {e}")


# Ordered by preference — newest/cheapest first. Google periodically retires
# older model ids (e.g. the original "gemini-pro" no longer serves generateContent),
# so instead of trusting list_models() metadata alone, we live-test each
# candidate with a tiny request and keep the first one that actually answers.
MODEL_PREFERENCES = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.0-flash",
    "gemini-2.0-flash-001",
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro",
    "gemini-pro",
]


@st.cache_resource(show_spinner=False)
def find_working_model():
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    except Exception:
        return None, None
    if not available:
        return None, None

    # Order candidates: known-good names first (if present in the account's
    # available list), then anything else the account exposes as a fallback.
    ordered = []
    for pref in MODEL_PREFERENCES:
        for name in available:
            if name.endswith(pref) and name not in ordered:
                ordered.append(name)
    for name in available:
        if name not in ordered:
            ordered.append(name)

    for name in ordered:
        try:
            candidate = genai.GenerativeModel(name)
            probe = candidate.generate_content("ping", generation_config={"max_output_tokens": 5})
            _ = probe.text  # raises if the model rejected the call
            return candidate, name
        except Exception:
            continue
    return None, None


model, model_name = find_working_model() if api_ready else (None, None)

# ============================================================
# 4. DATABASE
# ============================================================
def init_db():
    conn = sqlite3.connect('calc_history.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS history
                 (method TEXT, question TEXT, answer TEXT, timestamp TEXT)''')
    conn.commit()
    # migrate older DBs that were created before the timestamp column existed
    try:
        cur.execute("ALTER TABLE history ADD COLUMN timestamp TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass
    return conn


conn = init_db()
cursor = conn.cursor()

# ============================================================
# 5. STATE
# ============================================================
if "prefill" not in st.session_state:
    st.session_state.prefill = ""
if "voice_text_cache" not in st.session_state:
    st.session_state.voice_text_cache = None

# ============================================================
# 6. HERO
# ============================================================
total_count = cursor.execute("SELECT COUNT(*) FROM history").fetchone()[0]
voice_count = cursor.execute("SELECT COUNT(*) FROM history WHERE method='Voice'").fetchone()[0]
text_count = total_count - voice_count
last_row = cursor.execute("SELECT method, question, answer FROM history ORDER BY rowid DESC LIMIT 1").fetchone()

st.markdown(f"""
<div class="hero-wrap">
  <div class="hero-title">AI Financial Voice Assistant</div>
  <div class="hero-badge-row">
    <span class="pill"><span class="dot" style="background:{'#35d68e' if api_ready and model else '#ff2e63'}"></span>{"Model connected" if api_ready and model else "Model offline"}</span>
    <span class="pill">Voice · Text</span>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="stat-row">
  <div class="stat-card stat-gradient-1">
    <div class="dotgrid"></div>
    <div class="label">Total Calculations</div>
    <div class="value">{total_count}</div>
    <div class="sub">All-time questions asked</div>
  </div>
  <div class="stat-card stat-gradient-2">
    <div class="label">Voice Queries</div>
    <div class="value">{voice_count}</div>
    <div class="sub">Answered via mic input</div>
  </div>
  <div class="stat-card stat-gradient-3">
    <div class="label">Text Queries</div>
    <div class="value">{text_count}</div>
    <div class="sub">Answered via typed input</div>
  </div>
  <div class="stat-card stat-plain">
    <div class="label">Status</div>
    <div class="value" style="font-size:1.2rem;">{"Ready" if (api_ready and model) else "Needs setup"}</div>
    <div class="sub">{(model_name.replace("models/", "") + " is live") if (api_ready and model) else "Check API key / model access"}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 7. QUICK PROMPT CHIPS
# ============================================================
st.markdown('<div class="section-label">Quick Prompts</div>', unsafe_allow_html=True)
examples = [
    ("ROI", "Calculate the ROI on $5000 invested over 2 years at 7% annual return"),
    ("Loan EMI", "Calculate the monthly EMI for a $250,000 loan at 6.5% interest over 30 years"),
    ("Compound Interest", "What is the compound interest on $10,000 at 5% annually for 3 years?"),
    ("Budget Split", "Split a $6000 monthly income using the 50/30/20 budgeting rule"),
]
chip_cols = st.columns(len(examples))
for col, (label, prompt) in zip(chip_cols, examples):
    with col:
        if st.button(label, key=f"chip_{label}", use_container_width=True):
            st.session_state.prefill = prompt

# ============================================================
# 8. MAIN INTERACTION — Voice / Text / History
# ============================================================
tab1, tab2, tab3 = st.tabs(["Voice", "Text", "History"])

user_query = None
input_method = None

with tab1:
    st.markdown('<div class="panel"><h4>Speak your financial question</h4><p class="hint">Tap to record, then let the assistant do the math.</p>', unsafe_allow_html=True)
    voice_text = speech_to_text(start_prompt="Click to Speak", stop_prompt="Stop Recording", key='speech')
    if voice_text:
        st.info(f"Detected: {voice_text}")
        user_query = voice_text
        input_method = "Voice"
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="panel"><h4>Type your question</h4><p class="hint">e.g. "Calculate the ROI on $5000 over 2 years at 7%"</p>', unsafe_allow_html=True)
    typed_query = st.text_input(
        "question_input",
        value=st.session_state.prefill,
        placeholder="Ask a financial question…",
        label_visibility="collapsed",
    )
    if typed_query:
        user_query = typed_query
        input_method = "Text"
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    if total_count == 0:
        st.markdown("""
        <div class="empty-state">
          <div>No calculations yet — ask something in Voice or Text to see it here.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        rows = cursor.execute(
            "SELECT method, question, answer, timestamp FROM history ORDER BY rowid DESC LIMIT 20"
        ).fetchall()
        for method, question, answer, ts in rows:
            method_class = "voice" if method == "Voice" else "text"
            ts_display = ts if ts else ""
            answer_preview = (answer[:220] + "…") if answer and len(answer) > 220 else (answer or "")
            st.markdown(f"""
            <div class="hist-card">
              <div class="hist-top">
                <span class="hist-method {method_class}">{method}</span>
                <span class="hist-time">{ts_display}</span>
              </div>
              <div class="hist-q">{question}</div>
              <div class="hist-a">{answer_preview}</div>
            </div>
            """, unsafe_allow_html=True)

        csv_lines = ["method,question,answer,timestamp"]
        for method, question, answer, ts in rows:
            safe_q = (question or "").replace('"', "'")
            safe_a = (answer or "").replace('"', "'").replace("\n", " ")
            csv_lines.append(f'"{method}","{safe_q}","{safe_a}","{ts or ""}"')
        st.download_button(
            "Export history as CSV",
            data="\n".join(csv_lines),
            file_name="financial_assistant_history.csv",
            mime="text/csv",
            use_container_width=False,
        )

# ============================================================
# 9. EXECUTION LOGIC
# ============================================================
if user_query and model:
    with st.spinner("AI analyzing…"):
        try:
            response = model.generate_content(f"You are a financial assistant. Solve: {user_query}")
            answer = response.text

            st.markdown(f"""
            <div class="answer-card">
              <div class="tag">Answer</div>
              <p>{answer}</p>
            </div>
            """, unsafe_allow_html=True)

            cursor.execute(
                "INSERT INTO history (method, question, answer, timestamp) VALUES (?, ?, ?, ?)",
                (input_method, user_query, answer, datetime.now().strftime("%b %d, %Y · %H:%M")),
            )
            conn.commit()
            st.session_state.prefill = ""
        except Exception as e:
            st.error(f"AI Error: {e}")
elif user_query and not model:
    st.warning("The AI model isn't connected yet — check your GEMINI_API_KEY in Secrets.")
