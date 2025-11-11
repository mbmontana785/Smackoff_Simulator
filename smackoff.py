# smackoff.py
import time
import re
import random
import numpy as np
import pandas as pd
import streamlit as st
from typing import Optional

# ---------- Page setup ----------
st.set_page_config(page_title="Smackoff Simulator", page_icon="📞", layout="wide")

# Tighten spacing & widen content
st.markdown("""
<style>
div.stButton > button { margin-bottom: 4px; }
.block-container { max-width: 1400px; }
.header-nowrap { white-space: nowrap; }
</style>
""", unsafe_allow_html=True)

# Title (centered)
st.markdown(
    "<h1 style='text-align:center;'>📞 Mike in Jersey's Smackoff Simulator</h1>",
    unsafe_allow_html=True
)

# ---------- Input odds (American style, all positive here) ----------
smackoff_odds_raw = {
    'Brad_in_Corona': 500,
    'Mark_in_Boston': 600,
    'Mark_in_Hollywood': 700,
    'Leff_in_Laguna': 800,
    'Sean_the_Cablinasian': 900,
    'Kaleb_in_Green_Bay': 1300,
    'Vic_in_NoCal': 1500,
    'Rick_in_Buffalo': 1500,
    'V_in_the_Fee': 3200,
    'Mike_in_Indy': 3400,
    'Iafrate': 3800,
    'Silk_Brah': 4200,
    'Benny_in_Wisco': 5800,
    'Jeff_from_Richmond': 5800,
    'Matt_in_LA': 7000,
    'James_in_Portland': 7000,
    'Amber_in_Portland': 7000,
    'Dan_in_Denver': 8000,
    'KC_in_LA': 8000,
    'Steve_Carbone': 8500,
    'Jason_in_Fullerton': 8800,
    'Gail_in_Valencia': 8800,
    'Jeff_in_Southfield': 9000,
    'Nick_Caserio': 9500,
    'Bode_in_Pearland': 10000,
    'John_in_New_York': 10000,
    'Drizzle_in_Wichita': 10000,
    'Rich_in_Philly': 10000,
    'Dion_Dawkins': 10000,
    'John_in_Little_Rock': 10000,
    'Eliah_Drinkwitz': 10000,
    'Steve_in_Green_Bay': 10000,
    'Mike_in_Studio_City': 10000,
    'Mike_in_the_Bay': 10000,
    'Dre_in_Providence': 10000
}

# ---------- Helpers ----------
def implied_prob_from_american(odds: float) -> float:
    # Positive American odds: P = 100 / (odds + 100)
    return 100.0 / (odds + 100.0)

def normalize_probs(d: dict) -> dict:
    names = list(d.keys())
    vals = np.array(list(d.values()), dtype=float)
    vals = vals / vals.sum()
    return dict(zip(names, vals))

def pretty_name(name: str) -> str:
    name = name.replace("_", " ").replace("-", " ")
    return re.sub(r"\s+", " ", name).strip()

def predict_winner(probs_dict: dict, seed: Optional[int] = None) -> str:
    names = np.array(list(probs_dict.keys()))
    p = np.array(list(probs_dict.values()), dtype=float)
    p /= p.sum()
    rng = np.random.default_rng(seed)
    return rng.choice(names, p=p)

# Celebration: ticker-tape rain (no external JS; tunable & starts immediately)
def ticker_tape_rain(duration_sec: int = 5, density: int = 220, depth_vh: int = 200, speed_sec: float = 4.0):
    """
    A JS-free celebratory overlay that 'rains' colored streamers down the screen.
    - duration_sec: how long the overlay stays visible
    - density: how many pieces fall
    - depth_vh: how far they travel (e.g., 200 means to ~200% of viewport height)
    - speed_sec: how fast they fall (animation duration)
    """
    colors = ["#E91E63", "#9C27B0", "#3F51B5", "#2196F3", "#00BCD4",
              "#4CAF50", "#8BC34A", "#FFC107", "#FF9800", "#FF5722"]

    spans = []
    for _ in range(density):
        left = random.uniform(0, 100)         # vw
        w = random.uniform(6, 12)             # px
        h = random.uniform(14, 22)            # px
        rot = random.uniform(0, 360)
        delay = random.uniform(0, 0.6)        # s
        color = random.choice(colors)
        opacity = random.uniform(0.85, 1.0)
        spans.append(
            f"<span style='left:{left:.2f}vw;width:{w:.1f}px;height:{h:.1f}px;"
            f"background:{color};transform:rotate({rot:.1f}deg);"
            f"animation-delay:{delay:.2f}s;opacity:{opacity:.2f};'></span>"
        )

    ph = st.empty()
    ph.markdown(
        f"""
        <style>
          @keyframes streamerFall {{
            0%   {{ transform: translateY(-10vh) rotate(0deg);   }}
            100% {{ transform: translateY({depth_vh}vh) rotate(540deg); }}
          }}
          .ticker-overlay {{
            position: fixed; inset: 0; z-index: 9999; pointer-events: none; overflow: hidden;
          }}
          .ticker-overlay span {{
            position: absolute; top: -10vh; border-radius: 2px;
            animation: streamerFall {speed_sec}s linear forwards;
            mix-blend-mode: normal;
          }}
        </style>
        <div class="ticker-overlay">
          {''.join(spans)}
        </div>
        """,
        unsafe_allow_html=True
    )
    time.sleep(duration_sec)
    ph.empty()

# ---------- Convert odds -> normalized probabilities ----------
implied = {k: implied_prob_from_american(v) for k, v in smackoff_odds_raw.items()}
smackoff_probs = normalize_probs(implied)

# ---------- Probability Table (clean index, percent strings, styled & narrower) ----------
st.markdown(
    "<h3 style='text-align:center;'>Field & Probabilities (Based on Stucknut&#39;s Odds)</h3>",
    unsafe_allow_html=True
)

prob_df = (
    pd.Series(smackoff_probs, name="Probability")
      .to_frame()
      .rename_axis("Clone")
      .sort_values("Probability", ascending=False)
)

# Clean names and format percent strings
prob_df_display = prob_df.copy()
prob_df_display.index = prob_df_display.index.map(pretty_name)
prob_df_display["Probability (%)"] = (prob_df_display["Probability"] * 100).map(lambda x: f"{x:.2f}%")
prob_df_display = prob_df_display.drop(columns=["Probability"])

# Style: bigger/bolder text; center the % column; nicer header
styler = (
    prob_df_display.style
      .set_properties(**{"font-size": "18px"})  # body font
      .set_properties(subset=["Probability (%)"], **{"text-align": "center", "font-weight": "700"})
      .set_table_styles([
          {"selector": "th", "props": [("font-size", "18px"), ("font-weight", "700"), ("text-align", "center")]}
      ])
)

# Put the table and controls in a centered, slightly narrower column
left, mid, right = st.columns([1, 1.2, 1])
with mid:
    st.table(styler)

# ---------- Single Draw (hardcoded seed/seconds/title) ----------
SEED = 30
COUNTDOWN_SECONDS = 3
TITLE_TEXT = "💰 Smackoff Winner ⌚"

with mid:
    # Placeholder ABOVE the button for countdown & reveal
    reveal_area = st.empty()
    # Button (below the placeholder)
    go = st.button("Predict Smackoff 30 Winner", type="primary", use_container_width=True)

if go:
    winner_raw = predict_winner(smackoff_probs, seed=SEED)
    winner = pretty_name(winner_raw)

    # Countdown ABOVE the button
    for s in range(int(COUNTDOWN_SECONDS), 0, -1):
        reveal_area.markdown(f"""
        <div style="font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;
                    text-align:center; padding:0;">
          <div style="font-size:28px; margin-bottom:12px;">And the Smackoff 30 Winner is ...</div>
          <div style="font-size:64px; font-weight:800;">{s}</div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(1)

    # Reveal ABOVE the button (same placeholder)
    reveal_area.markdown(f"""
    <div style="display:flex; align-items:center; justify-content:center; height:50vh;">
      <div style="font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif; text-align:center;">
        <div style="font-size:22px; opacity:0.85;">{TITLE_TEXT}</div>
        <div style="margin-top:28px; font-size:72px; font-weight:900; letter-spacing:0.5px;">
          {winner}
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Celebrations (instant + deeper fall; tweak to taste)
    ticker_tape_rain(duration_sec=5, density=220, depth_vh=200, speed_sec=4.0)
    # Optional: also add a quick toast
    st.toast("🎉 Winner revealed!", icon="🥳")
