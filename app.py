import streamlit as st
import pandas as pd
import requests

PREDS_LOGO_URL = "https://assets.nhle.com/logos/nhl/svg/NSH_light.svg"

# Mapping team tricots to official NHL SVG logo URLs for the trade table
TEAM_LOGOS = {
    "PIT": "https://assets.nhle.com/logos/nhl/svg/PIT_light.svg",
    "SJS": "https://assets.nhle.com/logos/nhl/svg/SJS_light.svg",
    "ANA": "https://assets.nhle.com/logos/nhl/svg/ANA_light.svg",
    "SEA": "https://assets.nhle.com/logos/nhl/svg/SEA_light.svg",
    "PHI": "https://assets.nhle.com/logos/nhl/svg/PHI_light.svg",
    "MTL": "https://assets.nhle.com/logos/nhl/svg/MTL_light.svg"
}

st.set_page_config(
    page_title="Nashville Predators Hockey Operations Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Deep franchise theme injection
st.markdown(f"""
<style>
    html, body, [data-testid="stAppViewContainer"], .stApp {{
        background-color: #041E42 !important;
        color: #F8FAFC !important;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif !important;
    }}
    
    [data-testid="stHeader"] {{
        background-color: rgba(4, 30, 66, 0.95) !important;
    }}

    [data-testid="stSidebar"], [data-testid="stSidebarContent"] {{
        background-color: #03142D !important;
        border-right: 1.5px solid rgba(255, 184, 28, 0.3) !important;
    }}
    [data-testid="stSidebar"] * {{
        color: #F8FAFC !important;
    }}

    .block-container {{
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 95% !important;
    }}

    /* Permanent Sidebar Toggle Button */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapseButton"] button,
    [data-testid="collapsedControl"],
    [data-testid="collapsedControl"] button {{
        opacity: 1 !important;
        visibility: visible !important;
        display: flex !important;
    }}

    [data-testid="stSidebarCollapseButton"] button,
    [data-testid="collapsedControl"] button {{
        background-color: #061F47 !important;
        border: 2px solid #FFB81C !important;
        border-radius: 8px !important;
        padding: 4px 8px !important;
        box-shadow: 0 0 10px rgba(255, 184, 28, 0.4) !important;
        transition: all 0.2s ease-in-out !important;
    }}

    [data-testid="stSidebarCollapseButton"] button:hover,
    [data-testid="collapsedControl"] button:hover {{
        background-color: #FFB81C !important;
        box-shadow: 0 0 16px rgba(255, 184, 28, 0.7) !important;
        transform: scale(1.05);
    }}

    [data-testid="stSidebarCollapseButton"] svg,
    [data-testid="stSidebarCollapseButton"] svg *,
    [data-testid="collapsedControl"] svg,
    [data-testid="collapsedControl"] svg * {{
        opacity: 1 !important;
        visibility: visible !important;
        fill: #FFB81C !important;
        stroke: #FFB81C !important;
        color: #FFB81C !important;
    }}

    [data-testid="stSidebarCollapseButton"] button:hover svg,
    [data-testid="stSidebarCollapseButton"] button:hover svg *,
    [data-testid="collapsedControl"] button:hover svg,
    [data-testid="collapsedControl"] button:hover svg * {{
        fill: #041E42 !important;
        stroke: #041E42 !important;
        color: #041E42 !important;
    }}

    .header-container {{
        display: flex;
        align-items: center;
        gap: 22px;
        margin-bottom: 24px;
        border-bottom: 2px solid #FFB81C;
        padding-bottom: 18px;
    }}
    .header-logo {{
        width: 85px;
        height: auto;
        object-fit: contain;
    }}
    .header-title-box h1 {{
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
        color: #FFFFFF !important;
    }}
    .header-subtitle {{
        font-size: 0.95rem;
        color: #FFB81C !important;
        margin-top: 5px;
        font-weight: 600;
        letter-spacing: 0.3px;
    }}

    /* Financial Metrics Banner */
    .cap-strip {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 20px;
    }}
    .cap-cell {{
        background: linear-gradient(135deg, #092652 0%, #03142D 100%);
        border: 1.5px solid rgba(255, 184, 28, 0.4);
        border-radius: 10px;
        padding: 14px 18px;
        text-align: left;
    }}
    .cap-cell-label {{
        font-size: 0.72rem;
        color: #94A3B8;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .cap-cell-value {{
        font-size: 1.6rem;
        font-weight: 800;
        color: #FFB81C;
        margin-top: 4px;
    }}
    .cap-cell-sub {{
        font-size: 0.75rem;
        color: #E2E8F0;
        margin-top: 2px;
        font-weight: 600;
    }}

    /* Spotlight Card */
    .spotlight-card {{
        background: linear-gradient(135deg, #092652 0%, #03142D 100%);
        border: 2px solid #FFB81C;
        border-radius: 12px;
        padding: 24px 30px;
        box-shadow: 0 10px 28px rgba(0, 0, 0, 0.65);
        margin-bottom: 28px;
        color: #FFFFFF;
    }}
    .spotlight-title {{
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        color: #FFB81C !important;
        letter-spacing: -0.5px;
    }}
    .badge {{
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
    }}
    .stat-pill-container {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 14px;
        margin-top: 12px;
    }}
    .stat-pill {{
        background: #04142B;
        border: 1px solid rgba(255, 184, 28, 0.3);
        border-radius: 8px;
        padding: 12px 16px;
        text-align: left;
    }}
    .stat-pill-label {{
        font-size: 0.7rem;
        text-transform: uppercase;
        color: #94A3B8 !important;
        font-weight: 700;
        letter-spacing: 0.6px;
    }}
    .stat-pill-val {{
        font-size: 1.4rem;
        font-weight: 800;
        color: #FFFFFF !important;
        margin-top: 3px;
    }}
    .stat-pill-sub {{
        font-size: 0.75rem;
        color: #FFB81C !important;
        margin-top: 3px;
        font-weight: 600;
    }}

    /* NHL Line Card */
    .nhl-player-card {{
        background: linear-gradient(180deg, #092652 0%, #03142D 100%);
        border: 1.5px solid rgba(255, 184, 28, 0.4);
        border-radius: 10px;
        padding: 14px 12px;
        text-align: center;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.45);
        transition: transform 0.2s ease, border-color 0.2s ease;
        margin-bottom: 12px;
    }}
    .nhl-player-card:hover {{
        transform: translateY(-2px);
        border-color: #FFB81C;
        box-shadow: 0 6px 18px rgba(255, 184, 28, 0.35);
    }}
    .nhl-mug {{
        width: 86px;
        height: 86px;
        object-fit: cover;
        border-radius: 50%;
        border: 2px solid #FFB81C;
        margin: 0 auto 8px auto;
        display: block;
        background-color: #04142B;
    }}
    .nhl-num-pos {{
        font-size: 0.78rem;
        font-weight: 800;
        color: #FFB81C;
        letter-spacing: 0.5px;
    }}
    .nhl-name {{
        font-size: 1.05rem;
        font-weight: 800;
        color: #FFFFFF;
        margin: 2px 0 2px 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    .nhl-cap-line {{
        font-size: 0.78rem;
        color: #38BDF8;
        font-weight: 800;
        margin-bottom: 3px;
    }}
    .nhl-tag {{
        font-size: 0.72rem;
        color: #94A3B8;
        font-weight: 600;
    }}

    .line-header-banner {{
        background-color: #061F47;
        border-left: 4px solid #FFB81C;
        padding: 8px 14px;
        font-size: 1.05rem;
        font-weight: 800;
        color: #FFFFFF;
        margin-top: 14px;
        margin-bottom: 10px;
        letter-spacing: 0.3px;
        border-radius: 4px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .line-cap-total {{
        font-size: 0.82rem;
        color: #FFB81C;
        font-weight: 700;
    }}

    div[data-testid="stButton"] button[kind="secondary"] {{
        background-color: #061F47 !important;
        border: 2px solid #FFB81C !important;
        border-radius: 10px !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        padding: 8px 16px !important;
    }}
    div[data-testid="stButton"] button[kind="primary"] {{
        background-color: #FFB81C !important;
        border: 2px solid #FFB81C !important;
        border-radius: 10px !important;
        color: #041E42 !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
        padding: 8px 16px !important;
    }}

    .filter-label {{
        font-size: 0.92rem;
        font-weight: 700;
        color: #FFB81C;
        margin-top: 14px;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    [data-testid="stDataFrame"] {{
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(255, 184, 28, 0.3);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.55);
    }}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="header-container">
    <img src="{PREDS_LOGO_URL}" class="header-logo" alt="Nashville Predators">
    <div class="header-title-box">
        <h1>Nashville Predators | Hockey Operations & Cap Management</h1>
        <div class="header-subtitle">Executive Roster Modeling, 26/27 Cap Ledger & Real-Time Trade Deadline Target Intelligence</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Top Navigation in Sidebar
st.sidebar.markdown("### Operations Portal")
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Skater Analytics"

p_cols = st.sidebar.columns(3)
with p_cols[0]:
    btn_p1 = "primary" if st.session_state["current_page"] == "Skater Analytics" else "secondary"
    if st.button("Skater Hub", key="btn_nav_skaters", type=btn_p1, use_container_width=True):
        st.session_state["current_page"] = "Skater Analytics"
        st.rerun()

with p_cols[1]:
    btn_p2 = "primary" if st.session_state["current_page"] == "Line Combinations" else "secondary"
    if st.button("26/27 Lines", key="btn_nav_lines", type=btn_p2, use_container_width=True):
        st.session_state["current_page"] = "Line Combinations"
        st.rerun()

with p_cols[2]:
    btn_p3 = "primary" if st.session_state["current_page"] == "Trade Intelligence" else "secondary"
    if st.button("Target Ops", key="btn_nav_trades", type=btn_p3, use_container_width=True):
        st.session_state["current_page"] = "Trade Intelligence"
        st.rerun()

current_page = st.session_state["current_page"]

# ==============================================================================
# VERIFIED HEADSHOT OVERRIDES
# ==============================================================================
VERIFIED_MANUAL_HEADSHOTS = {
    "Steven Stamkos": "https://assets.nhle.com/mugs/nhl/latest/8474564.png",
    "Jonathan Marchessault": "https://assets.nhle.com/mugs/nhl/latest/8476539.png",
    "Roman Josi": "https://assets.nhle.com/mugs/nhl/latest/8474600.png",
    "Matthew Wood": "https://assets.nhle.com/mugs/nhl/latest/8484241.png",
    "Bryan Rust": "https://assets.nhle.com/mugs/nhl/latest/8475848.png",
    "Rickard Rakell": "https://assets.nhle.com/mugs/nhl/latest/8476460.png",
    "Mikael Granlund": "https://assets.nhle.com/mugs/nhl/latest/8475794.png",
    "Will Borgen": "https://assets.nhle.com/mugs/nhl/latest/8479379.png",
    "Noel Acciari": "https://assets.nhle.com/mugs/nhl/latest/8478496.png",
    "Joel Armia": "https://assets.nhle.com/mugs/nhl/latest/8476346.png"
}

@st.cache_data(ttl=86400)
def resolve_player_headshot(player_name, fallback_id=None):
    if player_name in VERIFIED_MANUAL_HEADSHOTS:
        return VERIFIED_MANUAL_HEADSHOTS[player_name]
    try:
        search_query = player_name.replace(" ", "%20")
        url = f"https://search.d3.nhle.com/api/v1/search/player?culture=en-us&limit=3&q={search_query}"
        res = requests.get(url, timeout=4)
        if res.status_code == 200:
            hits = res.json()
            if hits:
                p_id = hits[0].get("playerId")
                if p_id:
                    landing_res = requests.get(f"https://api-web.nhle.com/v1/player/{p_id}/landing", timeout=4)
                    if landing_res.status_code == 200:
                        headshot = landing_res.json().get("headshot")
                        if headshot:
                            return headshot
                    return f"https://assets.nhle.com/mugs/nhl/latest/{p_id}.png"
    except Exception:
        pass
    if fallback_id:
        return f"https://assets.nhle.com/mugs/nhl/latest/{fallback_id}.png"
    return PREDS_LOGO_URL

# ==============================================================================
# PAGE 1: 26/27 LINE COMBINATIONS (WITH SALARY CAP LINES)
# ==============================================================================
if current_page == "Line Combinations":
    st.subheader("26/27 Projected Line Combinations & Salary Distribution")
    st.caption("Tactical Alignment: Andrew Brunette 1-2-2 High-Pace Forecheck | Official Cap Ceiling: $104.0M")

    # Financial Ledger Strip
    st.markdown("""
    <div class="cap-strip">
        <div class="cap-cell">
            <div class="cap-cell-label">Cap Ceiling (26/27)</div>
            <div class="cap-cell-value">$104.00M</div>
            <div class="cap-cell-sub">NHL Official Upper Limit</div>
        </div>
        <div class="cap-cell">
            <div class="cap-cell-label">Active 20-Man Cap Hit</div>
            <div class="cap-cell-value">$95.25M</div>
            <div class="cap-cell-sub">Roster Cap Obligation</div>
        </div>
        <div class="cap-cell">
            <div class="cap-cell-label">Accrued Cap Space</div>
            <div class="cap-cell-value">$8.75M</div>
            <div class="cap-cell-sub">Current Free Cap Space</div>
        </div>
        <div class="cap-cell">
            <div class="cap-cell-label">Deadline Purchasing Power</div>
            <div class="cap-cell-value">~$20.4M</div>
            <div class="cap-cell-sub">Pro-Rated Day-of-Deadline Cap</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    def render_nhl_player_cap(col, num, name, pos, role_tag, fallback_id, aav_text, status_text):
        headshot_url = resolve_player_headshot(name, fallback_id)
        col.markdown(f"""
        <div class="nhl-player-card">
            <img class="nhl-mug" src="{headshot_url}" alt="{name}" onerror="this.onerror=null; this.src='{PREDS_LOGO_URL}';">
            <div class="nhl-num-pos">#{num} • {pos}</div>
            <div class="nhl-name">{name}</div>
            <div class="nhl-cap-line">{aav_text} <span style="font-weight: 500; font-size: 0.72rem; color: #CBD5E1;">({status_text})</span></div>
            <div class="nhl-tag">{role_tag}</div>
        </div>
        """, unsafe_allow_html=True)

    # Forward Line 1
    st.markdown('<div class="line-header-banner"><span>FORWARD LINE 1 | MATCHUP & HEAVY CYCLE</span><span class="line-cap-total">Line Cap: $18.50M</span></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    render_nhl_player_cap(c1, 9, "Filip Forsberg", "LW", "Sniper / Cycle Touch", 8476887, "$8.50M", "UFA '30")
    render_nhl_player_cap(c2, 90, "Ryan O'Reilly", "C", "200-Ft Anchor / Ozone Draws", 8475158, "$4.50M", "UFA '27")
    render_nhl_player_cap(c3, 81, "Jonathan Marchessault", "RW", "Perimeter Release / Boards", 8476539, "$5.50M", "UFA '29")

    # Forward Line 2
    st.markdown('<div class="line-header-banner"><span>FORWARD LINE 2 | RUSH STRIKE & HIGH-SLOT FINISHING</span><span class="line-cap-total">Line Cap: $12.35M</span></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    render_nhl_player_cap(c1, 91, "Steven Stamkos", "LW", "High-Slot One-Timer", 8474564, "$8.00M", "UFA '28")
    render_nhl_player_cap(c2, 22, "Mavrik Bourque", "C", "Pace Playmaker / Distributor", 8482142, "$3.40M", "RFA '29")
    render_nhl_player_cap(c3, 71, "Matthew Wood", "RW", "Power Forward / Net-Front", 8484241, "$0.95M", "ELC '28")

    # Forward Line 3
    st.markdown('<div class="line-header-banner"><span>FORWARD LINE 3 | RELENTLESS F1/F2 FORECHECK & TURNOVER CREATION</span><span class="line-cap-total">Line Cap: $9.85M</span></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    render_nhl_player_cap(c1, 79, "Ross Colton", "LW", "Puck-Hound / Physical Pressure", 8479525, "$4.00M", "UFA '27")
    render_nhl_player_cap(c2, 18, "Jack Drury", "C", "Neutral-Zone Transition Detail", 8480835, "$2.85M", "UFA '28")
    render_nhl_player_cap(c3, 21, "Nils Hoglander", "RW", "5v5 Motor / Cycle Finisher", 8481535, "$3.00M", "UFA '28")

    # Forward Line 4
    st.markdown('<div class="line-header-banner"><span>FORWARD LINE 4 | TRANSITION PACE & DEFENSIVE IQ</span><span class="line-cap-total">Line Cap: $4.90M</span></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    render_nhl_player_cap(c1, 14, "Alexander Kerfoot", "LW", "Two-Way Versatility", 8477021, "$3.00M", "UFA '27")
    render_nhl_player_cap(c2, 51, "Vitali Pinchuk", "C", "6'3\" Transition Frame", 8486189, "$0.95M", "ELC '28")
    render_nhl_player_cap(c3, 89, "Ozzy Wiesblatt", "RW", "North-South Energy / Agitator", 8482103, "$0.95M", "RFA '27")

    # Defensive Pairing 1
    st.markdown('<div class="line-header-banner"><span>DEFENSIVE PAIRING 1 | ELITE DUAL-THREAT TRANSITION</span><span class="line-cap-total">Pair Cap: $14.05M</span></div>', unsafe_allow_html=True)
    d1, d2 = st.columns(2)
    render_nhl_player_cap(d1, 41, "Nicolas Hague", "LD", "6'6\" Physical Anchor / Box-Outs", 8480051, "$5.00M", "UFA '29")
    render_nhl_player_cap(d2, 58, "Roman Josi", "RD", "Weak-Side Activation / Rush Rover", 8474600, "$9.05M", "UFA '28")

    # Defensive Pairing 2
    st.markdown('<div class="line-header-banner"><span>DEFENSIVE PAIRING 2 | TWO-WAY RUSH SUPPRESSION</span><span class="line-cap-total">Pair Cap: $9.82M</span></div>', unsafe_allow_html=True)
    d1, d2 = st.columns(2)
    render_nhl_player_cap(d1, 76, "Brady Skjei", "LD", "Exit Skating / Mobility", 8476869, "$7.00M", "UFA '31")
    render_nhl_player_cap(d2, 48, "Nick Perbix", "RD", "Puck Retrieval / Safe Breakout", 8480249, "$2.82M", "UFA '27")

    # Defensive Pairing 3
    st.markdown('<div class="line-header-banner"><span>DEFENSIVE PAIRING 3 | MOBILITY & CREASE PROTECTION</span><span class="line-cap-total">Pair Cap: $4.55M</span></div>', unsafe_allow_html=True)
    d1, d2 = st.columns(2)
    render_nhl_player_cap(d1, 83, "Adam Wilsby", "LD", "Puck-Moving Transition Skater", 8482482, "$1.30M", "RFA '28")
    render_nhl_player_cap(d2, 46, "Ilya Lyubushkin", "RD", "Physical Net-Front Suppression", 8480950, "$3.25M", "UFA '27")

    # Goaltending Tandem
    st.markdown('<div class="line-header-banner"><span>GOALTENDING TANDEM</span><span class="line-cap-total">Tandem Cap: $10.23M</span></div>', unsafe_allow_html=True)
    g1, g2 = st.columns(2)
    render_nhl_player_cap(g1, 74, "Juuse Saros", "G", "Starting Goaltender (Franchise Anchor)", 8477424, "$7.74M", "UFA '33")
    render_nhl_player_cap(g2, 29, "Justus Annunen", "G", "Backup Goaltender (High-End Tandem)", 8481020, "$2.49M", "RFA '28")

    st.stop()

# ==============================================================================
# PAGE 2: TRADE DEADLINE & REALISTIC BUY TARGET INTELLIGENCE (CARD GRID)
# ==============================================================================
if current_page == "Trade Intelligence":
    st.subheader("NHL Trade Deadline: Realistic Acquisition Targets & Cap Strategy")
    st.caption("Active evaluations of available top-six wingers and shutdown depth pieces carrying zero trade protection clauses (NMC/NTC-free).")

    # VETTED ACQUISITION TARGETS DATABASE
    realistic_targets = [
        {
            "Photo": resolve_player_headshot("Bryan Rust"),
            "Player": "Bryan Rust", 
            "Team_Logo": TEAM_LOGOS["PIT"],
            "Team": "PIT", 
            "Pos": "RW",
            "Cap_Hit": 5.125, 
            "Status": "Signed thru '28 (Trade Block)",
            "Category": "Top-Six Forward", 
            "Deadline_Posture": "🟢 Top BUY Target",
            "Brunette_Fit": 95, 
            "Archetype": "Proven Playoff Top-Line Winger / Relentless Motor",
            "Tactical_Scouting": "Two-time Stanley Cup champion actively made available as Pittsburgh cycles through a multi-year retool. World-class forechecking speed and high-compete board work that fits Andrew Brunette's system seamlessly."
        },
        {
            "Photo": resolve_player_headshot("Rickard Rakell"),
            "Player": "Rickard Rakell", 
            "Team_Logo": TEAM_LOGOS["PIT"],
            "Team": "PIT", 
            "Pos": "RW",
            "Cap_Hit": 5.00, 
            "Status": "Pending UFA '28 (No NMC)",
            "Category": "Top-Six Forward", 
            "Deadline_Posture": "🟢 BUY Target",
            "Brunette_Fit": 92, 
            "Archetype": "High-Volume Release / Skill Finisher",
            "Tactical_Scouting": "Perennial trade-block fixture on a non-contending Penguins roster with full trade maneuverability. Generates rapid rush shots that take pressure off Steven Stamkos."
        },
        {
            "Photo": resolve_player_headshot("Mikael Granlund"),
            "Player": "Mikael Granlund", 
            "Team_Logo": TEAM_LOGOS["ANA"],
            "Team": "ANA", 
            "Pos": "C",
            "Cap_Hit": 7.00, 
            "Status": "Signed thru '28",
            "Category": "Top-Six Forward", 
            "Deadline_Posture": "🔵 Secondary Scorer",
            "Brunette_Fit": 93, 
            "Archetype": "High-IQ Playmaker / Power Play Distributor",
            "Tactical_Scouting": "Smart veteran distributor with extensive familiarity with Nashville hockey ops. High-end vision to quarterback secondary power-play units and stabilize middle-six minutes."
        },
        {
            "Photo": resolve_player_headshot("Will Borgen"),
            "Player": "Will Borgen", 
            "Team_Logo": TEAM_LOGOS["SEA"],
            "Team": "SEA", 
            "Pos": "RD",
            "Cap_Hit": 2.70, 
            "Status": "Pending UFA '27 (No NMC)",
            "Category": "Top-4 Defensive Upgrade", 
            "Deadline_Posture": "🟡 Value BUY",
            "Brunette_Fit": 91, 
            "Archetype": "Heavy Physical Shutdown RD / Clean Exit",
            "Tactical_Scouting": "Under-the-radar right defenseman who suppresses neutral-zone rush entries at a top-tier rate. Highly cost-effective upgrade with complete roster flexibility."
        },
        {
            "Photo": resolve_player_headshot("Noel Acciari"),
            "Player": "Noel Acciari", 
            "Team_Logo": TEAM_LOGOS["PHI"],
            "Team": "PHI", 
            "Pos": "C",
            "Cap_Hit": 1.40, 
            "Status": "Signed thru '28",
            "Category": "Bottom-Six / PK Depth", 
            "Deadline_Posture": "🟡 Depth Grinder",
            "Brunette_Fit": 94, 
            "Archetype": "Hard-Nosed Playoff Wall / PK Shot Blocker",
            "Tactical_Scouting": "Fearless checking center who wins key defensive-zone draws, blocks point shots, and brings heavy physical identity to a bottom-six checking role."
        },
        {
            "Photo": resolve_player_headshot("Joel Armia"),
            "Player": "Joel Armia", 
            "Team_Logo": TEAM_LOGOS["MTL"],
            "Team": "MTL", 
            "Pos": "RW",
            "Cap_Hit": 3.40, 
            "Status": "Expiring Contract (No NMC)",
            "Category": "Bottom-Six / PK Depth", 
            "Deadline_Posture": "🔵 PK Specialist BUY",
            "Brunette_Fit": 89, 
            "Archetype": "6'3\" Low-Cycle Puck Protector / Short-Handed Weapon",
            "Tactical_Scouting": "Elite takeaway winger who uses his large frame to dominate board battles. High-impact addition for late-game defensive leads and penalty killing without contract blocks."
        }
    ]

    target_df = pd.DataFrame(realistic_targets)

    # Interactive Filtering Controls
    f_cols = st.columns([1.2, 1.2, 1.2, 1.4])
    with f_cols[0]:
        cat_opts = ["All Categories", "Top-Six Forward", "Top-4 Defensive Upgrade", "Bottom-Six / PK Depth"]
        sel_cat = st.selectbox("Target Category", cat_opts)
    with f_cols[1]:
        pos_opts = ["All Positions", "Centers (C)", "Wingers (RW/LW)", "Defensemen (RD/LD)"]
        sel_pos = st.selectbox("Position", pos_opts)
    with f_cols[2]:
        strat_opts = ["All Postures", "BUY Target", "Secondary Scorer", "Value BUY", "Depth Grinder", "PK Specialist BUY"]
        sel_strat = st.selectbox("Deadline Posture", strat_opts)
    with f_cols[3]:
        min_fit = st.slider("Min Brunette Scheme Fit", min_value=85, max_value=96, value=88)

    # Filter Application
    filtered_df = target_df[target_df["Brunette_Fit"] >= min_fit].copy()

    if sel_cat != "All Categories":
        filtered_df = filtered_df[filtered_df["Category"] == sel_cat]

    if sel_pos == "Centers (C)":
        filtered_df = filtered_df[filtered_df["Pos"].str.contains("C")]
    elif sel_pos == "Wingers (RW/LW)":
        filtered_df = filtered_df[filtered_df["Pos"].str.contains("LW|RW")]
    elif sel_pos == "Defensemen (RD/LD)":
        filtered_df = filtered_df[filtered_df["Pos"].str.contains("D")]

    if sel_strat != "All Postures":
        filtered_df = filtered_df[filtered_df["Deadline_Posture"].str.contains(sel_strat.split()[-1])]

    st.markdown("#### Real-Time Acquisition Target Registry (NMC-Free)")
    
    # Render targets as an executive card grid with direct image rendering
    for i, row in filtered_df.iterrows():
        with st.container(border=True):
            c1, c2, c3 = st.columns([1.2, 3.5, 5])
            with c1:
                st.image(row["Photo"], width=80)
                st.image(row["Team_Logo"], width=32)
            with c2:
                st.markdown(f"### **{row['Player']}** ({row['Pos']})")
                st.caption(f"**Tier:** {row['Category']} | **Cap Hit:** ${row['Cap_Hit']:.3f}M")
                st.markdown(f"**Action:** {row['Deadline_Posture']}")
                st.markdown(f"**Scheme Fit:** {row['Brunette_Fit']}/100")
            with c3:
                st.markdown(f"**Archetype:** `{row['Archetype']}`")
                st.info(f"**Tactical Evaluation:** {row['Tactical_Scouting']}")

    st.stop()

# ==============================================================================
# PAGE 3: SKATER ANALYTICS & PERFORMANCE HUB
# ==============================================================================

st.sidebar.markdown("### Filter Settings")

# 1. Season Selection
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

KNOWN_D_HANDEDNESS = {
    8474600: "L", 8475172: "R", 8475222: "L", 8476869: "L", 8478469: "L",
    8479323: "R", 8479410: "R", 8476885: "R", 8482079: "L", 8481541: "R",
    8483488: "L", 8484153: "R", 8480950: "R", 8480051: "L", 8480249: "R", 8482482: "L"
}

@st.cache_data(ttl=86400)
def load_roster_handedness(season):
    shoots_map = KNOWN_D_HANDEDNESS.copy()
    for s_param in [season, "current"]:
        url = f"{BASE_URL}/roster/{TEAM_TRICODE}/{s_param}"
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                data = res.json()
                for group in ["defensemen", "forwards"]:
                    for player in data.get(group, []):
                        p_id = player.get("id")
                        shoots = player.get("shootsCatches")
                        if p_id and shoots:
                            shoots_map[p_id] = shoots
        except Exception:
            pass
    return shoots_map

@st.cache_data(ttl=1800)
def load_zone_faceoffs(season, game_type):
    zone_dict = {}
    urls = [
        f"https://api.nhle.com/stats/rest/en/skater/faceoffpercentages?isAggregate=false&isGame=false&limit=100&sort=%5B%7B%22property%22:%22totalFaceoffs%22,%22direction%22:%22DESC%22%7D%5D&cayenneExp=seasonId={season}%20and%20gameTypeId={game_type}%20and%20franchiseId=34",
        f"https://api.nhle.com/stats/rest/en/skater/faceoffpercentages?isAggregate=false&isGame=false&limit=100&sort=%5B%7B%22property%22:%22totalFaceoffs%22,%22direction%22:%22DESC%22%7D%5D&cayenneExp=seasonId={season}%20and%20gameTypeId={game_type}%20and%20teamId=18",
    ]
    for url in urls:
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                data = res.json().get("data", [])
                if data:
                    for row in data:
                        p_id = row.get("playerId")
                        tot_fo = row.get("totalFaceoffs", 0)
                        if tot_fo and tot_fo > 0:
                            zone_dict[p_id] = {
                                "Total_FO": int(tot_fo),
                                "FO%": round(float(row.get("faceoffWinPct")) * 100.0, 1) if row.get("faceoffWinPct") is not None else None,
                                "OZ_FO%": round(float(row.get("offensiveZoneFaceoffPct")) * 100.0, 1) if row.get("offensiveZoneFaceoffPct") is not None else None,
                                "NZ_FO%": round(float(row.get("neutralZoneFaceoffPct")) * 100.0, 1) if row.get("neutralZoneFaceoffPct") is not None else None,
                                "DZ_FO%": round(float(row.get("defensiveZoneFaceoffPct")) * 100.0, 1) if row.get("defensiveZoneFaceoffPct") is not None else None,
                            }
                    if len(zone_dict) > 0:
                        break
        except Exception:
            continue
    return zone_dict

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

    shoots_map = load_roster_handedness(season)
    zone_map = load_zone_faceoffs(season, game_type)

    rows = []
    for s in skaters:
        player_id = s.get("playerId")
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

        raw_sh = s.get("shootingPctg") or s.get("shootingPct") or 0.0
        sh_pct = round(float(raw_sh) * 100.0, 1) if raw_sh is not None else 0.0

        z_stats = zone_map.get(player_id, {})
        tot_fo = z_stats.get("Total_FO", 0)
        fo_pct = z_stats.get("FO%")
        oz_fo = z_stats.get("OZ_FO%")
        nz_fo = z_stats.get("NZ_FO%")
        dz_fo = z_stats.get("DZ_FO%")

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

        raw_pos = s.get("positionCode", "N/A")
        shoots = shoots_map.get(player_id)

        if raw_pos == "D" and not shoots:
            try:
                p_res = requests.get(f"{BASE_URL}/player/{player_id}/landing", timeout=2)
                if p_res.status_code == 200:
                    shoots = p_res.json().get("shootsCatches", "")
                    shoots_map[player_id] = shoots
            except Exception:
                pass

        if raw_pos == "L":
            pos_code = "LW"
        elif raw_pos == "R":
            pos_code = "RW"
        elif raw_pos == "D":
            pos_code = f"{shoots}D" if shoots in ["L", "R"] else "LD"
        else:
            pos_code = raw_pos

        first_name = s.get("firstName", {}).get("default", "")
        last_name = s.get("lastName", {}).get("default", "")

        rows.append({
            "PlayerId": player_id,
            "Photo": s.get("headshot", f"https://assets.nhle.com/mugs/nhl/latest/{player_id}.png"),
            "Skater": f"{first_name} {last_name}",
            "Pos": pos_code,
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
            "Total_FO": int(tot_fo),
            "FO%": fo_pct,
            "OZ_FO%": oz_fo,
            "NZ_FO%": nz_fo,
            "DZ_FO%": dz_fo,
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
        df = df[df["Pos"].isin(["C", "LW", "RW", "F"])].reset_index(drop=True)
    elif position_filter == "Defensemen":
        df = df[df["Pos"].isin(["D", "LD", "RD"])].reset_index(drop=True)

# Spotlight Header
if df.empty:
    st.info(f"No {game_type_label.lower()} data recorded for {st.session_state['selected_season_label']}.")
else:
    if "selected_player_id" not in st.session_state or st.session_state["selected_player_id"] not in df["PlayerId"].values:
        st.session_state["selected_player_id"] = int(df.iloc[0]["PlayerId"])

    p = df[df["PlayerId"] == st.session_state["selected_player_id"]].iloc[0]
    fo_stat_line = (
        f"OZ: {p['OZ_FO%']:.1f}% | DZ: {p['DZ_FO%']:.1f}%" 
        if pd.notna(p['OZ_FO%']) and pd.notna(p['DZ_FO%']) 
        else f"{p['SH%']:.1f}% Shooting Pctg"
    )

    spotlight_html = f"""
    <div class="spotlight-card">
        <div style="display: flex; gap: 28px; align-items: center; flex-wrap: wrap;">
            <div style="flex-shrink: 0; text-align: center;">
                <img src="{p['Photo']}" onerror="this.onerror=null; this.src='{PREDS_LOGO_URL}';" style="width: 145px; height: 145px; object-fit: cover; border-radius: 50%; border: 2px solid #FFB81C; box-shadow: 0 6px 18px rgba(0,0,0,0.65);">
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
                        <div class="stat-pill-sub">{fo_stat_line}</div>
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

    # Roster Selector Grid
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

# Tabbed Analytical Views
st.subheader("Skater Performance")

if not df.empty:
    qualified_df = df[df["GP"] >= 5].reset_index(drop=True)
    limited_df = df[df["GP"] < 5].reset_index(drop=True)

    if "active_tab_view" not in st.session_state:
        st.session_state["active_tab_view"] = "Offensive Impact"

    tabs = [
        "Offensive Impact", 
        "Defensive Impact", 
        "Special Teams Performance",
        "Faceoff Breakdown",
        "Complete Skater Statistics",
        "Limited Sample (< 5 GP)"
    ]

    nav_cols = st.columns(6)
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
        "SH%": st.column_config.ProgressColumn("SH%", min_value=0.0, max_value=35.0, format="%.1f%%"),
        "Total_FO": st.column_config.NumberColumn("Total Draws", format="%d"),
        "FO%": st.column_config.ProgressColumn("Overall FO%", min_value=0.0, max_value=100.0, format="%.1f%%"),
        "OZ_FO%": st.column_config.ProgressColumn("OZ FO%", min_value=0.0, max_value=100.0, format="%.1f%%"),
        "NZ_FO%": st.column_config.ProgressColumn("NZ FO%", min_value=0.0, max_value=100.0, format="%.1f%%"),
        "DZ_FO%": st.column_config.ProgressColumn("DZ FO%", min_value=0.0, max_value=100.0, format="%.1f%%"),
        "P/60": st.column_config.ProgressColumn("P/60", min_value=0.0, max_value=float(df["P/60"].max() or 4.0), format="%.2f"),
        "Off_Score": st.column_config.ProgressColumn("Offensive Impact", min_value=0.0, max_value=float(df["Off_Score"].max() or 6.0), format="%.2f"),
        "Def_Score": st.column_config.ProgressColumn("Defensive Impact", min_value=float(df["Def_Score"].min() or -3.0), max_value=float(df["Def_Score"].max() or 5.0), format="%.2f"),
        "PP_Score": st.column_config.ProgressColumn("PP Impact", min_value=0.0, max_value=float(df["PP_Score"].max() or 5.0), format="%.2f"),
        "PK_Score": st.column_config.ProgressColumn("PK Impact", min_value=0.0, max_value=float(df["PK_Score"].max() or 4.0), format="%.2f"),
    }

    if active_view == "Offensive Impact":
        cols = ["Photo", "Skater", "Pos", "GP", "Off_Score", "P/60", "SOG/60", "PTS", "G", "A", "SOG", "SH%", "PPG", "GWG"]
        off_view = qualified_df[cols].sort_values(by="Off_Score", ascending=False).reset_index(drop=True)
        st.dataframe(off_view, column_config=base_column_config, use_container_width=True, hide_index=True)

    elif active_view == "Defensive Impact":
        cols = ["Photo", "Skater", "Pos", "GP", "Def_Score", "+/- /60", "TOI/GP", "+/-", "PIM", "SHG"]
        def_view = qualified_df[cols].sort_values(by="Def_Score", ascending=False).reset_index(drop=True)
        st.dataframe(def_view, column_config=base_column_config, use_container_width=True, hide_index=True)

    elif active_view == "Special Teams Performance":
        cols = ["Photo", "Skater", "Pos", "GP", "PP_Score", "PK_Score", "PPG", "SHG", "PIM", "TOI/GP"]
        st_view = qualified_df[cols].sort_values(by="PP_Score", ascending=False).reset_index(drop=True)
        st.dataframe(st_view, column_config=base_column_config, use_container_width=True, hide_index=True)

    elif active_view == "Faceoff Breakdown":
        fo_skaters = qualified_df[qualified_df["Total_FO"] > 0].copy()
        if fo_skaters.empty:
            st.info("No faceoffs recorded for skaters in this selection.")
        else:
            cols = ["Photo", "Skater", "Pos", "GP", "Total_FO", "FO%", "OZ_FO%", "NZ_FO%", "DZ_FO%"]
            fo_view = fo_skaters[cols].sort_values(by="Total_FO", ascending=False).reset_index(drop=True)
            st.dataframe(fo_view, column_config=base_column_config, use_container_width=True, hide_index=True)

    elif active_view == "Complete Skater Statistics":
        cols = [
            "Photo", "Skater", "Pos", "GP", "Off_Score", "Def_Score", "PP_Score", "PK_Score",
            "PTS", "G", "A", "+/-", "P/60", "TOI/GP", "SOG", "SH%", "FO%", "PIM", 
            "PPG", "SHG", "GWG"
        ]
        comp_view = qualified_df[cols].sort_values(by="PTS", ascending=False).reset_index(drop=True)
        st.dataframe(comp_view, column_config=base_column_config, use_container_width=True, hide_index=True)

    elif active_view == "Limited Sample (< 5 GP)":
        if limited_df.empty:
            st.info("No skaters currently have fewer than 5 games played for this selection.")
        else:
            cols = [
                "Photo", "Skater", "Pos", "GP", "PTS", "G", "A", "+/-", 
                "TOI/GP", "SOG", "SH%", "PIM", "P/60", "Off_Score", "Def_Score"
            ]
            lim_view = limited_df[cols].sort_values(by="GP", ascending=False).reset_index(drop=True)
            st.dataframe(lim_view, column_config=base_column_config, use_container_width=True, hide_index=True)
