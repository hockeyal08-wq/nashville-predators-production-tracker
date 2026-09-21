import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Predators Skater Tracker", page_icon="🏒", layout="wide")

st.title("🟡 Nashville Predators Skater Tracker")
st.caption("Live offensive production, defensive impact, and ice-time distributions via NHL API")

# --- Sidebar Controls ---
st.sidebar.header("Filter Settings")

selected_season = st.sidebar.selectbox(
    "Select Season",
    options=["20262027", "20252026", "20242025", "20232024"],
    index=0
)

game_type_label = st.sidebar.radio(
    "Game Type",
    options=["Regular Season", "Playoffs"],
    index=0
)
game_type_code = "2" if game_type_label == "Regular Season" else "3"

position_filter = st.sidebar.selectbox(
    "Position Group",
    options=["All Skaters", "Forwards", "Defensemen"],
    index=0
)

BASE_URL = "https://api-web.nhle.com/v1"
TEAM_TRICODE = "NSH"

@st.cache_data(ttl=900)
def load_club_skater_stats(season, game_type):
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
        plus_minus = s.get("plusMinus", 0)
        pim = s.get("penaltyMinutes", 0)
        pp_goals = s.get("powerPlayGoals", 0)
        pp_points = s.get("powerPlayPoints", 0)
        sh_goals = s.get("shorthandedGoals", 0)
        gw_goals = s.get("gameWinningGoals", 0)
        
        # Shooting Pct
        sh_pct = s.get("shootingPctg", 0.0)
        if isinstance(sh_pct, float) and sh_pct <= 1.0:
            sh_pct = round(sh_pct * 100, 1)
        else:
            sh_pct = round(float(sh_pct), 1)

        # Faceoff Win Pct
        fo_pct = s.get("faceoffWinningPctg", 0.0)
        if isinstance(fo_pct, float) and fo_pct <= 1.0:
            fo_pct = round(fo_pct * 100, 1)
        else:
            fo_pct = round(float(fo_pct), 1)

        # TOI Parsing
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
        pos = s.get("positionCode", "N/A")

        rows.append({
            "Headshot": s.get("headshot", f"https://assets.nhle.com/mugs/nhl/latest/{player_id}.png"),
            "Name": f"{first_name} {last_name}",
            "Pos": pos,
            "GP": gp,
            "G": goals,
            "A": assists,
            "PTS": pts,
            "+/-": plus_minus,
            "PIM": pim,
            "SOG": shots,
            "SH%": sh_pct,
            "PPG": pp_goals,
            "PPP": pp_points,
            "SHG": sh_goals,
            "GWG": gw_goals,
            "FO%": fo_pct,
            "P/60": p60,
            "TOI/GP": round(toi_gp_min, 1)
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df[df["GP"] > 0].sort_values(by="PTS", ascending=False).reset_index(drop=True)
    return df

with st.spinner("Fetching player analytics..."):
    df = load_club_skater_stats(selected_season, game_type_code)

# Filter by position
if not df.empty:
    if position_filter == "Forwards":
        df = df[df["Pos"].isin(["C", "L", "R", "F"])].reset_index(drop=True)
    elif position_filter == "Defensemen":
        df = df[df["Pos"] == "D"].reset_index(drop=True)

# --- Top Scorers Summary Cards ---
st.subheader("🏆 Top Producers")

if df.empty:
    st.info(f"No {game_type_label.lower()} stats recorded yet for {selected_season[:4]}-{selected_season[4:]}.")
else:
    top_cols = st.columns(min(3, len(df)))
    for i in range(min(3, len(df))):
        p = df.iloc[i]
        with top_cols[i]:
            st.image(p["Headshot"], width=125)
            st.markdown(f"### {p['Name']}")
            st.write(f"**Pos:** {p['Pos']} | **GP:** {p['GP']} | **+/-:** `{p['+/-']:+d}`")
            st.metric(label="Total Points", value=f"{p['PTS']} PTS", delta=f"{p['G']}G, {p['A']}A")
            st.write(f"⏱️ **TOI/GP:** {p['TOI/GP']} min | 🎯 **P/60:** {p['P/60']}")

st.divider()

# --- Tabbed Analytical Views ---
st.subheader("📊 Roster Performance & Effectiveness")

if not df.empty:
    tab1, tab2, tab3 = st.tabs(["⚡ Offensive Efficiency", "🛡️ Defensive & Two-Way Impact", "📋 All Skater Stats"])

    with tab1:
        st.markdown("**Finishing, shot conversion, power-play generation, and scoring rates per 60 minutes.**")
        st.dataframe(
            df[["Name", "Pos", "GP", "G", "A", "PTS", "P/60", "SOG", "SH%", "PPG", "PPP", "GWG"]].sort_values(by="P/60", ascending=False),
            use_container_width=True,
            hide_index=True
        )

    with tab2:
        st.markdown("**Ice-time burdens, penalty discipline, net goal differential, short-handed scoring, and faceoff share.**")
        st.dataframe(
            df[["Name", "Pos", "GP", "TOI/GP", "+/-", "PIM", "SHG", "FO%"]].sort_values(by="TOI/GP", ascending=False),
            use_container_width=True,
            hide_index=True
        )

    with tab3:
        st.dataframe(
            df[["Name", "Pos", "GP", "G", "A", "PTS", "+/-", "SOG", "SH%", "P/60", "TOI/GP", "PIM", "PPG", "PPP", "SHG", "GWG", "FO%"]],
            use_container_width=True,
            hide_index=True
        )
