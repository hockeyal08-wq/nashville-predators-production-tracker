import streamlit as st
import pandas as pd
import requests

# Page setup
st.set_page_config(page_title="Predators Skater Tracker", page_icon="🏒", layout="wide")

st.title("🟡 Nashville Predators Skater Tracker")
st.caption("Live production, ice-time share, and scoring rates via NHL API")

# --- Sidebar Controls ---
st.sidebar.header("Filter Settings")

selected_season = st.sidebar.selectbox(
    "Select Season",
    options=["20262027", "20252026", "20242025", "20232024"],
    index=0  # Defaults to 2026-2027
)

game_type_label = st.sidebar.radio(
    "Game Type",
    options=["Regular Season", "Preseason"],
    index=0
)
game_type_code = "2" if game_type_label == "Regular Season" else "1"

BASE_URL = "https://api-web.nhle.com/v1"
TEAM_TRICODE = "NSH"

@st.cache_data(ttl=600)  # Caches for 10 minutes so new games refresh automatically
def load_club_skater_stats(season, game_type):
    # Strict endpoint call for the exact season and game type selected
    url = f"{BASE_URL}/club-stats/{TEAM_TRICODE}/{season}/{game_type}"
    res = requests.get(url)
    if res.status_code != 200:
        return pd.DataFrame()
    
    data = res.json()
    skaters = data.get("skaters", [])
    if not skaters:
        return pd.DataFrame()

    rows = []
    for s in skaters:
        gp = s.get("gamesPlayed", 0)
        pts = s.get("points", 0)
        goals = s.get("goals", 0)
        assists = s.get("assists", 0)
        shots = s.get("shots", 0)

        # Parse TOI handling numeric seconds, MM:SS strings, and decimal representations
        toi_raw = s.get("timeOnIcePerGame") or s.get("avgTimeOnIcePerGame") or s.get("avgToi") or 0
        if isinstance(toi_raw, (int, float)):
            toi_gp_min = toi_raw / 60.0
        elif isinstance(toi_raw, str) and ":" in toi_raw:
            parts = toi_raw.split(":")
            toi_gp_min = int(parts[0]) + (int(parts[1]) / 60.0)
        else:
            toi_gp_min = float(toi_raw) / 60.0 if str(toi_raw).replace(".", "").isdigit() else 0.0

        total_toi_min = toi_gp_min * gp
        p60 = round((pts / total_toi_min) * 60, 2) if total_toi_min > 0 else 0.0

        player_id = s.get("playerId")
        first_name = s.get("firstName", {}).get("default", "")
        last_name = s.get("lastName", {}).get("default", "")

        rows.append({
            "Headshot": s.get("headshot", f"https://assets.nhle.com/mugs/nhl/latest/{player_id}.png"),
            "Name": f"{first_name} {last_name}",
            "Pos": s.get("positionCode", "N/A"),
            "GP": gp,
            "G": goals,
            "A": assists,
            "PTS": pts,
            "SOG": shots,
            "P/60": p60,
            "TOI/GP": round(toi_gp_min, 1)
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        # Keep players with at least 1 game played in that specific game type
        df = df[df["GP"] > 0].sort_values(by="PTS", ascending=False).reset_index(drop=True)
    return df

with st.spinner("Fetching stats..."):
    df = load_club_skater_stats(selected_season, game_type_code)

# --- Top Scorers Cards Row ---
st.subheader("🏆 Top Producers")

if df.empty:
    st.info(f"No {game_type_label.lower()} games logged yet for {selected_season[:4]}-{selected_season[4:]}. Production cards and the table will populate as games are submitted.")
else:
    top_cols = st.columns(min(3, len(df)))
    for i in range(min(3, len(df))):
        p = df.iloc[i]
        with top_cols[i]:
            st.image(p["Headshot"], width=130)
            st.markdown(f"### {p['Name']}")
            st.write(f"**Position:** {p['Pos']} | **GP:** {p['GP']}")
            st.metric(label="Points", value=f"{p['PTS']} PTS", delta=f"{p['G']}G, {p['A']}A")
            st.write(f"⏱️ **TOI/GP:** {p['TOI/GP']} min | 🎯 **P/60:** {p['P/60']}")

st.divider()

# --- Full Team Leaderboard Table ---
st.subheader("📋 Skater Leaderboard")
if not df.empty:
    st.dataframe(
        df[["Name", "Pos", "GP", "G", "A", "PTS", "SOG", "P/60", "TOI/GP"]],
        use_container_width=True,
        hide_index=True
    )
