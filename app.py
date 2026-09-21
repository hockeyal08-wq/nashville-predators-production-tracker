import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Predators Skater Tracker", page_icon="🏒", layout="wide")

# Custom CSS for flashy spotlight card and roster grid
st.markdown("""
<style>
    .spotlight-card {
        background: linear-gradient(135deg, rgba(254, 187, 0, 0.12) 0%, rgba(4, 30, 66, 0.88) 100%);
        border: 2px solid #FFB81C;
        border-radius: 16px;
        padding: 24px 28px;
        box-shadow: 0 8px 32px rgba(254, 187, 0, 0.22);
        margin-bottom: 24px;
        color: white;
    }
    .spotlight-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        color: #FFB81C;
        letter-spacing: -0.5px;
    }
    .badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 184, 28, 0.5);
        border-radius: 6px;
        padding: 4px 10px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 6px;
        margin-top: 6px;
        margin-bottom: 12px;
    }
    .stat-pill-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-top: 14px;
    }
    .stat-pill {
        background: rgba(10, 22, 40, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 10px;
        padding: 12px;
        text-align: center;
    }
    .stat-pill-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        color: #94A3B8;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .stat-pill-val {
        font-size: 1.35rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-top: 4px;
    }
    .stat-pill-sub {
        font-size: 0.75rem;
        color: #FFB81C;
        margin-top: 2px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🟡 Nashville Predators Skater Performance & Value Index")
st.caption("Live player spotlight, two-way effectiveness ratings, and ice-time distributions via NHL API")

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
        sh_goals = s.get("shorthandedGoals", 0)
        gw_goals = s.get("gameWinningGoals", 0)

        # Percentages
        sh_pct = s.get("shootingPctg", 0.0)
        sh_pct = round(sh_pct * 100, 4) if isinstance(sh_pct, float) and sh_pct <= 1.0 else round(float(sh_pct), 4)

        fo_pct = s.get("faceoffWinningPctg", 0.0)
        fo_pct = round(fo_pct * 100, 4) if isinstance(fo_pct, float) and fo_pct <= 1.0 else round(float(fo_pct), 4)

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
        p60 = round((pts / total_toi_min) * 60, 4) if total_toi_min > 0 else 0.0
        sog60 = round((shots / total_toi_min) * 60, 4) if total_toi_min > 0 else 0.0
        pm60 = round((plus_minus / total_toi_min) * 60, 4) if total_toi_min > 0 else 0.0
        pim60 = round((pim / total_toi_min) * 60, 4) if total_toi_min > 0 else 0.0

        # Composite Effectiveness Ratings
        off_score = round(p60 + (sog60 * 0.25) + ((pp_goals / gp) * 1.5), 4) if gp > 0 else 0.0
        def_score = round((pm60 * 1.5) + (toi_gp_min * 0.1) + ((sh_goals / gp) * 2.0) - (pim60 * 0.2), 4) if gp > 0 else 0.0
        pp_score = round(((pp_goals / gp) * 3.0) + (sog60 * 0.1), 4) if gp > 0 else 0.0
        pk_score = round((toi_gp_min * 0.05) + ((sh_goals / gp) * 4.0) - (pim60 * 0.1), 4) if gp > 0 else 0.0

        player_id = s.get("playerId")
        first_name = s.get("firstName", {}).get("default", "")
        last_name = s.get("lastName", {}).get("default", "")

        rows.append({
            "PlayerId": player_id,
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
            "SHG": int(sh_goals),
            "GWG": int(gw_goals),
            "FO%": fo_pct,
            "TOI/GP": round(toi_gp_min, 4),
            "P/60": p60,
            "SOG/60": sog60,
            "+/- /60": pm60,
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

# --- Spotlight Header ---
if df.empty:
    st.info(f"No {game_type_label.lower()} stats recorded yet for {selected_season[:4]}-{selected_season[4:]}.")
else:
    if "selected_player_id" not in st.session_state or st.session_state["selected_player_id"] not in df["PlayerId"].values:
        st.session_state["selected_player_id"] = int(df.iloc[0]["PlayerId"])

    p = df[df["PlayerId"] == st.session_state["selected_player_id"]].iloc[0]

    # Large Gold Glow Spotlight Banner
    spotlight_html = f"""
    <div class="spotlight-card">
        <div style="display: flex; gap: 28px; align-items: center; flex-wrap: wrap;">
            <div style="flex-shrink: 0; text-align: center;">
                <img src="{p['Headshot']}" style="width: 175px; height: 175px; object-fit: cover; border-radius: 50%; border: 3px solid #FFB81C; box-shadow: 0 4px 20px rgba(0,0,0,0.5);">
            </div>
            <div style="flex-grow: 1; min-width: 280px;">
                <h1 class="spotlight-title">{p['Name']}</h1>
                <div>
                    <span class="badge">POSITION: {p['Pos']}</span>
                    <span class="badge">GAMES PLAYED: {p['GP']}</span>
                    <span class="badge">TOI/GP: {p['TOI/GP']:.2f} MIN</span>
                </div>
                <div class="stat-pill-container">
                    <div class="stat-pill">
                        <div class="stat-pill-label">Total Points</div>
                        <div class="stat-pill-val">{p['PTS']}</div>
                        <div class="stat-pill-sub">{p['G']}G, {p['A']}A</div>
                    </div>
                    <div class="stat-pill">
                        <div class="stat-pill-label">Scoring Rate</div>
                        <div class="stat-pill-val">{p['P/60']:.2f}</div>
                        <div class="stat-pill-sub">Points / 60</div>
                    </div>
                    <div class="stat-pill">
                        <div class="stat-pill-label">Offense Index</div>
                        <div class="stat-pill-val">{p['Off_Score']:.4f}</div>
                        <div class="stat-pill-sub">{p['PPG']} PPG</div>
                    </div>
                    <div class="stat-pill">
                        <div class="stat-pill-label">Defense Index</div>
                        <div class="stat-pill-val">{p['Def_Score']:.4f}</div>
                        <div class="stat-pill-sub">{p['+/-']:+d} Net Diff</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(spotlight_html, unsafe_allow_html=True)

    # --- Clickable Roster Grid ---
    st.markdown("### 👥 Select a Skater to Spotlight")
    num_cols = 6
    for i in range(0, len(df), num_cols):
        cols = st.columns(num_cols)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(df):
                skater = df.iloc[idx]
                with col:
                    with st.container(border=True):
                        st.image(skater["Headshot"], use_container_width=True)
                        st.caption(f"**{skater['Name']}** ({skater['Pos']})")
                        st.caption(f"{skater['PTS']} PTS | {skater['GP']} GP")
                        if st.button("Spotlight", key=f"btn_{skater['PlayerId']}", use_container_width=True):
                            st.session_state["selected_player_id"] = int(skater["PlayerId"])
                            st.rerun()

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
    "TOI/GP": "{:.4f}",
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
        st.markdown("**Ranked by `Off_Score` (P/60 + SOG/60 + PP Finishing):**")
        off_df = df[["Name", "Pos", "GP", "Off_Score", "P/60", "SOG/60", "PTS", "G", "A", "SOG", "SH%", "PPG", "GWG"]].sort_values(by="Off_Score", ascending=False).reset_index(drop=True)
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
        st_df = df[["Name", "Pos", "GP", "PP_Score", "PK_Score", "PPG", "SHG", "PIM", "TOI/GP"]].sort_values(by="PP_Score", ascending=False).reset_index(drop=True)
        styled_st = (
            st_df.style
            .apply(lambda _: apply_outlier_styling(st_df, ["PP_Score", "PK_Score", "PPG", "SHG"], min_gp=5), axis=None)
            .format(format_4dec)
        )
        st.dataframe(styled_st, use_container_width=True, hide_index=True)

    with tab4:
        comp_df = df[[
            "Name", "Pos", "GP", "Off_Score", "Def_Score", "PP_Score", "PK_Score",
            "PTS", "G", "A", "+/-", "P/60", "TOI/GP", "SOG", "SH%", "PIM", 
            "PPG", "SHG", "GWG", "FO%"
        ]].sort_values(by="PTS", ascending=False).reset_index(drop=True)
        styled_comp = (
            comp_df.style
            .apply(lambda _: apply_outlier_styling(comp_df, ["Off_Score", "Def_Score", "PP_Score", "PK_Score", "PTS", "+/-", "P/60", "TOI/GP"], min_gp=5), axis=None)
            .format(format_4dec)
        )
        st.dataframe(styled_comp, use_container_width=True, hide_index=True)
