import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_connection import run_query

st.set_page_config(page_title="Top Player Stats", page_icon="📊", layout="wide")
st.title("📊 Top Player Stats")

fmt = st.selectbox("Format", ["ODI", "Test", "T20I"])

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏏 Most Runs")
    df = run_query("""
        SELECT p.full_name AS Player, p.country AS Country,
               SUM(b.runs_scored) AS Runs,
               ROUND(AVG(b.strike_rate), 2) AS "Strike Rate",
               SUM(CASE WHEN b.runs_scored >= 100 THEN 1 ELSE 0 END) AS "100s"
        FROM batting_scorecard b
        JOIN players p ON p.player_id = b.player_id
        JOIN matches m ON m.match_id = b.match_id
        WHERE m.match_format = ?
        GROUP BY p.player_id ORDER BY Runs DESC LIMIT 10
    """, [fmt])
    st.dataframe(df, hide_index=True, width="stretch")

with col2:
    st.subheader("🎯 Most Wickets")
    df = run_query("""
        SELECT p.full_name AS Player, p.country AS Country,
               SUM(bw.wickets_taken) AS Wickets,
               ROUND(SUM(bw.runs_conceded)*1.0/NULLIF(SUM(bw.overs),0), 2) AS Economy
        FROM bowling_scorecard bw
        JOIN players p ON p.player_id = bw.player_id
        JOIN matches m ON m.match_id = bw.match_id
        WHERE m.match_format = ?
        GROUP BY p.player_id ORDER BY Wickets DESC LIMIT 10
    """, [fmt])
    st.dataframe(df, hide_index=True, width="stretch")

st.divider()
st.subheader("🏆 Highest Individual Scores")
df = run_query("""
    SELECT p.full_name AS Player, m.match_desc AS Match, b.runs_scored AS Runs,
           b.balls_faced AS Balls, b.strike_rate AS SR
    FROM batting_scorecard b
    JOIN players p ON p.player_id = b.player_id
    JOIN matches m ON m.match_id = b.match_id
    WHERE m.match_format = ?
    ORDER BY b.runs_scored DESC LIMIT 10
""", [fmt])
st.dataframe(df, hide_index=True, width="stretch")
