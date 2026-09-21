import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Predators Skater Tracker", page_icon="🏒", layout="wide")

st.title("🟡 Nashville Predators Skater Performance & Value Index")
st.caption("Rate scoring, two-way effectiveness, and special-teams impact via NHL API")

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
        
        # Power Play & Short-Handed Counting Stats (checking alternative key variants)
        pp_goals = s.get("powerPlayGoals", 0)
        pp_assists = s.get("powerPlayAssists") or s.get("ppAssists") or 0
        pp_points = s.get("powerPlayPoints") or (pp_goals + pp_assists)
        
        sh_goals = s.get("shorthandedGoals", 0)
        sh_assists = s.get("shorthandedAssists") or s.get("shAssists") or 0
        sh_points = s.get("shorthandedPoints") or (sh_goals + sh_assists)
        
        gw_goals = s.get("gameWinningGoals", 0)

        # Percentages
        sh_pct = s.get("shootingPctg", 0.0)
        sh_pct = round(sh_pct * 100, 4) if isinstance(sh_pct, float) and sh_pct <= 1.0 else round(float(sh_pct), 4)

        fo_pct = s.get("faceoffWinningPctg", 0.0)
        fo_pct = round(fo_pct * 100, 4) if isinstance(fo_pct, float) and fo_pct <= 1.0 else round(float(fo_pct), 4)

        # TOI Parsing Helper (handles seconds, MM:SS strings, or direct decimals)
        def parse_toi(val):
            if not val:
                return 0.0
            if isinstance(val, (int, float)):
                return val / 60.0
            if isinstance(val, str) and ":" in val:
                parts = val.split(":")
                return int(parts[0]) + (int(parts[1]) / 60.0)
            return float(val) / 60.0 if str(val).replace(".", "").isdigit() else 0.0

        # Look up all official NHL API variants for overall and special teams TOI
        toi_raw = s.get("timeOnIcePerGame") or s.get("avgTimeOnIcePerGame") or s.get("avgToi") or 0
        pp_toi_raw = (
            s.get("powerPlayTimeOnIcePerGame") or 
            s.get("powerPlayToi") or 
            s.get("ppTimeOnIcePerGame") or 
            s.get("ppTimeOnIce") or 0
        )
        sh_toi_raw = (
            s.get("shorthandedTimeOnIcePerGame") or 
            s.get("shorthandedToi") or 
            s.get("shTimeOnIcePerGame") or 
            s.get("shTimeOnIce") or 0
        )

        toi_gp_min = parse_toi(toi_raw)
        pp_toi_gp = parse_toi(pp_toi_raw)
        sh_toi_gp = parse_toi(sh_toi_raw)

        total_toi_min = toi_gp_min * gp
        total_pp_toi_min = pp_toi_gp * gp

        # Per-60 rate conversions
        p60 = round((pts / total_toi_min) * 60, 4) if total_toi_min > 0 else 0.0
        sog60 = round((shots / total_toi_min) * 60, 4) if total_toi_min > 0 else 0.0
        pm60 = round((plus_minus / total_toi_min) * 60, 4) if total_toi_min > 0 else 0.0
        pim60 = round((pim / total_toi_min) * 60, 4) if total_toi_min > 0 else 0.0
        ppp60 = round((pp_points / total_pp_toi_min) * 60, 4) if total_pp_toi_min > 0 else 0.0

        # Composite Effectiveness Ratings
        off_score = round(p60 + (sog60 * 0.25) + ((pp_points / gp) * 0.5), 4) if gp > 0 else 0.0
        def_score = round((pm60 * 1.5) + (toi_gp_min * 0.1) + ((sh_goals / gp) * 1.0) - (pim60 * 0.2), 4) if gp > 0 else 0.0
        
        # Special Teams Ratings
        pp_score = round(ppp60 + ((pp_goals / gp) * 2.0), 4) if gp > 0 else 0.0
        pk_score = round((sh_toi_gp * 1.5) + ((sh_points / gp) * 2.0) - ((pim / gp) * 0.25), 4) if gp > 0 else 0.0

        player_id = s.get("playerId")
        first_name = s.get("firstName", {}).get("default", "")
        last_name = s.get("lastName", {}).get("default", "")

        rows.append({
            "Headshot": s.get("headshot", f"https://assets.nhle.com/mugs/nhl/latest/{player_id}.png"),
            "Name": f"{first_name} {last_name}",
            "Pos": s.get("positionCode", "N/A"),
            "GP": int(gp),
            "G": int(goals),
            "A": int(assists),
            "PTS": int(pts),
            "+/-": int(plus_minus),
            "PIM": int(pim),
            "SOG": int(shots),
            "SH%": sh_pct,
            "PPG": int(pp_goals),
            "PPA": int(pp_assists),
            "PPP": int(pp_points),
            "SHG": int(sh_goals),
            "SHA": int(sh_assists),
            "SHP": int(sh_points),
            "GWG": int(gw_goals),
            "FO%": fo_pct,
            "TOI/GP": round(toi_gp_min, 4),
            "PP_TOI/GP": round(pp_toi_gp, 4),
            "SH_TOI/GP": round(sh_toi_gp, 4),
            "P/60": p60,
            "SOG/60": sog60,
            "+/- /60": pm60,
            "PPP/60": ppp60,
            "Off_Score": off_score,
            "Def_Score": def_score,
            "PP_Score": pp_score,
            "PK_Score": pk_score
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df[df["GP"] > 0].sort_values(by="PTS", ascending=False).reset_index(drop=True)
    return df

# --- Outlier Styling (Min 5 GP filter) ---
def apply_outlier_styling(data_df, cols_to_style, min_gp=5, high_q=0.85, low_q=0.15):
    """Styles target columns green/red using only players with >= min_gp to calculate thresholds."""
    styler_df = pd.DataFrame('', index=data_df.index, columns=data_df.columns)
    eligible_mask = data_df["GP"] >= min_gp
    eligible_df = data_df[eligible_mask]

    for col in cols_to_style:
        if col not in data_df.columns:
            continue
            
        eligible_vals = eligible_df[col].dropna()
        if len(eligible_vals) < 3:
            continue
            
        high_thresh = eligible_vals.quantile(high_q)
        low_thresh = eligible_vals.quantile(low_q)

        for idx in data_df.index:
            if not eligible_mask.loc[idx]:
                continue
            val = data_df.loc[idx, col]
            if pd.isna(val):
                continue
            if val >= high_thresh:
                styler_df.loc[idx, col] = 'background-color: rgba(34, 197, 94, 0.35); font-weight: bold;'
            elif val <= low_thresh:
                styler_df.loc[idx, col] = 'background-color: rgba(239, 68, 68, 0.35); font-weight: bold;'
                
    return styler_df

with st.spinner("Fetching player analytics..."):
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
            st.markdown(f"⚡ **Off:** `{p['Off_Score']:.4f}` | 🛡️ **Def:** `{p['Def_Score']:.4f}`")
            st.caption(f"🎯 PP: `{p['PP_Score']:.4f}` | 🧱 PK: `{p['PK_Score']:.4f}`")

st.divider()

# --- Tabbed Analytical Views with 4-Decimal Precision ---
st.subheader("📊 Roster Effectiveness & Advanced Leaderboards")
st.caption("🟢 **Green:** Top 15% tier | 🔴 **Red:** Bottom 15% tier (Minimum 5 GP required to qualify)")

format_4dec = {
    "Off_Score": "{:.4f}",
    "Def_Score": "{:.4f}",
    "PP_Score": "{:.4f}",
    "PK_Score": "{:.4f}",
    "P/60": "{:.4f}",
    "SOG/60": "{:.4f}",
    "+/- /60": "{:.4f}",
    "PPP/60": "{:.4f}",
    "TOI/GP": "{:.4f}",
    "PP_TOI/GP": "{:.4f}",
    "SH_TOI/GP": "{:.4f}",
    "SH%": "{:.4f}%",
    "FO%": "{:.4f}%"
}

if not df.empty:
    tab1, tab2, tab3, tab4 = st.tabs([
        "⚡ Offensive Impact", 
        "🛡️ Defensive Impact", 
        "🚨 Special Teams (PP & PK)", 
        "📋 Complete Statistics"
    ])

    with tab1:
        st.markdown("**Ranked by `Off_Score` (P/60 + SOG/60 + Power Play Generation):**")
        off_df = df[["Name", "Pos", "GP", "Off_Score", "P/60", "SOG/60", "PTS", "G", "A", "SOG", "SH%", "PPP", "GWG"]].sort_values(by="Off_Score", ascending=False).reset_index(drop=True)
        styled_off = (
            off_df.style
            .apply(lambda _: apply_outlier_styling(off_df, ["Off_Score", "P/60", "SOG/60", "PTS", "SH%"], min_gp=5), axis=None)
            .format(format_4dec)
        )
        st.dataframe(styled_off, use_container_width=True, hide_index=True)

    with tab2:
        st.markdown("**Ranked by `Def_Score` (On-Ice Goal Differential per 60 + TOI Burden - Penalty Discipline):**")
        def_df = df[["Name", "Pos", "GP", "Def_Score", "+/- /60", "TOI/GP", "+/-", "PIM", "SHG", "FO%"]].sort_values(by="Def_Score", ascending=False).reset_index(drop=True)
        styled_def = (
            def_df.style
            .apply(lambda _: apply_outlier_styling(def_df, ["Def_Score", "+/- /60", "TOI/GP", "+/-", "FO%"], min_gp=5), axis=None)
            .format(format_4dec)
        )
        st.dataframe(styled_def, use_container_width=True, hide_index=True)

    with tab3:
        st.markdown("**Ranked by Special Teams Impact (`PP_Score` & `PK_Score`):**")
        st_df = df[["Name", "Pos", "GP", "PP_Score", "PK_Score", "PPP/60", "PP_TOI/GP", "PPP", "PPG", "SH_TOI/GP", "SHP", "SHG", "PIM"]].sort_values(by="PP_Score", ascending=False).reset_index(drop=True)
        styled_st = (
            st_df.style
            .apply(lambda _: apply_outlier_styling(st_df, ["PP_Score", "PK_Score", "PPP/60", "PP_TOI/GP", "SH_TOI/GP"], min_gp=5), axis=None)
            .format(format_4dec)
        )
        st.dataframe(styled_st, use_container_width=True, hide_index=True)

    with tab4:
        comp_df = df[[
            "Name", "Pos", "GP", "Off_Score", "Def_Score", "PP_Score", "PK_Score",
            "PTS", "G", "A", "+/-", "P/60", "TOI/GP", "PP_TOI/GP", "SH_TOI/GP",
            "SOG", "SH%", "PIM", "PPG", "PPP", "SHG", "SHP", "GWG", "FO%"
        ]].sort_values(by="PTS", ascending=False).reset_index(drop=True)
        styled_comp = (
            comp_df.style
            .apply(lambda _: apply_outlier_styling(comp_df, ["Off_Score", "Def_Score", "PP_Score", "PK_Score", "PTS", "+/-", "P/60", "TOI/GP"], min_gp=5), axis=None)
            .format(format_4dec)
        )
        st.dataframe(styled_comp, use_container_width=True, hide_index=True)
