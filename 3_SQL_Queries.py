import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_connection import run_query
from utils.sql_queries import QUERIES

st.set_page_config(page_title="SQL Queries & Analytics", page_icon="🧮", layout="wide")
st.title("🧮 SQL Queries & Analytics")
st.caption("All 25 practice questions from the project brief — pick one to run it live against the database.")

level = st.radio("Difficulty", list(QUERIES.keys()), horizontal=True)
questions = QUERIES[level]

labels = {num: f"Q{num}. {title}" for num, (title, _) in questions.items()}
choice = st.selectbox("Question", options=list(questions.keys()), format_func=lambda n: labels[n])

title, sql = questions[choice]
st.subheader(labels[choice])

with st.expander("View SQL"):
    st.code(sql.strip(), language="sql")

try:
    df = run_query(sql)
    if df.empty:
        st.info("This query ran successfully but returned 0 rows — the seeded sample data doesn't meet this "
                 "question's threshold (e.g. '10+ matches', '6+ quarters'). Swap in a fuller dataset and it "
                 "will populate.")
    else:
        st.dataframe(df, hide_index=True, width="stretch")
        st.caption(f"{len(df)} row(s)")
except Exception as e:
    st.error(f"Query failed: {e}")
