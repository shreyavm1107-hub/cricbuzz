import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.db_connection import init_schema, db_is_empty, run_query
from utils.cricbuzz_api import has_api_key

st.set_page_config(page_title="Cricbuzz LiveStats", page_icon="🏏", layout="wide")

init_schema()
if db_is_empty():
    from data.seed_data import seed
    seed()

st.title("🏏 Cricbuzz LiveStats")
st.caption("Real-Time Cricket Insights & SQL-Based Analytics")

st.markdown("""
Use the sidebar to navigate:

- **🔴 Live Matches** — live/recent/upcoming matches from the Cricbuzz API (needs your API key)
- **📊 Top Player Stats** — leading run scorers & wicket takers
- **🧮 SQL Queries & Analytics** — all 25 practice queries from the project brief, running live against the database
- **⚙️ CRUD Operations** — add, edit, and delete player records
""")

if not has_api_key():
    st.warning(
        "No Cricbuzz API key found yet. The **Live Matches** page won't be able to pull real data until you "
        "set `CRICBUZZ_API_KEY` (see README.md). Everything else — Top Stats, all 25 SQL queries, and CRUD — "
        "already works against the seeded sample database.",
        icon="⚠️"
    )

c1, c2, c3, c4 = st.columns(4)
c1.metric("Players", run_query("SELECT COUNT(*) n FROM players").n[0])
c2.metric("Matches", run_query("SELECT COUNT(*) n FROM matches").n[0])
c3.metric("Venues", run_query("SELECT COUNT(*) n FROM venues").n[0])
c4.metric("Series", run_query("SELECT COUNT(*) n FROM series").n[0])

st.divider()
st.subheader("Project structure")
st.code("""
cricbuzz-livestats/
├── app.py                     # Home page (this one)
├── requirements.txt
├── README.md
├── pages/
│   ├── 1_Live_Matches.py      # Cricbuzz API — live/recent/upcoming
│   ├── 2_Top_Player_Stats.py  # Leaderboards from the DB
│   ├── 3_SQL_Queries.py       # All 25 practice queries
│   └── 4_CRUD_Operations.py   # Add/edit/delete players
├── utils/
│   ├── db_connection.py       # SQLite connection + schema
│   ├── sql_queries.py         # The 25 SQL query definitions
│   └── cricbuzz_api.py        # RapidAPI wrapper
├── data/
│   └── seed_data.py           # Generates realistic sample data
└── cricbuzz_livestats.db      # Created automatically on first run
""", language="text")
