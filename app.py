import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import sqlite3
import base64
import random
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
  --bg: #f6f4f0;
  --card-border: rgba(255,255,255,0.14);
  --card-border-hover: rgba(255,255,255,0.28);
  --text: #f6f4f0;
  --text-dim: #cdc7bd;
  --text-dimmer: #8f887c;
  /* the dark-glass cards (--text/--text-dim/--text-dimmer above) keep their
     own light-on-dark contrast unchanged; these two are only for the
     handful of headline elements that sit directly on the page background,
     which flipped from near-black to white */
  --text-onbg: #1c1a17;
  --text-onbg-dim: #55504a;
  --orange-a: #ff5a1f;
  --orange-b: #ff9a52;
  /* a richer, more varied palette for the stat cards — refined gradients
     instead of a single accent colour, inspired by the fintech dashboard
     reference (deep magenta/pink, indigo/blue, violet) */
  --pink-a: #7a1f5c; --pink-b: #ff3d7f;
  --blue-a: #14224f; --blue-b: #3d7fff;
  --violet-a: #2a1a4a; --violet-b: #9d6fff;
  --glass-black: rgba(8,8,8,0.44);
  --glass-white: rgba(255,255,255,0.16);
  --glass-dark: rgba(20,18,16,0.40);
  --radius: 26px;
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

/* the scramble-reveal trigger is a logic-only iframe (no visuals of its
   own) — collapse its slot completely so it never takes up page space */
div[data-testid="stElementContainer"]:has(iframe[srcdoc*="SCRAMBLE_TRIGGER_MARKER"]){
  position: fixed !important; width:0 !important; height:0 !important;
  overflow: hidden !important; opacity:0; pointer-events:none;
}
/* ---------- BACKGROUND: generated plexus network (no external asset —
   drawn as inline SVG so there's no separate file that can go missing
   from a push; see _generate_plexus_svg()) ---------- */
.bg-video-wrap{ position: fixed; inset: 0; z-index: 0; overflow: hidden; background: var(--bg); }
.bg-plexus-wrap{ position:absolute; inset:0; }
.bg-plexus{ width:100%; height:100%; display:block; animation: plexusDrift 34s ease-in-out infinite; transform-origin: 50% 50%; }
@keyframes plexusDrift{
  0%   { transform: scale(1) rotate(0deg); }
  50%  { transform: scale(1.035) rotate(0.4deg); }
  100% { transform: scale(1) rotate(0deg); }
}
/* every node drifts on its own small orbit (radius/speed/offset randomized
   per-element via inline custom properties — see _generate_plexus_svg) so
   the network actually feels alive, not just a slowly-breathing photo */
.plexus-dot{
  animation: plexusFloat var(--dur, 9s) ease-in-out infinite;
  animation-delay: var(--delay, 0s);
  transform-box: fill-box; transform-origin: center;
}
@keyframes plexusFloat{
  0%, 100% { transform: translate(0, 0); }
  50%      { transform: translate(var(--dx, 5px), var(--dy, 5px)); }
}
.plexus-line{
  animation: plexusPulse var(--ldur, 6s) ease-in-out infinite;
  animation-delay: var(--ldelay, 0s);
}
@keyframes plexusPulse{
  0%, 100% { opacity: 0.45; }
  50%      { opacity: 1; }
}
@media (prefers-reduced-motion: reduce){
  .bg-plexus, .plexus-dot, .plexus-line{ animation: none !important; }
}
.bg-tint{
  position:absolute; inset:0;
  background: radial-gradient(circle at 22% 10%, rgba(255,154,82,0.10), transparent 46%);
  opacity: 0.9;
}
.bg-scrim{
  position:absolute; inset:0;
  background:
    radial-gradient(circle at 18% 8%, rgba(255,255,255,0.5), transparent 42%),
    linear-gradient(180deg, rgba(246,244,240,0) 0%, rgba(246,244,240,0.55) 55%, rgba(246,244,240,0.88) 100%);
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
  font-size: clamp(1.9rem, 3.4vw, 2.6rem); font-weight: 800; color: var(--text-onbg); margin:0;
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
  border-radius: var(--radius); padding: 22px 22px 20px;
  border: 1px solid var(--card-border);
  position: relative; overflow:hidden; min-height: 134px;
  backdrop-filter: blur(var(--blur)) saturate(160%); -webkit-backdrop-filter: blur(var(--blur)) saturate(160%);
  box-shadow: 0 1px 0 rgba(255,255,255,0.08) inset, 0 14px 30px rgba(0,0,0,0.22);
  /* micro-interaction: everything touchable acknowledges the touch —
     slightly slower/smoother than the app-wide default for a heavier,
     more premium feel on these anchor cards */
  transition: transform 0.32s var(--ease), box-shadow 0.32s var(--ease), border-color 0.32s var(--ease);
}
.stat-card:hover{
  transform: translateY(-6px) scale(1.01);
  border-color: var(--card-border-hover);
  box-shadow: 0 1px 0 rgba(255,255,255,0.10) inset, 0 24px 48px rgba(0,0,0,0.36);
}
.stat-card .label{ font-size: 0.74rem; color: rgba(255,255,255,0.8); font-weight:600; letter-spacing:0.02em; }
.stat-card .value{
  font-size: 1.95rem; font-weight: 800; color: #fff; margin-top: 11px;
  font-family:'JetBrains Mono', monospace; letter-spacing: 0.01em;
}
.stat-card .sub{ font-size: 0.72rem; color: rgba(255,255,255,0.7); margin-top:5px; }

/* four distinct, refined gradients instead of one repeated accent colour —
   each card reads as its own moment, tied together by the same shape
   language and motion (course rule: variety through colour, cohesion
   through consistent structure) */
.stat-glass-orange{ background: linear-gradient(160deg, rgba(255,122,61,0.70), rgba(255,90,31,0.60) 55%, rgba(122,31,92,0.48)); border-color: rgba(255,154,82,0.35); }
.stat-glass-white{ background: linear-gradient(160deg, rgba(61,127,255,0.70) 0%, rgba(20,34,79,0.70) 100%); border-color: rgba(120,160,255,0.32); }
.stat-glass-black{ background: linear-gradient(160deg, rgba(157,111,255,0.70) 0%, rgba(42,26,74,0.70) 100%); border-color: rgba(180,140,255,0.30); }
.stat-plain{ background: linear-gradient(160deg, rgba(40,36,32,0.58), rgba(10,9,8,0.62)); }
.stat-plain .value{ color: var(--text); }
.stat-plain .label{ color: var(--text-dim); }
.stat-plain .sub{ color: var(--text-dimmer); }

.dotgrid{
  position:absolute; right:16px; top:48px; width: 70px; height: 44px;
  background-image: radial-gradient(rgba(255,255,255,0.6) 1.4px, transparent 1.4px);
  background-size: 9px 9px; opacity:0.5;
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
  border-top: 1px solid rgba(0,0,0,0.10);
  text-align:center; color: var(--text-onbg-dim); font-size: 0.76rem; letter-spacing:0.02em;
}

/* ---------- CARD PANEL ---------- */
.panel{
  background: linear-gradient(175deg, rgba(30,26,38,0.48), var(--glass-dark) 60%);
  border: 1px solid var(--card-border); border-radius: var(--radius);
  padding: 28px 28px 24px; margin-top: 18px;
  backdrop-filter: blur(var(--blur)) saturate(160%); -webkit-backdrop-filter: blur(var(--blur)) saturate(160%);
  box-shadow: 0 1px 0 rgba(255,255,255,0.06) inset, 0 18px 36px rgba(0,0,0,0.24);
  transition: border-color 0.32s var(--ease), box-shadow 0.32s var(--ease);
}
.panel:hover{
  border-color: var(--card-border-hover);
  box-shadow: 0 1px 0 rgba(255,255,255,0.08) inset, 0 22px 44px rgba(0,0,0,0.30);
}
.panel h4{ margin:0 0 4px 0; color: var(--text); font-size:1.05rem; }
.panel p.hint{ color: var(--text-dimmer); font-size: 0.85rem; margin: 0 0 16px 0; }

/* ---------- ANSWER CARD ---------- */
/* This is the app's one signature moment (course rule: countless small
   micro-interactions, plus ONE memorable moment people notice) — the
   answer arrives with a fade+rise reveal and a single soft glow pulse.
   Palette now draws on the richer pink/blue/violet gradient family used
   on the stat cards, instead of orange alone, for a more cohesive,
   "designed" feel across the whole dashboard. */
.answer-card{
  position: relative;
  border-radius: var(--radius); padding: 24px 26px; margin-top: 18px;
  background: linear-gradient(155deg, rgba(255,90,31,0.26) 0%, rgba(157,111,255,0.18) 55%, rgba(10,10,10,0.54) 100%);
  border: 1px solid rgba(255,154,82,0.26);
  backdrop-filter: blur(var(--blur)) saturate(160%); -webkit-backdrop-filter: blur(var(--blur)) saturate(160%);
  box-shadow: 0 1px 0 rgba(255,255,255,0.08) inset, 0 20px 42px rgba(0,0,0,0.28);
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
  border: 1px solid var(--card-border); background: linear-gradient(165deg, rgba(28,24,34,0.50), var(--glass-dark) 65%);
  border-radius: 18px;
  padding: 17px 19px; margin-bottom: 12px;
  box-shadow: 0 1px 0 rgba(255,255,255,0.05) inset, 0 8px 20px rgba(0,0,0,0.18);
  transition: border-color 0.28s var(--ease), transform 0.28s var(--ease), box-shadow 0.28s var(--ease);
  backdrop-filter: blur(var(--blur)) saturate(150%); -webkit-backdrop-filter: blur(var(--blur)) saturate(150%);
}
.hist-card:hover{
  border-color: var(--card-border-hover);
  transform: translateY(-3px);
  box-shadow: 0 1px 0 rgba(255,255,255,0.08) inset, 0 16px 32px rgba(0,0,0,0.28);
}
.hist-top{ display:flex; align-items:center; justify-content:space-between; margin-bottom:6px; }
.hist-method{ font-size:0.72rem; font-weight:700; padding:3px 10px; border-radius:999px; }
.hist-method.voice{ background: linear-gradient(135deg, rgba(255,90,31,0.28), rgba(157,111,255,0.22)); color:#ffb27a; }
.hist-method.text{ background: linear-gradient(135deg, rgba(61,127,255,0.26), rgba(157,111,255,0.18)); color:#dbe6ff; }
.hist-time{ font-size:0.72rem; color: var(--text-dimmer); }
.hist-q{ color:#fff; font-weight:600; font-size:0.92rem; margin-bottom:4px; }
.hist-a{ color: var(--text-dim); font-size:0.85rem; line-height:1.5; }

.empty-state{ text-align:center; padding: 50px 20px; color: var(--text-onbg-dim); }

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
  position:relative; width:min(480px, 86vw); height:min(480px, 86vw);
  display:flex; align-items:center; justify-content:center;
}
/* A single light traces the ring and closes the full circle before the
   welcome slide appears — pure SVG/CSS, no video asset to go missing. */
.loader-ring-svg{ position:absolute; inset:0; width:100%; height:100%; transform: rotate(-90deg); }
.loader-ring-track{ fill:none; stroke: rgba(255,255,255,0.10); stroke-width: 2.5; }
.loader-ring-progress{
  fill:none; stroke: var(--orange-b); stroke-width: 2.5; stroke-linecap: round;
  stroke-dasharray: 346; stroke-dashoffset: 346;
  filter: drop-shadow(0 0 8px rgba(255,154,82,0.95)) drop-shadow(0 0 22px rgba(255,90,31,0.55));
  animation: ringComplete 1.9s cubic-bezier(0.65,0,0.35,1) forwards;
}
.loader-ring-head-wrap{
  position:absolute; inset:0;
  animation: ringHeadOrbit 1.9s cubic-bezier(0.65,0,0.35,1) forwards;
}
.loader-ring-head{
  /* distance from center = ring radius (55) / half the viewBox (70), so the
     dot traces exactly the same circle the SVG ring is drawn on, at any
     container size */
  position:absolute; top:10.71%; left:50%; width:16px; height:16px;
  transform: translate(-50%, -50%);
  border-radius:50%; background: radial-gradient(circle, #fff 0%, var(--orange-b) 65%, transparent 100%);
  box-shadow: 0 0 14px 6px rgba(255,154,82,0.9), 0 0 30px 12px rgba(255,90,31,0.45);
}
@keyframes ringComplete{ to{ stroke-dashoffset:0; } }
@keyframes ringHeadOrbit{ from{ transform: rotate(0deg); } to{ transform: rotate(360deg); } }
@media (prefers-reduced-motion: reduce){
  .loader-ring-progress{ animation: none; stroke-dashoffset:0; }
  .loader-ring-head-wrap{ animation: none; }
}
.loading-brand{
  position:relative; text-align:center; pointer-events:none;
  font-family: 'Jura', 'Inter', -apple-system, sans-serif;
  font-size: 0.95rem; font-weight: 700; color: var(--text-onbg); letter-spacing: 0.02em;
}
.loading-text{
  color: var(--text-onbg-dim); font-size: 0.85rem; letter-spacing: 0.03em;
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
  font-size: clamp(2.4rem, 6vw, 3.6rem); font-weight: 700; color: var(--text-onbg);
  letter-spacing: -0.01em; margin:0;
  white-space: nowrap;
}

/* ---------- SHUTTER REVEAL (jitter.video-style vertical-slice wipe) ---------- */
/* A row of solid bars sits over the title and peels away in a staggered,
   alternating-direction wipe — the same "blinds" reveal used in the
   reference showcase clip — before the scramble-decode kicks in underneath. */
.welcome-title-wrap{ position: relative; display: inline-block; }
.shutter-reveal{
  position: absolute; inset: -4px -2px; display: flex; z-index: 2; pointer-events: none;
  border-radius: 6px; overflow: hidden;
}
.shutter-reveal span{
  flex: 1 1 0; background: var(--bg);
  transform: scaleY(1);
  animation: shutterOpen 0.62s var(--ease) both;
}
.shutter-reveal span:nth-child(odd){ transform-origin: top; }
.shutter-reveal span:nth-child(even){ transform-origin: bottom; }
.shutter-reveal span:nth-child(1){ animation-delay: 0.05s; }
.shutter-reveal span:nth-child(2){ animation-delay: 0.11s; }
.shutter-reveal span:nth-child(3){ animation-delay: 0.17s; }
.shutter-reveal span:nth-child(4){ animation-delay: 0.23s; }
.shutter-reveal span:nth-child(5){ animation-delay: 0.29s; }
.shutter-reveal span:nth-child(6){ animation-delay: 0.35s; }
.shutter-reveal span:nth-child(7){ animation-delay: 0.41s; }
.shutter-reveal span:nth-child(8){ animation-delay: 0.47s; }
.shutter-reveal span:nth-child(9){ animation-delay: 0.53s; }
.shutter-reveal span:nth-child(10){ animation-delay: 0.59s; }
@keyframes shutterOpen{
  0%   { transform: scaleY(1); }
  100% { transform: scaleY(0); }
}
@media (prefers-reduced-motion: reduce){
  .shutter-reveal{ display:none; }
}

/* ---------- STAGE TRANSITION (full-screen shutter wipe, "Let's Begin" -> dashboard) ---------- */
/* Same vertical-slice language as the welcome title's shutter-reveal, scaled
   up to cover the whole viewport — plays once, then peels away to reveal
   the dashboard, which is itself already fading/rising in underneath via
   the .reveal classes. */
.stage-transition-overlay{
  position: fixed; inset: 0; z-index: 999999; display: flex; pointer-events: none;
}
.stage-transition-overlay span{
  flex: 1 1 0; background: var(--bg);
  transform: scaleY(1);
  animation: shutterOpen 0.85s var(--ease) both;
}
.stage-transition-overlay span:nth-child(odd){ transform-origin: top; }
.stage-transition-overlay span:nth-child(even){ transform-origin: bottom; }
.stage-transition-overlay span:nth-child(1){ animation-delay: 0.06s; }
.stage-transition-overlay span:nth-child(2){ animation-delay: 0.12s; }
.stage-transition-overlay span:nth-child(3){ animation-delay: 0.18s; }
.stage-transition-overlay span:nth-child(4){ animation-delay: 0.24s; }
.stage-transition-overlay span:nth-child(5){ animation-delay: 0.30s; }
.stage-transition-overlay span:nth-child(6){ animation-delay: 0.36s; }
.stage-transition-overlay span:nth-child(7){ animation-delay: 0.42s; }
.stage-transition-overlay span:nth-child(8){ animation-delay: 0.48s; }
.stage-transition-overlay span:nth-child(9){ animation-delay: 0.54s; }
.stage-transition-overlay span:nth-child(10){ animation-delay: 0.60s; }
.stage-transition-overlay span:nth-child(11){ animation-delay: 0.66s; }
.stage-transition-overlay span:nth-child(12){ animation-delay: 0.72s; }
.stage-transition-overlay span:nth-child(13){ animation-delay: 0.78s; }
.stage-transition-overlay span:nth-child(14){ animation-delay: 0.84s; }
@media (prefers-reduced-motion: reduce){
  .stage-transition-overlay{ display:none; }
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


@st.cache_resource(show_spinner=False)
def _generate_plexus_svg(seed=42, num_points=150, width=1600, height=900, connect_dist=165):
    # Procedurally drawn plexus-network pattern (matches the reference image
    # the user shared) — generated once as plain SVG markup and cached, so
    # there's no separate binary asset file that can go missing from a push.
    rng = random.Random(seed)
    pts = [(rng.uniform(0, width), rng.uniform(0, height)) for _ in range(num_points)]

    lines = []
    neighbor_count = [0] * num_points
    for i in range(num_points):
        for j in range(i + 1, num_points):
            x1, y1 = pts[i]
            x2, y2 = pts[j]
            d = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
            if d < connect_dist:
                op = max(0.04, 0.30 * (1 - d / connect_dist))
                # a subset of lines gently pulse in opacity so the mesh
                # visibly breathes, not just the dots sitting on top of it
                pulse_style = ""
                if rng.random() < 0.4:
                    ldur = rng.uniform(4.5, 9.0)
                    ldelay = -rng.uniform(0, ldur)  # negative delay = starts mid-cycle, desyncs everything
                    pulse_style = f' class="plexus-line" style="--ldur:{ldur:.2f}s; --ldelay:{ldelay:.2f}s;"'
                lines.append(
                    f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                    f'stroke="rgba(45,52,68,{op:.3f})" stroke-width="1"{pulse_style}/>'
                )
                if d < connect_dist * 0.62:
                    neighbor_count[i] += 1
                    neighbor_count[j] += 1

    # a handful of filled triangle facets for the faceted look in the reference
    triangles = []
    for i in range(num_points):
        if len(triangles) >= 16:
            break
        if neighbor_count[i] < 2:
            continue
        close = [
            j for j in range(num_points)
            if j != i and ((pts[i][0]-pts[j][0])**2 + (pts[i][1]-pts[j][1])**2) ** 0.5 < connect_dist * 0.62
        ]
        if len(close) >= 2 and rng.random() < 0.16:
            a, b = close[0], close[1]
            (x1, y1), (x2, y2), (x3, y3) = pts[i], pts[a], pts[b]
            triangles.append(
                f'<polygon points="{x1:.1f},{y1:.1f} {x2:.1f},{y2:.1f} {x3:.1f},{y3:.1f}" '
                f'fill="rgba(60,68,88,0.05)"/>'
            )

    dots = []
    for (x, y) in pts:
        r = rng.uniform(1.1, 2.4)
        op = rng.uniform(0.35, 0.75)
        # every dot floats on its own small, slow orbit — randomized radius,
        # direction, speed and phase so nothing moves in lockstep
        dx = rng.uniform(-7, 7)
        dy = rng.uniform(-7, 7)
        dur = rng.uniform(7, 15)
        delay = -rng.uniform(0, dur)
        dots.append(
            f'<circle class="plexus-dot" cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" '
            f'fill="rgba(35,40,54,{op:.2f})" '
            f'style="--dx:{dx:.1f}px; --dy:{dy:.1f}px; --dur:{dur:.2f}s; --delay:{delay:.2f}s;"/>'
        )

    return f"""<svg class="bg-plexus" viewBox="0 0 {width} {height}" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="plexusGlow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3.2" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <g filter="url(#plexusGlow)">
    {''.join(triangles)}
    {''.join(lines)}
    {''.join(dots)}
  </g>
</svg>"""


st.markdown("""
<div class="bg-video-wrap">
  <div class="bg-plexus-wrap"></div>
  <div class="bg-tint"></div>
  <div class="bg-scrim"></div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# LIVE PLEXUS NETWORK — canvas-driven, so the mesh actually moves and
# reshapes (nodes drift, connections form/break as distance changes,
# facets appear/disappear) instead of the earlier static SVG that only
# nudged each node a few px in place. Same persistent-iframe pattern as
# the scramble script above: injected once with no per-rerun nonce, so
# Streamlit/React reuses this exact iframe instead of tearing it down
# and restarting the animation on every interaction.
# ============================================================
_PLEXUS_CANVAS_HTML = """
<!-- PLEXUS_CANVAS_MARKER -->
<!DOCTYPE html>
<html><head></head><body>
<script>
(function(){
  try {
    var doc = window.parent.document;
    var win = window.parent;
    var reduceMotion = win.matchMedia && win.matchMedia('(prefers-reduced-motion: reduce)').matches;

    var wrap = doc.querySelector('.bg-plexus-wrap');
    if (!wrap) return;
    var canvas = wrap.querySelector('#plexus-canvas');
    if (!canvas) {
      canvas = doc.createElement('canvas');
      canvas.id = 'plexus-canvas';
      canvas.style.position = 'absolute';
      canvas.style.inset = '0';
      canvas.style.width = '100%';
      canvas.style.height = '100%';
      canvas.style.display = 'block';
      wrap.appendChild(canvas);
    }
    // already running from an earlier mount of this same iframe — don't start a second loop
    if (canvas.dataset.plexusRunning === '1') return;
    canvas.dataset.plexusRunning = '1';

    var ctx = canvas.getContext('2d');
    var dpr = win.devicePixelRatio || 1;
    var W = 0, H = 0;
    var NUM = 110;
    var CONNECT_FRAC = 0.155;   // connect radius as a fraction of the smaller viewport side
    var points = [];

    function resize(){
      W = wrap.clientWidth || win.innerWidth;
      H = wrap.clientHeight || win.innerHeight;
      canvas.width = Math.max(1, Math.floor(W * dpr));
      canvas.height = Math.max(1, Math.floor(H * dpr));
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    function initPoints(){
      points = [];
      for (var i = 0; i < NUM; i++){
        var ang = Math.random() * Math.PI * 2;
        var speed = 0.000035 + Math.random() * 0.00006; // fraction of viewport per ms — slow, deliberate
        points.push({
          x: Math.random(), y: Math.random(),
          vx: Math.cos(ang) * speed, vy: Math.sin(ang) * speed,
          r: 1.1 + Math.random() * 1.4
        });
      }
    }

    resize();
    initPoints();
    win.addEventListener('resize', resize);

    var last = null;
    function frame(ts){
      if (last === null) last = ts;
      var dt = Math.min(64, ts - last);
      last = ts;

      if (!reduceMotion){
        for (var i = 0; i < points.length; i++){
          var p = points[i];
          p.x += p.vx * dt;
          p.y += p.vy * dt;
          if (p.x <= 0 || p.x >= 1) p.vx *= -1;
          if (p.y <= 0 || p.y >= 1) p.vy *= -1;
          p.x = Math.min(1, Math.max(0, p.x));
          p.y = Math.min(1, Math.max(0, p.y));
        }
      }

      ctx.clearRect(0, 0, W, H);
      var connectDist = Math.min(W, H) * CONNECT_FRAC;
      var neighbors = points.map(function(){ return []; });

      // edges — also record close neighbors so we can facet a few triangles below
      ctx.lineWidth = 1;
      for (var i = 0; i < points.length; i++){
        for (var j = i + 1; j < points.length; j++){
          var a = points[i], b = points[j];
          var dx = (a.x - b.x) * W, dy = (a.y - b.y) * H;
          var d = Math.sqrt(dx * dx + dy * dy);
          if (d < connectDist){
            var op = Math.max(0.03, 0.30 * (1 - d / connectDist));
            ctx.strokeStyle = 'rgba(45,52,68,' + op.toFixed(3) + ')';
            ctx.beginPath();
            ctx.moveTo(a.x * W, a.y * H);
            ctx.lineTo(b.x * W, b.y * H);
            ctx.stroke();
            if (d < connectDist * 0.62){
              neighbors[i].push(j);
              neighbors[j].push(i);
            }
          }
        }
      }

      // a handful of filled facets — reshape continuously as the mesh drifts,
      // this is the "3D object" reading rather than a flat dot-and-line web
      var triCount = 0;
      for (var i = 0; i < points.length && triCount < 16; i++){
        if (neighbors[i].length < 2) continue;
        var a = neighbors[i][0], b = neighbors[i][1];
        var p0 = points[i], p1 = points[a], p2 = points[b];
        ctx.fillStyle = 'rgba(60,68,88,0.045)';
        ctx.beginPath();
        ctx.moveTo(p0.x * W, p0.y * H);
        ctx.lineTo(p1.x * W, p1.y * H);
        ctx.lineTo(p2.x * W, p2.y * H);
        ctx.closePath();
        ctx.fill();
        triCount++;
      }

      // dots
      for (var i = 0; i < points.length; i++){
        var p = points[i];
        ctx.fillStyle = 'rgba(35,40,54,0.6)';
        ctx.beginPath();
        ctx.arc(p.x * W, p.y * H, p.r, 0, Math.PI * 2);
        ctx.fill();
      }

      win.requestAnimationFrame(frame);
    }
    win.requestAnimationFrame(frame);
  } catch (e) {}
})();
</script>
</body></html>
"""

components.html(_PLEXUS_CANVAS_HTML, height=1, scrolling=False)


# ============================================================
# TEXT SCRAMBLE-REVEAL — the one signature motion, reused on every
# headline in the app (Reebok "All-Crew Shakeout Run" reference: text
# resolves out of scrambled characters).
#
# This is ONE persistent iframe, injected once, rather than one fired
# per rerun. Streamlit reruns the whole script on every interaction
# (a button click, the mic recorder polling, a tab switch), and each
# rerun used to spin up a brand-new iframe — which tore down any
# animation still in flight and left the text stuck mid-scramble
# forever (e.g. "Hello, FoVYPN" instead of "Hello, Folks!"). Because
# this srcdoc string never changes, Streamlit/React reuses the same
# iframe across reruns instead of recreating it, so a MutationObserver
# living inside it keeps watching the page for the whole session and
# every scramble is guaranteed to finish once started (elapsed-time
# based, not a step counter that can be cut off mid-count).
# ============================================================
_SCRAMBLE_SCRIPT_HTML = """
<!-- SCRAMBLE_TRIGGER_MARKER -->
<!DOCTYPE html>
<html><head></head><body>
<script>
(function(){
  try {
    var doc = window.parent.document;
    var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    var duration = 850;   // ms per element — noticeable, but doesn't drag
    var staggerMs = 120;  // each headline starts a beat after the last

    function animate(el){
      var target = el.textContent;
      var start = null;
      function step(ts){
        if (start === null) start = ts;
        var progress = Math.min(1, (ts - start) / duration);
        var revealed = Math.floor(progress * target.length);
        var out = '';
        for (var i = 0; i < target.length; i++){
          var ch = target[i];
          if (ch === ' ' || ch === '\\n' || ch === '\\t'){ out += ch; continue; }
          out += (i < revealed) ? ch : chars[Math.floor(Math.random() * chars.length)];
        }
        el.textContent = out;
        if (progress < 1){
          window.requestAnimationFrame(step);
        } else {
          el.textContent = target; // guaranteed correct final text, always
        }
      }
      window.requestAnimationFrame(step);
    }

    function scan(){
      var els = doc.querySelectorAll('.scramble:not([data-scrambled="1"])');
      els.forEach(function(el, idx){
        el.setAttribute('data-scrambled', '1'); // claim it before the delay so scan() can't double-queue it
        setTimeout(function(){ animate(el); }, idx * staggerMs);
      });
    }

    scan();
    var mo = new MutationObserver(function(){ scan(); });
    mo.observe(doc.body, { childList: true, subtree: true });
  } catch (e) {}
})();
</script>
</body></html>
"""

components.html(_SCRAMBLE_SCRIPT_HTML, height=1, scrolling=False)


# ============================================================
# STAGE FLOW — loading -> welcome -> dashboard
# ============================================================
if "app_stage" not in st.session_state:
    st.session_state.app_stage = "loading"

if st.session_state.app_stage == "loading":
    st.markdown("""
    <div class="loading-wrap">
      <div class="loader-badge">
        <svg class="loader-ring-svg" viewBox="0 0 140 140">
          <circle class="loader-ring-track" cx="70" cy="70" r="55"></circle>
          <circle class="loader-ring-progress" cx="70" cy="70" r="55"></circle>
        </svg>
        <div class="loader-ring-head-wrap"><div class="loader-ring-head"></div></div>
        <div class="loading-brand scramble">Getting ready to calculate....</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(2.1)
    st.session_state.app_stage = "welcome"
    st.rerun()

elif st.session_state.app_stage == "welcome":
    st.markdown("""
    <div class="welcome-wrap reveal">
      <div class="welcome-title-wrap">
        <div class="welcome-title scramble">Hello, Folks!</div>
        <div class="shutter-reveal">
          <span></span><span></span><span></span><span></span><span></span>
          <span></span><span></span><span></span><span></span><span></span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    with st.container(key="begin_wrap"):
        if st.button("Let's Begin", key="begin_btn"):
            st.session_state.app_stage = "dashboard"
            st.session_state.play_stage_transition = True
            st.rerun()

else:

    # ============================================================
    # STAGE TRANSITION — vertical-bar wipe (jitter.video reference) played
    # once, right when "Let's Begin" lands on the dashboard. The dashboard
    # content underneath already fades/rises in via the .reveal classes,
    # so the wipe just needs to cover it for a beat before peeling away.
    # ============================================================
    if st.session_state.get("play_stage_transition"):
        st.markdown("""
        <div class="stage-transition-overlay">
          <span></span><span></span><span></span><span></span><span></span><span></span><span></span>
          <span></span><span></span><span></span><span></span><span></span><span></span><span></span>
        </div>
        """, unsafe_allow_html=True)
        st.session_state.play_stage_transition = False

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
      <div class="hero-title scramble">AI Financial Voice Assistant</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="stat-row reveal reveal-2">
      <div class="stat-card stat-glass-orange">
        <div class="dotgrid"></div>
        <div class="label">Total Calculations</div>
        <div class="value scramble">{total_count}</div>
        <div class="sub">All-time questions asked</div>
      </div>
      <div class="stat-card stat-glass-white">
        <div class="label">Voice Queries</div>
        <div class="value scramble">{voice_count}</div>
        <div class="sub">Answered via mic input</div>
      </div>
      <div class="stat-card stat-glass-black">
        <div class="label">Text Queries</div>
        <div class="value scramble">{text_count}</div>
        <div class="sub">Answered via typed input</div>
      </div>
      <div class="stat-card stat-plain">
        <div class="label">Status</div>
        <div class="value scramble" style="font-size:1.2rem;">{"Ready" if (api_ready and model) else "Needs setup"}</div>
        <div class="sub">{(model_name.replace("models/", "") + " is live") if (api_ready and model) else "Check API key / model access"}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ============================================================
    # 8. MAIN INTERACTION — Voice / Text / History
    # ============================================================
    tab1, tab2, tab3 = st.tabs(["Voice", "Text", "History"])

    user_query = None
    input_method = None

    with tab1:
        st.markdown('<div class="panel"><h4 class="scramble">Speak your financial question</h4><p class="hint">Tap to record, then let the assistant do the math.</p>', unsafe_allow_html=True)
        voice_text = speech_to_text(start_prompt="Click to Speak", stop_prompt="Stop Recording", key='speech')
        if voice_text:
            st.info(f"Detected: {voice_text}")
            user_query = voice_text
            input_method = "Voice"
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="panel"><h4 class="scramble">Type your question</h4><p class="hint">e.g. "Calculate the ROI on $5000 over 2 years at 7%"</p>', unsafe_allow_html=True)
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
                  <div class="tag scramble">Answer</div>
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

    # Footer removed per request.
