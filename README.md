# Nashville Predators Skater Production Tracker

A Python analytics pipeline that fetches game-by-game data directly from the NHL Web API, tracks seasonal skater trajectories, and evaluates rate production metrics (P/60, shooting percentages, and rolling form).

## Features

- **Automated Data Pipeline:** Pulls active forwards and defensemen directly from the official NHL Web API (`api-web.nhle.com`).
- **Rate Metrics:** Normalizes scoring with Time on Ice (TOI) to compute Points per 60 (`P/60`) and true ice-time share (`TOI/GP`).
- **Rolling Form:** Computes 5-game moving averages to highlight scoring streaks and slumps across the schedule.
- **Visual Trajectories:** Generates cumulative point progression plots across team games.

## Quickstart

### 1. Clone the repository
```bash
git clone [https://github.com/hockeyal08-wq/nashville-predators-production-tracker.git](https://github.com/hockeyal08-wq/nashville-predators-production-tracker.git)
cd nashville-predators-production-tracker
