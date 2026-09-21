import streamlit as st
import pandas as pd
import requests
import time

# Set up page styling
st.set_page_config(page_title="Predators Skater Tracker", page_icon="🏒", layout="wide")

st.title("🟡 Nashville Predators Skater Tracker")
st.caption("Live production, ice-time share, and scoring trajectories via NHL API")

# --- 1. Fetch Roster & Headshots ---
BASE_URL = "https://api-web.nhle.com/v1"
TEAM_TRICODE = "NSH"

@st.cache_data(ttl=3600)  # Caches data for 1 hour so the site loads fast
def load_skater_summary(season="20242025"):
    # (We can test with 20242025 first so all 82 games show up immediately)
    url = f"{BASE_URL}/roster/{TEAM_TRICODE}/{season}"
    res = requests.get(url)
    if res.status_code != 200:
        # Fallback to current roster if season endpoint varies
        res = requests.get(f"{BASE_URL}/roster/{TEAM_TRICODE}/current")
    
    roster_data = res.json()
    skaters = []
    
    for group in ["forwards", "defensemen"]:
        for p in roster_data.get(group, []):
            skaters.append({
                "player_id": p["id"],
                "name": f"{p['firstName']['default']} {p['lastName']['default']}",
                "number": p.get("sweaterNumber", "--"),
                "position": p.get("positionCode", "N/A"),
                "headshot": f"https://assets.nhle.com/mugs/nhl/latest/{p['id']}.png"
            })
            
    # For demonstration/initial test, let's pull season totals
    # (We will expand this to full game-log trajectories next)
    rows = []
    for s in skaters:
        gl_url = f"{BASE_URL}/player/{s['player_id']}/game-log/{season}/2"
        gl_res = requests.get(gl_url)
        games = gl_res.json().get("gameLog", []) if gl_res.status_code == 200 else []
        
        gp = len(games)
        goals = sum(g.get("goals", 0) for g in games)
        assists = sum(g.get("assists", 0) for g in games)
        pts = sum(g.get("points", 0) for g in games)
        shots = sum(g.get("shots", 0) for g in games)
        
        # Calculate minutes
        toi_sec = 0
        for g in games:
            t = g.get("toi", "00:00").split(":")
            toi_sec += int(t[0]) * 60 + int(t[1])
        toi_min = toi_sec / 60.0
        
        p60 = round((pts / toi_min) * 60, 2) if toi_min > 0 else 0.0
        toi_gp = round(toi_min / gp, 1) if gp > 0 else 0.0
        
        rows.append({
            "Headshot": s["headshot"],
            "Name": s["name"],
            "#": s["number"],
            "Pos": s["position"],
            "GP": gp,
            "G": goals,
            "A": assists,
            "PTS": pts,
            "SOG": shots,
            "P/60": p60,
            "TOI/GP": toi_gp
        })
        time.sleep(0.05)
        
    df = pd.DataFrame(rows)
    return df[df["GP"] > 0].sort_values(by="PTS", ascending=False).reset_index(drop=True)

# Load the data
with st.spinner("Fetching Predators roster stats..."):
    df = load_skater_summary()

# --- 2. Top Scorers Cards Row ---
st.subheader("🏆 Top Producers")
top_cols = st.columns(3)

for i in range(min(3, len(df))):
    p = df.iloc[i]
    with top_cols[i]:
        st.image(p["Headshot"], width=130)
        st.markdown(f"### #{p['#']} {p['Name']}")
        st.write(f"**Position:** {p['Pos']} | **GP:** {p['GP']}")
        st.metric(label="Total Points", value=f"{p['PTS']} PTS", delta=f"{p['G']}G, {p['A']}A")
        st.write(f"⏱️ **TOI/GP:** {p['TOI/GP']} min | 🎯 **P/60:** {p['P/60']}")

st.divider()

# --- 3. Full Team Leaderboard Table ---
st.subheader("📋 Skater Leaderboard")
st.dataframe(
    df[["Name", "#", "Pos", "GP", "G", "A", "PTS", "SOG", "P/60", "TOI/GP"]],
    use_container_width=True,
    hide_index=True
)
