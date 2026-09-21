import time
import requests
import pandas as pd
import matplotlib.pyplot as plt

BASE_URL = "https://api-web.nhle.com/v1"
TEAM_TRICODE = "NSH"

def get_predators_skaters():
    """Fetch current Predators forwards and defensemen."""
    url = f"{BASE_URL}/roster/{TEAM_TRICODE}/current"
    response = requests.get(url)
    response.raise_for_status()
    roster_data = response.json()
    
    skaters = []
    for pos_group in ["forwards", "defensemen"]:
        for p in roster_data.get(pos_group, []):
            skaters.append({
                "player_id": p["id"],
                "name": f"{p['firstName']['default']} {p['lastName']['default']}",
                "position": p["positionCode"]
            })
    return skaters

def parse_toi_to_minutes(toi_str):
    """Convert 'MM:SS' string into float minutes."""
    if not toi_str or not isinstance(toi_str, str):
        return 0.0
    parts = toi_str.split(":")
    return int(parts[0]) + int(parts[1]) / 60.0

def fetch_player_season_gamelog(player_id, season="20252026", game_type=2):
    """
    Fetch game log for a single player.
    game_type: 2 = Regular Season, 3 = Playoffs
    """
    url = f"{BASE_URL}/player/{player_id}/game-log/{season}/{game_type}"
    res = requests.get(url)
    if res.status_code == 404:
        return []
    res.raise_for_status()
    return res.json().get("gameLog", [])

def build_production_dataframe(season="20252026"):
    skaters = get_predators_skaters()
    all_game_rows = []
    
    print(f"Gathering production data for {len(skaters)} Predators skaters...")
    
    for s in skaters:
        p_id = s["player_id"]
        name = s["name"]
        pos = s["position"]
        
        games = fetch_player_season_gamelog(p_id, season=season)
        for g in games:
            toi_min = parse_toi_to_minutes(g.get("toi", "00:00"))
            all_game_rows.append({
                "player_id": p_id,
                "name": name,
                "position": pos,
                "game_id": g.get("gameId"),
                "game_date": g.get("gameDate"),
                "opponent": g.get("opponentCommonName", {}).get("default", "N/A"),
                "goals": g.get("goals", 0),
                "assists": g.get("assists", 0),
                "points": g.get("points", 0),
                "shots": g.get("shots", 0),
                "plus_minus": g.get("plusMinus", 0),
                "power_play_goals": g.get("powerPlayGoals", 0),
                "power_play_points": g.get("powerPlayPoints", 0),
                "toi_minutes": toi_min
            })
        time.sleep(0.15)  # Be polite to the public API
        
    df = pd.DataFrame(all_game_rows)
    if df.empty:
        print("No games logged yet for the selected season.")
        return df

    # Sort chronologically
    df["game_date"] = pd.to_datetime(df["game_date"])
    df = df.sort_values(by=["name", "game_date"]).reset_index(drop=True)
    
    # Calculate cumulative metrics and rolling form
    df["cum_points"] = df.groupby("name")["points"].cumsum()
    df["cum_goals"] = df.groupby("name")["goals"].cumsum()
    df["cum_toi"] = df.groupby("name")["toi_minutes"].cumsum()
    df["rolling_5g_points"] = df.groupby("name")["points"].rolling(5, min_periods=1).mean().values
    
    return df

def generate_skater_summary(df):
    """Aggregate per-skater production and rate metrics (e.g., P/60)."""
    summary = df.groupby(["name", "position"]).agg(
        GP=("game_id", "count"),
        G=("goals", "sum"),
        A=("assists", "sum"),
        PTS=("points", "sum"),
        SOG=("shots", "sum"),
        PPP=("power_play_points", "sum"),
        TOI_Total=("toi_minutes", "sum")
    ).reset_index()
    
    summary["TOI/GP"] = (summary["TOI_Total"] / summary["GP"]).round(1)
    summary["P/60"] = ((summary["PTS"] / summary["TOI_Total"]) * 60).round(2)
    summary["Sh%"] = ((summary["G"] / summary["SOG"]) * 100).round(1).fillna(0)
    
    return summary.sort_values(by="PTS", ascending=False).reset_index(drop=True)

def plot_top_producers(df, top_n=5):
    """Plot cumulative scoring trajectories for top N point producers."""
    top_scorers = (
        df.groupby("name")["points"]
        .sum()
        .nlargest(top_n)
        .index.tolist()
    )
    
    plt.figure(figsize=(10, 6))
    for player in top_scorers:
        player_df = df[df["name"] == player].sort_values("game_date")
        plt.plot(
            range(1, len(player_df) + 1),
            player_df["cum_points"],
            marker="o",
            label=player
        )
        
    plt.title(f"Nashville Predators: Top {top_n} Skater Production Trajectory", fontsize=14)
    plt.xlabel("Team Game Number", fontsize=11)
    plt.ylabel("Cumulative Points", fontsize=11)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    df_games = build_production_dataframe(season="20252026")
    
    if not df_games.empty:
        summary_table = generate_skater_summary(df_games)
        print("\n--- Nashville Predators Production Summary ---")
        print(summary_table[["name", "position", "GP", "G", "A", "PTS", "P/60", "TOI/GP"]].to_string())
        
        plot_top_producers(df_games, top_n=5)
