import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import sqlite3
import base64
import time
from pathlib import Path
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
# 2. DESIGN SYSTEM — black / white / orange, animated glass finish
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500&family=Jura:wght@500;600;700&display=swap');

:root{
  --bg: #060606;
  --card-border: rgba(255,255,255,0.14);
  --card-border-hover: rgba(255,255,255,0.28);
  --text: #f6f4f0;
  --text-dim: #cdc7bd;
  --text-dimmer: #8f887c;
  --orange-a: #ff5a1f;
  --orange-b: #ff9a52;
  --glass-black: rgba(8,8,8,0.55);
  --glass-white: rgba(255,255,255,0.16);
  --glass-dark: rgba(20,18,16,0.46);
  --radius: 20px;
  --blur: 20px;
  /* ---- one motion language, reused everywhere (course rule: pick your
     durations/easing once, hold them everywhere — consistency is what
     reads as "one crafted thing" instead of scattered effects) ---- */
  --ease: cubic-bezier(0.16, 1, 0.3, 1);
  --dur: 0.8s;
  --dur-fast: 0.22s;
  /* ---- one spacing scale, reused everywhere ---- */
  --space-1: 8px; --space-2: 16px; --space-3: 24px; --space-4: 32px; --space-5: 48px; --space-6: 64px;
}

html, body, [class*="css"]  { font-family: 'Inter', -apple-system, sans-serif; }

/* ---------- MOTION LANGUAGE: fade + rise + stagger on entrance ---------- */
@keyframes fadeRise{
  from{ opacity:0; transform: translateY(28px); }
  to{ opacity:1; transform: translateY(0); }
}
@keyframes ringPulse{
  0%{ box-shadow: 0 0 0 0 rgba(255,90,31,0.38); }
  100%{ box-shadow: 0 0 0 22px rgba(255,90,31,0); }
}
.reveal{ animation: fadeRise var(--dur) var(--ease) both; }
.reveal-1{ animation-delay: 0.04s; }
.reveal-2{ animation-delay: 0.14s; }
.reveal-3{ animation-delay: 0.24s; }
.reveal-4{ animation-delay: 0.34s; }
.reveal-5{ animation-delay: 0.44s; }
@media (prefers-reduced-motion: reduce){
  .reveal, .reveal-1, .reveal-2, .reveal-3, .reveal-4, .reveal-5{
    animation: none !important; opacity:1 !important; transform:none !important;
  }
  .answer-card::after{ animation: none !important; }
}

.stApp { background: var(--bg); }

#MainMenu, footer, header {visibility: hidden;}
.block-container { padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1100px; position: relative; z-index: 1; }

/* ---------- ANIMATED 3D NETWORK BACKGROUND ---------- */
/* The canvas animation is rendered inside a components.html srcdoc iframe;
   this selector finds that specific iframe (by a marker in its srcdoc) and
   promotes it to a fixed, full-viewport, click-through background layer. */
div[data-testid="stElementContainer"]:has(iframe[srcdoc*="NETWORK_BG_MARKER"]){
  position: fixed !important; inset: 0 !important; width: 100vw !important; height: 100vh !important;
  z-index: 0; overflow: hidden; pointer-events: none;
}
div[data-testid="stElementContainer"]:has(iframe[srcdoc*="NETWORK_BG_MARKER"]) iframe{
  position: fixed !important; inset: 0 !important; width: 100vw !important; height: 100vh !important;
  border: none; pointer-events: none;
}
.bg-video-wrap{ position: fixed; inset: 0; z-index: 0; overflow: hidden; background: var(--bg); }
.bg-tint{
  position:absolute; inset:0;
  background: radial-gradient(circle at 22% 10%, rgba(70,140,210,0.16), transparent 46%);
  opacity: 0.9;
}
.bg-scrim{
  position:absolute; inset:0;
  background:
    radial-gradient(circle at 18% 8%, rgba(90,160,230,0.14), transparent 42%),
    linear-gradient(180deg, rgba(3,6,10,0.35) 0%, rgba(3,6,10,0.62) 55%, rgba(3,6,10,0.86) 100%);
}

/* ---------- GLASS BASE (mat frosted finish) ---------- */
.glass{
  backdrop-filter: blur(var(--blur)) saturate(150%);
  -webkit-backdrop-filter: blur(var(--blur)) saturate(150%);
}

/* ---------- HERO ---------- */
.hero-wrap{
  display:flex; align-items:center; justify-content:space-between;
  flex-wrap: wrap; gap: 18px; margin-bottom: 28px;
}
.hero-title{
  font-family: 'Jura', 'Inter', -apple-system, sans-serif;
  /* extreme size contrast vs. the small dim badges beside it — the single
     thing the eye should hit first on this screen */
  font-size: clamp(1.9rem, 3.4vw, 2.6rem); font-weight: 800; color: var(--text); margin:0;
  letter-spacing: -0.02em; line-height:1.05; display:flex; align-items:center; gap:12px;
}
.hero-badge-row{ display:flex; gap:10px; flex-wrap: wrap; opacity: 0.9; }
.pill{
  padding: 7px 14px; border-radius: 999px; font-size: 0.78rem; font-weight: 600;
  background: var(--glass-dark); border: 1px solid var(--card-border); color: var(--text-dim);
  display:inline-flex; align-items:center; gap:6px; white-space: nowrap;
  backdrop-filter: blur(14px) saturate(150%); -webkit-backdrop-filter: blur(14px) saturate(150%);
}
.pill .dot{ width:6px; height:6px; border-radius:50%; }

/* ---------- STAT CARDS ---------- */
.stat-row{ display:grid; grid-template-columns: repeat(4, 1fr); gap:14px; margin-bottom: 26px; }
@media (max-width: 900px){ .stat-row{ grid-template-columns: repeat(2, 1fr); } }

.stat-card{
  border-radius: var(--radius); padding: 20px 20px 18px;
  border: 1px solid var(--card-border);
  position: relative; overflow:hidden; min-height: 128px;
  backdrop-filter: blur(var(--blur)) saturate(150%); -webkit-backdrop-filter: blur(var(--blur)) saturate(150%);
  /* micro-interaction: everything touchable acknowledges the touch */
  transition: transform var(--dur-fast) var(--ease), box-shadow var(--dur-fast) var(--ease), border-color var(--dur-fast) var(--ease);
}
.stat-card:hover{
  transform: translateY(-4px);
  border-color: var(--card-border-hover);
  box-shadow: 0 18px 40px rgba(0,0,0,0.32);
}
.stat-card .label{ font-size: 0.74rem; color: rgba(255,255,255,0.78); font-weight:600; letter-spacing:0.02em; }
.stat-card .value{ font-size: 1.85rem; font-weight: 800; color: #fff; margin-top: 10px; font-family:'JetBrains Mono', monospace; }
.stat-card .sub{ font-size: 0.72rem; color: rgba(255,255,255,0.68); margin-top:4px; }

.stat-glass-orange{ background: linear-gradient(135deg, rgba(255,90,31,0.80), rgba(255,154,82,0.72)); border-color: rgba(255,154,82,0.35); }
.stat-glass-white{ background: linear-gradient(135deg, rgba(255,255,255,0.22), rgba(255,255,255,0.08)); }
.stat-glass-black{ background: var(--glass-black); }
.stat-plain{ background: var(--glass-black); }
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
/* one button feel, reused everywhere — every clickable element in the app
   uses this same transition timing so hovers read as one crafted system */
.stButton>button, .stDownloadButton>button{
  transition: transform var(--dur-fast) var(--ease), box-shadow var(--dur-fast) var(--ease),
              background var(--dur-fast) var(--ease), border-color var(--dur-fast) var(--ease),
              color var(--dur-fast) var(--ease) !important;
}
.stButton>button:hover, .stDownloadButton>button:hover{ transform: translateY(-2px); }
.stButton>button:active, .stDownloadButton>button:active{ transform: translateY(0); }

div[data-testid="stHorizontalBlock"] .stButton>button{
  background: var(--glass-dark); color: var(--text); border: 1px solid var(--card-border);
  border-radius: 999px; padding: 6px 16px; font-size: 0.82rem; font-weight: 600;
  backdrop-filter: blur(14px) saturate(150%); -webkit-backdrop-filter: blur(14px) saturate(150%);
}
div[data-testid="stHorizontalBlock"] .stButton>button:hover{
  border-color: var(--orange-a); background: rgba(255,90,31,0.16); color:#fff;
  box-shadow: 0 10px 24px rgba(255,90,31,0.18);
}

/* generic buttons (e.g. CSV export) */
.stDownloadButton>button{
  background: var(--glass-dark); color: var(--text); border: 1px solid var(--card-border);
  border-radius: 999px; font-weight:600;
  backdrop-filter: blur(14px) saturate(150%); -webkit-backdrop-filter: blur(14px) saturate(150%);
}
.stDownloadButton>button:hover{ border-color: var(--orange-a); color:#fff; box-shadow: 0 10px 24px rgba(255,90,31,0.18); }

/* ---------- TABS reskinned as pill nav ---------- */
.stTabs [data-baseweb="tab-list"]{
  gap: 6px; background: var(--glass-dark); padding:6px; border-radius: 999px;
  border:1px solid var(--card-border); width: fit-content;
  backdrop-filter: blur(16px) saturate(150%); -webkit-backdrop-filter: blur(16px) saturate(150%);
}
.stTabs [data-baseweb="tab"]{
  border-radius: 999px; padding: 8px 20px; color: var(--text-dim); font-weight:600;
  transition: color var(--dur-fast) var(--ease), background var(--dur-fast) var(--ease);
}
.stTabs [data-baseweb="tab"]:hover{ color: #fff; }
.stTabs [aria-selected="true"]{ background: #fff !important; color:#0a0a0a !important; }
.stTabs [data-baseweb="tab-highlight"]{ display:none; }
.stTabs [data-baseweb="tab-border"]{ display:none; }

/* ---------- FOOTER ---------- */
/* the closing beat of the story (course: identity -> proof -> experience ->
   conversion) — quiet, restrained, single line, never competing for attention */
.app-footer{
  margin-top: var(--space-6); padding-top: var(--space-3);
  border-top: 1px solid var(--card-border);
  text-align:center; color: var(--text-dimmer); font-size: 0.76rem; letter-spacing:0.02em;
}

/* ---------- CARD PANEL ---------- */
.panel{
  background: var(--glass-dark); border: 1px solid var(--card-border); border-radius: var(--radius);
  padding: 26px 26px 22px; margin-top: 18px;
  backdrop-filter: blur(var(--blur)) saturate(150%); -webkit-backdrop-filter: blur(var(--blur)) saturate(150%);
}
.panel h4{ margin:0 0 4px 0; color: var(--text); font-size:1.05rem; }
.panel p.hint{ color: var(--text-dimmer); font-size: 0.85rem; margin: 0 0 16px 0; }

/* ---------- ANSWER CARD ---------- */
/* This is the app's one signature moment (course rule: countless small
   micro-interactions, plus ONE memorable moment people notice) — the
   answer arrives with a fade+rise reveal and a single soft glow pulse. */
.answer-card{
  position: relative;
  border-radius: var(--radius); padding: 22px 24px; margin-top: 18px;
  background: linear-gradient(160deg, rgba(255,90,31,0.22), rgba(10,10,10,0.55));
  border: 1px solid rgba(255,154,82,0.28);
  backdrop-filter: blur(var(--blur)) saturate(150%); -webkit-backdrop-filter: blur(var(--blur)) saturate(150%);
  animation: fadeRise var(--dur) var(--ease) both;
}
.answer-card::after{
  content:''; position:absolute; inset:0; border-radius: var(--radius);
  pointer-events:none; animation: ringPulse 1.1s var(--ease) 1;
}
.answer-card .tag{ font-size:0.72rem; font-weight:700; color: var(--orange-b); text-transform:uppercase; letter-spacing:0.05em; }
.answer-card p{ color: var(--text); font-size: 0.98rem; line-height:1.55; margin-top:8px; white-space: pre-wrap; }

/* ---------- HISTORY CARDS ---------- */
.hist-card{
  border: 1px solid var(--card-border); background: var(--glass-dark); border-radius: 16px;
  padding: 16px 18px; margin-bottom: 12px;
  transition: border-color var(--dur-fast) var(--ease), transform var(--dur-fast) var(--ease);
  backdrop-filter: blur(var(--blur)) saturate(150%); -webkit-backdrop-filter: blur(var(--blur)) saturate(150%);
}
.hist-card:hover{ border-color: var(--card-border-hover); transform: translateY(-2px); }
.hist-top{ display:flex; align-items:center; justify-content:space-between; margin-bottom:6px; }
.hist-method{ font-size:0.72rem; font-weight:700; padding:3px 10px; border-radius:999px; }
.hist-method.voice{ background: rgba(255,90,31,0.20); color:#ff9a52; }
.hist-method.text{ background: rgba(255,255,255,0.14); color:#fff; }
.hist-time{ font-size:0.72rem; color: var(--text-dimmer); }
.hist-q{ color:#fff; font-weight:600; font-size:0.92rem; margin-bottom:4px; }
.hist-a{ color: var(--text-dim); font-size:0.85rem; line-height:1.5; }

.empty-state{ text-align:center; padding: 50px 20px; color: var(--text-dimmer); }

/* inputs */
.stTextInput input{
  background: rgba(255,255,255,0.06) !important; border:1px solid var(--card-border) !important;
  border-radius: 12px !important; color: #fff !important; padding: 12px 14px !important;
  backdrop-filter: blur(14px) saturate(150%);
}

/* ---------- LOADING SCREEN ---------- */
.loading-wrap{
  position:relative; z-index:1; min-height: 82vh;
  display:flex; flex-direction:column; align-items:center; justify-content:center; gap: 24px;
}
.loader-badge{
  position:relative; width:min(360px, 70vw); height:min(360px, 70vw);
}
.loader-video{
  width:100%; height:100%; border-radius:50%;
  overflow:hidden; object-fit:cover; display:block;
  box-shadow: 0 0 0 1px rgba(255,255,255,0.10), 0 14px 46px rgba(255,90,31,0.30);
  /* Mask out the animated counter number in the middle of the clip,
     leaving only the decorative dotted ring visible around the edge. */
  -webkit-mask-image: radial-gradient(circle, transparent 0%, transparent 58%, #000 62%, #000 100%);
  mask-image: radial-gradient(circle, transparent 0%, transparent 58%, #000 62%, #000 100%);
}
.loading-brand{
  position:absolute; left:50%; top:50%; transform:translate(-50%, -50%);
  width:62%; text-align:center; pointer-events:none;
  font-family: 'Jura', 'Inter', -apple-system, sans-serif;
  font-size: 0.95rem; font-weight: 700; color: var(--text); letter-spacing: 0.02em;
}
.loading-text{
  color: var(--text-dimmer); font-size: 0.85rem; letter-spacing: 0.03em;
}
.loading-dots span{ animation: dot-pulse 1.2s infinite; opacity:0; }
.loading-dots span:nth-child(2){ animation-delay: 0.2s; }
.loading-dots span:nth-child(3){ animation-delay: 0.4s; }
@keyframes dot-pulse{ 0%{opacity:0;} 30%{opacity:1;} 60%{opacity:0;} 100%{opacity:0;} }

/* ---------- WELCOME SCREEN ---------- */
/* Streamlit's own top-level vertical block stretches to fill the available
   height even though it holds little content, which meant centering IT
   (via block-container flex) did not visually center the title/button
   inside it — they stayed pinned near its top. Fixed-positioning each
   piece directly relative to the viewport sidesteps that entirely and
   guarantees true centering regardless of Streamlit's own box sizing.
   Verified live in the browser before committing to these offsets. */
.block-container [data-testid="stElementContainer"]:has(.welcome-title){
  position: fixed !important;
  top: calc(50% - 55px) !important;
  left: 50% !important;
  transform: translate(-50%, -50%) !important;
  width: auto !important;
  z-index: 1;
}
.welcome-wrap{
  position:relative; z-index:1;
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  text-align:center; gap: 20px; padding: 0 20px;
}
.welcome-title{
  font-family: 'Jura', 'Inter', -apple-system, sans-serif;
  font-size: clamp(2.4rem, 6vw, 3.6rem); font-weight: 700; color: var(--text);
  letter-spacing: -0.01em; margin:0;
  white-space: nowrap;
}
.st-key-begin_wrap{
  position: fixed !important;
  top: calc(50% + 55px) !important;
  left: 50% !important;
  transform: translate(-50%, -50%) !important;
  width: auto !important;
  z-index: 1;
  display:flex !important; flex-direction:column !important; align-items:center !important;
  /* opacity-only entrance — this element's transform is already spoken for
     by the fixed-centering translate(-50%,-50%) above, so animating
     transform here would fight it; fadeIn keeps the same motion timing
     without touching that property */
  animation: fadeIn var(--dur) var(--ease) 0.15s both;
}
@keyframes fadeIn{ from{ opacity:0; } to{ opacity:1; } }
.st-key-begin_wrap .stButton>button{
  background: linear-gradient(135deg, var(--orange-a), var(--orange-b)) !important;
  color:#fff !important; border:none !important; border-radius: 999px !important;
  padding: 14px 46px !important; font-size: 1rem !important; font-weight:700 !important;
  letter-spacing: 0.02em; box-shadow: 0 10px 34px rgba(255,90,31,0.32);
  transition: transform .15s ease, box-shadow .15s ease;
}
.st-key-begin_wrap .stButton>button:hover{
  transform: translateY(-2px); box-shadow: 0 14px 40px rgba(255,90,31,0.42);
}
</style>
""", unsafe_allow_html=True)


_NETWORK_BG_HTML = """
<!-- NETWORK_BG_MARKER -->
<!DOCTYPE html>
<html>
<head>
<style>
  html, body { margin:0; padding:0; overflow:hidden; background:#04070c; height:100%; }
  canvas { display:block; }
</style>
</head>
<body>
<canvas id="netbg"></canvas>
<script>
(function(){
  var canvas = document.getElementById('netbg');
  var ctx = canvas.getContext('2d');
  var W, H, DPR;

  function resize(){
    DPR = Math.min(window.devicePixelRatio || 1, 2);
    W = window.innerWidth; H = window.innerHeight;
    canvas.width = W * DPR; canvas.height = H * DPR;
    canvas.style.width = W + 'px'; canvas.style.height = H + 'px';
    ctx.setTransform(DPR,0,0,DPR,0,0);
  }
  window.addEventListener('resize', resize);
  resize();

  var NUM = 170;
  var particles = [];
  for (var i = 0; i < NUM; i++) {
    particles.push({
      x: (Math.random()-0.5)*2,
      y: (Math.random()-0.5)*2,
      z: (Math.random()-0.5)*2,
      vx: (Math.random()-0.5)*0.00050,
      vy: (Math.random()-0.5)*0.00050,
      vz: (Math.random()-0.5)*0.00050,
      flash: 0,
      flashTarget: 0
    });
  }

  var angle = 0;
  function project(p){
    var cosA = Math.cos(angle), sinA = Math.sin(angle);
    var x = p.x*cosA - p.z*sinA;
    var z = p.x*sinA + p.z*cosA;
    var y = p.y;
    /* depth (z) only modulates apparent size/brightness — position spreads
       across the FULL frame regardless of depth, so nodes fill edge to edge
       like a real plexus network rather than clustering toward the center. */
    var depthScale = 0.55 + (z+1)/2*0.85;
    return {
      sx: W/2 + x*W*0.5,
      sy: H/2 + y*H*0.5,
      scale: depthScale,
      z: z
    };
  }

  function tick(){
    ctx.clearRect(0, 0, W, H);
    angle += 0.0011;

    for (var i = 0; i < NUM; i++) {
      var p = particles[i];
      p.x += p.vx; p.y += p.vy; p.z += p.vz;
      if (p.x > 1 || p.x < -1) p.vx *= -1;
      if (p.y > 1 || p.y < -1) p.vy *= -1;
      if (p.z > 1 || p.z < -1) p.vz *= -1;
      if (p.flash <= 0.02 && Math.random() < 0.0012) p.flashTarget = 1;
      if (p.flashTarget > 0) {
        p.flash += (p.flashTarget - p.flash) * 0.15;
        if (p.flash > 0.92) p.flashTarget = 0;
      } else if (p.flash > 0) {
        p.flash *= 0.90;
        if (p.flash < 0.02) p.flash = 0;
      }
    }

    var proj = new Array(NUM);
    for (var i = 0; i < NUM; i++) proj[i] = project(particles[i]);

    for (var i = 0; i < NUM; i++) {
      for (var j = i+1; j < NUM; j++) {
        var a = proj[i], b = proj[j];
        var dx = a.sx-b.sx, dy = a.sy-b.sy;
        var dist = Math.sqrt(dx*dx+dy*dy);
        var maxDist = Math.min(W,H) * 0.19;
        if (dist < maxDist) {
          var depth = (a.scale+b.scale)/2;
          var op = (1 - dist/maxDist) * 0.5 * depth;
          var flashBoost = Math.max(particles[i].flash, particles[j].flash) * 0.5;
          ctx.strokeStyle = 'rgba(140,195,255,' + Math.min(1, op+flashBoost) + ')';
          ctx.lineWidth = 0.7 * depth;
          ctx.beginPath();
          ctx.moveTo(a.sx, a.sy);
          ctx.lineTo(b.sx, b.sy);
          ctx.stroke();
        }
      }
    }

    for (var i = 0; i < NUM; i++) {
      var p = particles[i], sp = proj[i];
      var depth = sp.scale;
      var r = Math.max(0.7, 1.4*depth + p.flash*2.6);
      var baseOp = Math.min(1, 0.5*depth + p.flash*0.6);

      if (p.flash > 0.04) {
        var glowR = 16 * depth * (0.4 + p.flash);
        var grad = ctx.createRadialGradient(sp.sx, sp.sy, 0, sp.sx, sp.sy, glowR);
        grad.addColorStop(0, 'rgba(190,230,255,' + (0.75*p.flash) + ')');
        grad.addColorStop(1, 'rgba(190,230,255,0)');
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(sp.sx, sp.sy, glowR, 0, Math.PI*2);
        ctx.fill();
      }

      ctx.fillStyle = 'rgba(205,230,255,' + baseOp + ')';
      ctx.beginPath();
      ctx.arc(sp.sx, sp.sy, r, 0, Math.PI*2);
      ctx.fill();
    }

    requestAnimationFrame(tick);
  }
  tick();
})();
</script>
</body>
</html>
"""

components.html(_NETWORK_BG_HTML, height=1, scrolling=False)
st.markdown("""
<div class="bg-video-wrap">
  <div class="bg-tint"></div>
  <div class="bg-scrim"></div>
</div>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def _load_loader_video_b64():
    video_path = Path(__file__).resolve().parent / "assets" / "loader-counter.mp4"
    if video_path.exists():
        return base64.b64encode(video_path.read_bytes()).decode("utf-8")
    return ""


# ============================================================
# STAGE FLOW — loading -> welcome -> dashboard
# ============================================================
if "app_stage" not in st.session_state:
    st.session_state.app_stage = "loading"

if st.session_state.app_stage == "loading":
    st.markdown(f"""
    <div class="loading-wrap">
      <div class="loader-badge">
        <video class="loader-video" autoplay muted loop playsinline>
          <source src="data:video/mp4;base64,{_load_loader_video_b64()}" type="video/mp4">
        </video>
        <div class="loading-brand">Getting ready to calculate....</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(1.6)
    st.session_state.app_stage = "welcome"
    st.rerun()

elif st.session_state.app_stage == "welcome":
    st.markdown("""
    <div class="welcome-wrap reveal">
      <div class="welcome-title">Hello, Folks!</div>
    </div>
    """, unsafe_allow_html=True)
    with st.container(key="begin_wrap"):
        if st.button("Let's Begin", key="begin_btn"):
            st.session_state.app_stage = "dashboard"
            st.rerun()

else:

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
    <div class="hero-wrap reveal reveal-1">
      <div class="hero-title">AI Financial Voice Assistant</div>
      <div class="hero-badge-row">
        <span class="pill"><span class="dot" style="background:{'#ff5a1f' if api_ready and model else 'rgba(255,255,255,0.3)'}"></span>{"Model connected" if api_ready and model else "Model offline"}</span>
        <span class="pill">Voice · Text</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="stat-row reveal reveal-2">
      <div class="stat-card stat-glass-orange">
        <div class="dotgrid"></div>
        <div class="label">Total Calculations</div>
        <div class="value">{total_count}</div>
        <div class="sub">All-time questions asked</div>
      </div>
      <div class="stat-card stat-glass-white">
        <div class="label">Voice Queries</div>
        <div class="value">{voice_count}</div>
        <div class="sub">Answered via mic input</div>
      </div>
      <div class="stat-card stat-glass-black">
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
    st.markdown('<div class="section-label reveal reveal-3">Quick Prompts</div>', unsafe_allow_html=True)
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

    # ============================================================
    # 10. FOOTER — the closing beat of the story
    # ============================================================
    st.markdown(
        '<div class="app-footer reveal reveal-5">AI Financial Voice Assistant · Powered by Gemini</div>',
        unsafe_allow_html=True,
    )
