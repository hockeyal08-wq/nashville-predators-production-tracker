import streamlit as st
import pandas as pd
import requests

PREDS_LOGO_URL = "https://assets.nhle.com/logos/nhl/svg/NSH_light.svg"

st.set_page_config(
    page_title="Nashville Predators Hockey Operations Dashboard",
    layout="wide"
)

# Deep franchise theme injection
st.markdown("""
<style>
    /* Full Page Canvas, Main Body & App View Container */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #041E42 !important;
        color: #F8FAFC !important;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif !important;
    }
    
    /* Top Toolbar / Header */
    [data-testid="stHeader"] {
        background-color: rgba(4, 30, 66, 0.95) !important;
    }

    /* Left Sidebar Theming */
    [data-testid="stSidebar"], [data-testid="stSidebarContent"] {
        background-color: #03142D !important;
        border-right: 1.5px solid rgba(255, 184, 28, 0.3) !important;
    }
    [data-testid="stSidebar"] * {
        color: #F8FAFC !important;
    }

    /* Page Padding & Spacing */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 95% !important;
    }

    /* ============================================================ */
    /* SPORTY GOLD CHEVRON BADGE FOR SIDEBAR TOGGLE                 */
    /* ============================================================ */
    
    /* Collapsed Control Toggle (When sidebar is hidden) */
    [data-testid="collapsedControl"] {
        top: 18px !important;
        left: 18px !important;
    }
    [data-testid="collapsedControl"] button {
        background-color: #061F47 !important;
        border: 1.5px solid #FFB81C !important;
        border-radius: 8px !important;
        padding: 4px 8px !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.6), 0 0 10px rgba(255, 184, 28, 0.25) !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    [data-testid="collapsedControl"] button:hover {
        background-color: #FFB81C !important;
        box-shadow: 0 0 16px rgba(255, 184, 28, 0.6) !important;
        transform: scale(1.08);
    }
    [data-testid="collapsedControl"] svg {
        fill: #FFB81C !important;
        stroke: #FFB81C !important;
        transition: all 0.2s ease-in-out !important;
    }
    [data-testid="collapsedControl"] button:hover svg {
        fill: #041E42 !important;
        stroke: #041E42 !important;
    }

    /* Expanded Sidebar Collapse Arrow (<<) */
    [data-testid="stSidebarCollapseButton"] button {
        background-color: #061F47 !important;
        border: 1.5px solid #FFB81C !important;
        border-radius: 8px !important;
        transition: all 0.25s ease-in-out !important;
    }
    [data-testid="stSidebarCollapseButton"] button:hover {
        background-color: #FFB81C !important;
        box-shadow: 0 0 12px rgba(255, 184, 28, 0.5) !important;
    }
    [data-testid="stSidebarCollapseButton"] svg {
        fill: #FFB81C !important;
        stroke: #FFB81C !important;
    }
    [data-testid="stSidebarCollapseButton"] button:hover svg {
        fill: #041E42 !important;
        stroke: #041E42 !important;
    }

    /* Header Container */
    .header-container {
        display: flex;
        align-items: center;
        gap: 22px;
        margin-bottom: 24px;
        border-bottom: 2px solid #FFB81C;
        padding-bottom: 18px;
    }
    .header-logo {
        width: 85px;
        height: auto;
        object-fit: contain;
    }
    .header-title-box h1 {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
        color: #FFFFFF !important;
    }
    .header-subtitle {
        font-size: 0.95rem;
        color: #FFB81C !important;
        margin-top: 5px;
        font-weight: 600;
        letter-spacing: 0.3px;
    }

    /* Executive Spotlight Showcase Card */
    .spotlight-card {
        background: linear-gradient(135deg, #092652 0%, #03142D 100%);
        border: 2px solid #FFB81C;
        border-radius: 12px;
        padding: 24px 30px;
        box-shadow: 0 10px 28px rgba(0, 0, 0, 0.65);
        margin-bottom: 28px;
        color: #FFFFFF;
    }
    .spotlight-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        color: #FFB81C !important;
        letter-spacing: -0.5px;
    }
    .badge {
        display: inline-block;
        background: rgba(255, 184, 28, 0.15);
        border: 1px solid rgba(255, 184, 28, 0.5);
        border-radius: 4px;
        padding: 4px 10px;
        font-size: 0.78rem;
        font-weight: 700;
        margin-right: 6px;
        margin-top: 8px;
        margin-bottom: 14px;
        color: #FFB81C !important;
        letter-spacing: 0.5px;
    }
    .stat-pill-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 14px;
        margin-top: 12px;
    }
    .stat-pill {
        background: #04142B;
        border: 1px solid rgba(255, 184, 28, 0.3);
        border-radius: 8px;
        padding: 12px 16px;
        text-align: left;
    }
    .stat-pill-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        color: #94A3B8 !important;
        font-weight: 700;
        letter-spacing: 0.6px;
    }
    .stat-pill-val {
        font-size: 1.4rem;
        font-weight: 800;
        color: #FFFFFF !important;
        margin-top: 3px;
    }
    .stat-pill-sub {
        font-size: 0.75rem;
        color: #FFB81C !important;
        margin-top: 3px;
        font-weight: 600;
    }

    /* Roster Grid Container Boxes */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: rgba(255, 184, 28, 0.3) !important;
        background-color: #061A3B !important;
        border-radius: 8px !important;
    }

    h1, h2, h3, h4 {
        color: #FFFFFF !important;
    }

    /* Predators Gold Rounded Buttons */
    div[data-testid="stButton"] button[kind="secondary"] {
        background-color: #061F47 !important;
        border: 2px solid #FFB81C !important;
        border-radius: 10px !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        padding: 8px 16px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
        transition: all 0.2s ease-in-out !important;
    }
    div[data-testid="stButton"] button[kind="secondary"]:hover {
        background-color: rgba(255, 184, 28, 0.2) !important;
        box-shadow: 0 0 12px rgba(255, 184, 28, 0.5) !important;
    }
    div[data-testid="stButton"] button[kind="primary"] {
        background-color: #FFB81C !important;
        border: 2px solid #FFB81C !important;
        border-radius: 10px !important;
        color: #041E42 !important;
        -webkit-text-fill-color: #041E42 !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
        padding: 8px 16px !important;
        box-shadow: 0 4px 14px rgba(255, 184, 28, 0.45) !important;
    }

    /* Sidebar Label Styling */
    .filter-label {
        font-size: 0.92rem;
        font-weight: 700;
        color: #FFB81C;
        margin-top: 14px;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Sleek Dataframe Container Styling */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(255, 184, 28, 0.3);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.55);
    }
</style>
""", unsafe_allow_html=True)

# Executive Header with Official Franchise Vector Logo
st.markdown(f"""
<div class="header-container">
    <img src="{PREDS_LOGO_URL}" class="header-logo" alt="Nashville Predators">
    <div class="header-title-box">
        <h1>Nashville Predators | Skater Analytics & Performance Index</h1>
        <div class="header-subtitle">Hockey Operations Evaluation: Production Efficiency, Role Workload, and Two-Way Models</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Sidebar Controls (Interactive Gold & Navy Buttons) ---
st.sidebar.markdown("### Filter Settings")

# 1. Season Selection
st.sidebar.markdown('<div class="filter-label">Season</div>', unsafe_allow_html=True)
season_map = {
    "26/27": "20262027",
    "25/26": "20252026",
    "24/25": "20242025",
    "23/24": "20232024"
}
if "selected_season_label" not in st.session_state:
    st.session_state["selected_season_label"] = "26/27"

s_cols = st.sidebar.columns(2)
for i, label in enumerate(["26/27", "25/26", "24/25", "23/24"]):
    with s_cols[i % 2]:
        btn_type = "primary" if st.session_state["selected_season_label"] == label else "secondary"
        if st.button(label, key=f"btn_season_{label}", type=btn_type, use_container_width=True):
            st.session_state["selected_season_label"] = label
            st.rerun()

selected_season = season_map[st.session_state["selected_season_label"]]

# 2. Game Type Selection
st.sidebar.markdown('<div class="filter-label">Game Type</div>', unsafe_allow_html=True)
if "selected_game_type" not in st.session_state:
    st.session_state["selected_game_type"] = "Regular Season"

gt_cols = st.sidebar.columns(2)
for i, gt in enumerate(["Regular Season", "Playoffs"]):
    with gt_cols[i]:
        btn_type = "primary" if st.session_state["selected_game_type"] == gt else "secondary"
        if st.button(gt, key=f"btn_gt_{gt}", type=btn_type, use_container_width=True):
            st.session_state["selected_game_type"] = gt
            st.rerun()

game_type_label = st.session_state["selected_game_type"]
game_type_code = "2" if game_type_label == "Regular Season" else "3"

# 3. Position Group Selection
st.sidebar.markdown('<div class="filter-label">Position Group</div>', unsafe_allow_html=True)
if "selected_pos_group" not in st.session_state:
    st.session_state["selected_pos_group"] = "All Skaters"

btn_type_all = "primary" if st.session_state["selected_pos_group"] == "All Skaters" else "secondary"
if st.sidebar.button("All Skaters", key="btn_pos_all", type=btn_type_all, use_container_width=True):
    st.session_state["selected_pos_group"] = "All Skaters"
    st.rerun()

pos_sub_cols = st.sidebar.columns(2)
with pos_sub_cols[0]:
    btn_type_f = "primary" if st.session_state["selected_pos_group"] == "Forwards" else "secondary"
    if st.button("Forwards", key="btn_pos_f", type=btn_type_f, use_container_width=True):
        st.session_state["selected_pos_group"] = "Forwards"
        st.rerun()

with pos_sub_cols[1]:
    btn_type_d = "primary" if st.session_state["selected_pos_group"] == "Defensemen" else "secondary"
    if st.button("Defensemen", key="btn_pos_d", type=btn_type_d, use_container_width=True):
        st.session_state["selected_pos_group"] = "Defensemen"
        st.rerun()

position_filter = st.session_state["selected_pos_group"]

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

        # Raw percentage decimals
        sh_pct = s.get("shootingPctg", 0.0)
        sh_pct = float(sh_pct) if sh_pct is not None else 0.0

        fo_pct = s.get("faceoffWinningPctg", 0.0)
        fo_pct = float(fo_pct) if fo_pct is not None else 0.0

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

        p60 = round((pts / total_toi_min) * 60, 4) if total_toi_min > 0 else 0.0
        sog60 = round((shots / total_toi_min) * 60, 4) if total_toi_min > 0 else 0.0
        pm60 = round((plus_minus / total_toi_min) * 60, 4) if total_toi_min > 0 else 0.0
        pim60 = round((pim / total_toi_min) * 60, 4) if total_toi_min > 0 else 0.0

        off_score = round(p60 + (sog60 * 0.25) + ((pp_goals / gp) * 1.5), 4) if gp > 0 else 0.0
        def_score = round((pm60 * 1.5) + (toi_gp_min * 0.1) + ((sh_goals / gp) * 2.0) - (pim60 * 0.2), 4) if gp > 0 else 0.0
        pp_score = round(((pp_goals / gp) * 3.0) + (sog60 * 0.1), 4) if gp > 0 else 0.0
        pk_score = round((toi_gp_min * 0.05) + ((sh_goals / gp) * 4.0) - (pim60 * 0.1), 4) if gp > 0 else 0.0

        player_id = s.get("playerId")
        first_name = s.get("firstName", {}).get("default", "")
        last_name = s.get("lastName", {}).get("default", "")

        rows.append({
            "PlayerId": player_id,
            "Photo": s.get("headshot", f"https://assets.nhle.com/mugs/nhl/latest/{player_id}.png"),
            "Skater": f"{first_name} {last_name}",
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
            "TOI/GP": round(toi_gp_min, 2),
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

with st.spinner("Loading NHL operations data..."):
    df = load_club_skater_stats(selected_season, game_type_code)

if not df.empty:
    if position_filter == "Forwards":
        df = df[df["Pos"].isin(["C", "L", "R", "F"])].reset_index(drop=True)
    elif position_filter == "Defensemen":
        df = df[df["Pos"] == "D"].reset_index(drop=True)

# --- Spotlight Header ---
if df.empty:
    st.info(f"No {game_type_label.lower()} data recorded for {st.session_state['selected_season_label']}.")
else:
    if "selected_player_id" not in st.session_state or st.session_state["selected_player_id"] not in df["PlayerId"].values:
        st.session_state["selected_player_id"] = int(df.iloc[0]["PlayerId"])

    p = df[df["PlayerId"] == st.session_state["selected_player_id"]].iloc[0]

    spotlight_html = f"""
    <div class="spotlight-card">
        <div style="display: flex; gap: 28px; align-items: center; flex-wrap: wrap;">
            <div style="flex-shrink: 0; text-align: center;">
                <img src="{p['Photo']}" style="width: 145px; height: 145px; object-fit: cover; border-radius: 50%; border: 2px solid #FFB81C; box-shadow: 0 6px 18px rgba(0,0,0,0.65);">
            </div>
            <div style="flex-grow: 1; min-width: 280px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <h2 class="spotlight-title">{p['Skater']}</h2>
                        <div>
                            <span class="badge">POS: {p['Pos']}</span>
                            <span class="badge">GP: {p['GP']}</span>
                            <span class="badge">TOI/GP: {p['TOI/GP']:.2f} MIN</span>
                            <span class="badge">SOG: {p['SOG']}</span>
                        </div>
                    </div>
                    <img src="{PREDS_LOGO_URL}" style="width: 60px; opacity: 0.9;" alt="Predators">
                </div>
                <div class="stat-pill-container">
                    <div class="stat-pill">
                        <div class="stat-pill-label">Scoring Production</div>
                        <div class="stat-pill-val">{p['PTS']} PTS</div>
                        <div class="stat-pill-sub">{p['G']}G, {p['A']}A</div>
                    </div>
                    <div class="stat-pill">
                        <div class="stat-pill-label">Rate Scoring (P/60)</div>
                        <div class="stat-pill-val">{p['P/60']:.4f}</div>
                        <div class="stat-pill-sub">{(p['SH%'] * 100):.2f}% Finishing</div>
                    </div>
                    <div class="stat-pill">
                        <div class="stat-pill-label">Offensive Score</div>
                        <div class="stat-pill-val">{p['Off_Score']:.4f}</div>
                        <div class="stat-pill-sub">{p['PPG']} Power Play G</div>
                    </div>
                    <div class="stat-pill">
                        <div class="stat-pill-label">Defensive Score</div>
                        <div class="stat-pill-val">{p['Def_Score']:.4f}</div>
                        <div class="stat-pill-sub">{p['+/-']:+d} Differential</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(spotlight_html, unsafe_allow_html=True)

    # --- Interactive Roster Selector Grid ---
    st.markdown("#### Roster Selection")
    num_cols = 6
    for i in range(0, len(df), num_cols):
        cols = st.columns(num_cols)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(df):
                skater = df.iloc[idx]
                with col:
                    with st.container(border=True):
                        st.image(skater["Photo"], use_container_width=True)
                        st.caption(f"**{skater['Skater']}** | {skater['Pos']}")
                        st.caption(f"{skater['PTS']} PTS ({skater['GP']} GP)")
                        if st.button("Select", key=f"btn_{skater['PlayerId']}", use_container_width=True):
                            st.session_state["selected_player_id"] = int(skater["PlayerId"])
                            st.rerun()

st.divider()

# --- Tabbed Analytical Views with Professional Column Configurations ---
st.subheader("Roster Performance & Advanced Indices")

if not df.empty:
    qualified_df = df[df["GP"] >= 5].reset_index(drop=True)
    limited_df = df[df["GP"] < 5].reset_index(drop=True)

    if "active_tab_view" not in st.session_state:
        st.session_state["active_tab_view"] = "Offensive Impact"

    tabs = [
        "Offensive Impact", 
        "Defensive Impact", 
        "Special Teams Performance", 
        "Complete Skater Statistics",
        "Limited Sample (< 5 GP)"
    ]

    nav_cols = st.columns(5)
    for idx, tab_name in enumerate(tabs):
        with nav_cols[idx]:
            btn_type = "primary" if st.session_state["active_tab_view"] == tab_name else "secondary"
            if st.button(tab_name, key=f"nav_btn_{idx}", type=btn_type, use_container_width=True):
                st.session_state["active_tab_view"] = tab_name
                st.rerun()

    active_view = st.session_state["active_tab_view"]

    base_column_config = {
        "Photo": st.column_config.ImageColumn("", width="small"),
        "Skater": st.column_config.TextColumn("Player", width="medium"),
        "Pos": st.column_config.TextColumn("Pos", width="small"),
        "GP": st.column_config.NumberColumn("GP", format="%d"),
        "PTS": st.column_config.NumberColumn("PTS", format="%d"),
        "G": st.column_config.NumberColumn("G", format="%d"),
        "A": st.column_config.NumberColumn("A", format="%d"),
        "SOG": st.column_config.NumberColumn("SOG", format="%d"),
        "+/-": st.column_config.NumberColumn("+/-", format="%+d"),
        "PIM": st.column_config.NumberColumn("PIM", format="%d"),
        "TOI/GP": st.column_config.NumberColumn("TOI/GP", format="%.2f m"),
        "SH%": st.column_config.ProgressColumn("SH%", min_value=0.0, max_value=0.35, format="%.1f%%"),
        "FO%": st.column_config.ProgressColumn("FO%", min_value=0.0, max_value=0.75, format="%.1f%%"),
        "P/60": st.column_config.ProgressColumn("P/60", min_value=0.0, max_value=float(df["P/60"].max() or 4.0), format="%.2f"),
        "Off_Score": st.column_config.ProgressColumn("Offensive Impact", min_value=0.0, max_value=float(df["Off_Score"].max() or 6.0), format="%.2f"),
        "Def_Score": st.column_config.ProgressColumn("Defensive Impact", min_value=float(df["Def_Score"].min() or -3.0), max_value=float(df["Def_Score"].max() or 5.0), format="%.2f"),
        "PP_Score": st.column_config.ProgressColumn("PP Impact", min_value=0.0, max_value=float(df["PP_Score"].max() or 5.0), format="%.2f"),
        "PK_Score": st.column_config.ProgressColumn("PK Impact", min_value=0.0, max_value=float(df["PK_Score"].max() or 4.0), format="%.2f"),
    }

    if active_view == "Offensive Impact":
        st.markdown("**Ranked by Offensive Impact:**")
        cols = ["Photo", "Skater", "Pos", "GP", "Off_Score", "P/60", "SOG/60", "PTS", "G", "A", "SOG", "SH%", "PPG", "GWG"]
        off_view = qualified_df[cols].sort_values(by="Off_Score", ascending=False).reset_index(drop=True)
        st.dataframe(off_view, column_config=base_column_config, use_container_width=True, hide_index=True)

    elif active_view == "Defensive Impact":
        st.markdown("**Ranked by Defensive Impact:**")
        cols = ["Photo", "Skater", "Pos", "GP", "Def_Score", "+/- /60", "TOI/GP", "+/-", "PIM", "SHG", "FO%"]
        def_view = qualified_df[cols].sort_values(by="Def_Score", ascending=False).reset_index(drop=True)
        st.dataframe(def_view, column_config=base_column_config, use_container_width=True, hide_index=True)

    elif active_view == "Special Teams Performance":
        st.markdown("**Ranked by Special Teams Impact:**")
        cols = ["Photo", "Skater", "Pos", "GP", "PP_Score", "PK_Score", "PPG", "SHG", "PIM", "TOI/GP"]
        st_view = qualified_df[cols].sort_values(by="PP_Score", ascending=False).reset_index(drop=True)
        st.dataframe(st_view, column_config=base_column_config, use_container_width=True, hide_index=True)

    elif active_view == "Complete Skater Statistics":
        st.markdown("**Complete Skater Statistics:**")
        cols = [
            "Photo", "Skater", "Pos", "GP", "Off_Score", "Def_Score", "PP_Score", "PK_Score",
            "PTS", "G", "A", "+/-", "P/60", "TOI/GP", "SOG", "SH%", "PIM", 
            "PPG", "SHG", "GWG", "FO%"
        ]
        comp_view = qualified_df[cols].sort_values(by="PTS", ascending=False).reset_index(drop=True)
        st.dataframe(comp_view, column_config=base_column_config, use_container_width=True, hide_index=True)

    elif active_view == "Limited Sample (< 5 GP)":
        st.markdown("**Limited Sample Size Skaters (< 5 Games Played):**")
        st.caption("Rates and composite impact models are unweighted due to low minute exposure.")
        if limited_df.empty:
            st.info("No skaters currently have fewer than 5 games played for this selection.")
        else:
            cols = [
                "Photo", "Skater", "Pos", "GP", "PTS", "G", "A", "+/-", 
                "TOI/GP", "SOG", "SH%", "PIM", "P/60", "Off_Score", "Def_Score"
            ]
            lim_view = limited_df[cols].sort_values(by="GP", ascending=False).reset_index(drop=True)
            st.dataframe(lim_view, column_config=base_column_config, use_container_width=True, hide_index=True)
