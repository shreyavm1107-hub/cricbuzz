# 🏏 Cricbuzz LiveStats

Real-Time Cricket Insights & SQL-Based Analytics — a multi-page Streamlit app combining
the Cricbuzz API, a SQL database, and 25 practice analytics queries.

## Pages
1. **Live Matches** — live/recent/upcoming matches via the Cricbuzz API (needs your key)
2. **Top Player Stats** — leading run scorers & wicket takers by format
3. **SQL Queries & Analytics** — all 25 questions from the brief (Beginner → Advanced), run live
4. **CRUD Operations** — add, edit, delete player records with a form UI

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```
The database (`cricbuzz_livestats.db`) and sample data are created automatically on first run
— you don't need to run anything else manually.

## Setting up your Cricbuzz API key
The Live Matches page needs a free RapidAPI key:

1. Go to **rapidapi.com**, sign up / log in.
2. Search **"Cricbuzz Cricket"** in the marketplace and open the one published on RapidAPI's
   own hub (not a third-party clone) — it's the standard one used for this project.
3. Click **Subscribe** on the free "Basic" plan.
4. Copy your `X-RapidAPI-Key` from the code snippets panel.
5. Set it:
   - **Locally**: create `.streamlit/secrets.toml` with:
     ```toml
     CRICBUZZ_API_KEY = "your-key-here"
     ```
   - **Streamlit Cloud**: app → Settings → Secrets → paste the same line.

Until the key is set, every other page (Top Stats, all 25 SQL queries, CRUD) works fully
against the seeded sample database.

## Project structure
```
cricbuzz-livestats/
├── app.py                     # Home page
├── requirements.txt
├── README.md
├── pages/
│   ├── 1_Live_Matches.py
│   ├── 2_Top_Player_Stats.py
│   ├── 3_SQL_Queries.py
│   └── 4_CRUD_Operations.py
├── utils/
│   ├── db_connection.py       # SQLite connection + schema
│   ├── sql_queries.py         # The 25 SQL query definitions
│   └── cricbuzz_api.py        # RapidAPI wrapper
├── data/
│   └── seed_data.py           # Generates the sample dataset
└── cricbuzz_livestats.db      # Created automatically
```

## Database schema
`players`, `venues`, `series`, `matches`, `batting_scorecard`, `bowling_scorecard`, `fielding_stats`
— see `utils/db_connection.py` for full column definitions.

## Sample data note
The seeded dataset (72 players, 76 matches, ~1,500 batting rows) is enough for every one of the
25 queries to run without error. A few of the stricter advanced queries (10+ matches for one
bowler, 6+ quarters tracked for one player) return 0 rows against this sample size — that's
expected, not a bug. Once your API key is live and you're pulling and storing real matches over
time, those will populate naturally.
