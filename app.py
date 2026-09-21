import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Predators Skater Tracker", page_icon="🏒", layout="wide")

st.title("🟡 Nashville Predators Skater Performance & Value Index")
st.caption("Rate scoring, two-way effectiveness models, and ice-time distributions via NHL API")

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

        # Shooting %
        sh_pct = s.get("shootingPctg", 0.0)
        sh_pct = round(sh_pct * 100, 1) if isinstance(sh_pct, float) and sh_pct <= 1.0 else round(float(sh_pct), 1)

        # Faceoff Win %
        fo_pct = s.get("faceoffWinningPctg", 0.0)
        fo_pct = round(fo_pct * 100, 1) if isinstance(fo_pct, float) and fo_pct <= 1.0 else round(float(fo_pct), 1)

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

        # Per-60 rate conversions
        p60 = round((pts / total_toi_min) * 60, 2) if total_toi_min > 0 else 0.0
        sog60 = round((shots / total_toi_min) * 60, 2) if total_toi_min > 0 else 0.0
        pm60 = round((plus_minus / total_toi_min) * 60, 2) if total_toi_min > 0 else 0.0
        pim60 = round((pim / total_toi_min) * 60, 2) if total_toi_min > 0 else 0.0

        # --- Composite Ratings ---
        # Offensive Rating: Points rate (weight: 1.0) + Shot generation rate (weight: 0.25) + PP production per GP (weight: 0.5)
        off_score = round(p60 + (sog60 * 0.25) + ((pp_points / gp) * 0.5), 2) if gp > 0 else 0.0

        # Defensive Rating: Net on-ice goal rate (weight: 1.5) + Heavy TOI workload baseline (weight: 0.1) + PK short-handed output - Penalty cost
        def_score = round((pm60 * 1.5) + (toi_gp_min * 0.1) + ((sh_goals / gp) * 1.0) - (pim60 * 0.2), 2) if gp > 0 else 0.0

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
            "+/-": plus_minus,
            "PIM": pim,
            "SOG": shots,
            "SH%": sh_pct,
            "PPG": pp_goals,
            "PPP": pp_points,
            "SHG": sh_goals,
            "GWG": gw_goals,
            "FO%": fo_pct,
            "TOI/GP": round(toi_gp_min, 1),
            "P/60": p60,
            "SOG/60": sog60,
            "+/- /60": pm60,
            "Off_Score": off_score,
            "Def_Score": def_score
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df[df["GP"] > 0].sort_values(by="PTS", ascending=False).reset_index(drop=True)
    return df

with st.spinner("Fetching stats..."):
    df = load_club_skater_stats(selected_season, game_type_code)

if not df.empty:
    if position_filter == "Forwards":
        df = df[df["Pos"].isin(["C", "L", "R", "F"])].reset_index(drop=True)
    elif position_filter == "Defensemen":
        df = df[df["Pos"] == "D"].reset_index(drop=True)

# --- Top Scorers Summary Cards ---
st.subheader("🏆 Top Producers")

if df.empty:
    st.info(f"No {game_type_label.lower()} stats recorded yet for {selected_season[:4]}-{selected_season[4:]}. Live box scores will populate here as regular season play starts.")
else:
    top_cols = st.columns(min(3, len(df)))
    for i in range(min(3, len(df))):
        p = df.iloc[i]
        with top_cols[i]:
            st.image(p["Headshot"], width=125)
            st.markdown(f"### {p['Name']}")
            st.write(f"**Pos:** {p['Pos']} | **GP:** {p['GP']} | **+/-:** `{p['+/-']:+d}`")
            st.metric(label="Total Points", value=f"{p['PTS']} PTS", delta=f"{p['G']}G, {p['A']}A")
            st.markdown(f"⚡ **Off Rating:** `{p['Off_Score']}` | 🛡️ **Def Rating:** `{p['Def_Score']}`")
            st.caption(f"⏱️ TOI/GP: {p['TOI/GP']}m | 🎯 P/60: {p['P/60']}")

st.divider()

# --- Tabbed Analytical Views ---
st.subheader("📊 Roster Effectiveness & Advanced Leaderboards")

if not df.empty:
    tab1, tab2, tab3 = st.tabs(["⚡ Offensive Impact (Off_Score)", "🛡️ Defensive Impact (Def_Score)", "📋 Complete Statistics"])

    with tab1:
        st.markdown("**Ranked by `Off_Score` (P/60 + SOG/60 + Power Play Generation):**")
        st.dataframe(
            df[["Name", "Pos", "GP", "Off_Score", "P/60", "SOG/60", "PTS", "G", "A", "SOG", "SH%", "PPP", "GWG"]].sort_values(by="Off_Score", ascending=False),
            use_container_width=True,
            hide_index=True
        )

    with tab2:
        st.markdown("**Ranked by `Def_Score` (On-Ice Goal Differential per 60 + TOI Burden - Penalty Discipline):**")
        st.dataframe(
            df[["Name", "Pos", "GP", "Def_Score", "+/- /60", "TOI/GP", "+/-", "PIM", "SHG", "FO%"]].sort_values(by="Def_Score", ascending=False),
            use_container_width=True,
            hide_index=True
        )

    with tab3:
        st.dataframe(
            df[["Name", "Pos", "GP", "Off_Score", "Def_Score", "PTS", "G", "A", "+/-", "P/60", "TOI/GP", "SOG", "SH%", "PIM", "PPG", "PPP", "SHG", "GWG", "FO%"]].sort_values(by="PTS", ascending=False),
            use_container_width=True,
            hide_index=True
        )
