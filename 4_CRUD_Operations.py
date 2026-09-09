import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_connection import run_query, execute

st.set_page_config(page_title="CRUD Operations", page_icon="⚙️", layout="wide")
st.title("⚙️ CRUD Operations — Players")
st.caption("Form-based Create, Read, Update, Delete on the players table.")

tab_create, tab_read, tab_update, tab_delete = st.tabs(["➕ Create", "📖 Read", "✏️ Update", "🗑️ Delete"])

ROLES = ["Batsman", "Bowler", "All-rounder", "Wicket-keeper"]
BAT_STYLES = ["Right-hand bat", "Left-hand bat"]
BOWL_STYLES = ["", "Right-arm fast", "Left-arm fast", "Right-arm off-break", "Left-arm orthodox",
               "Right-arm leg-break", "Right-arm medium"]

with tab_create:
    with st.form("create_player", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("Full name")
        country = c2.text_input("Country")
        role = c1.selectbox("Playing role", ROLES)
        batting_style = c2.selectbox("Batting style", BAT_STYLES)
        bowling_style = c1.selectbox("Bowling style", BOWL_STYLES)
        submitted = st.form_submit_button("Add player")
        if submitted:
            if not name or not country:
                st.error("Full name and country are required.")
            else:
                new_id = run_query("SELECT COALESCE(MAX(player_id),0)+1 AS n FROM players").n[0]
                execute(
                    "INSERT INTO players (player_id, full_name, country, playing_role, batting_style, bowling_style) "
                    "VALUES (?,?,?,?,?,?)",
                    [int(new_id), name, country, role, batting_style, bowling_style or None]
                )
                st.success(f"Added {name} (player_id {new_id}).")

with tab_read:
    search = st.text_input("Filter by name or country (optional)")
    if search:
        df = run_query(
            "SELECT * FROM players WHERE full_name LIKE ? OR country LIKE ? ORDER BY player_id",
            [f"%{search}%", f"%{search}%"]
        )
    else:
        df = run_query("SELECT * FROM players ORDER BY player_id")
    st.dataframe(df, hide_index=True, width="stretch")
    st.caption(f"{len(df)} player(s)")

with tab_update:
    players_df = run_query("SELECT player_id, full_name FROM players ORDER BY full_name")
    if players_df.empty:
        st.info("No players yet.")
    else:
        options = dict(zip(players_df.full_name + " (ID " + players_df.player_id.astype(str) + ")", players_df.player_id))
        pick = st.selectbox("Player to edit", list(options.keys()))
        pid = int(options[pick])
        current = run_query("SELECT * FROM players WHERE player_id = ?", [pid]).iloc[0]

        with st.form("update_player"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Full name", value=current.full_name)
            country = c2.text_input("Country", value=current.country)
            role = c1.selectbox("Playing role", ROLES, index=ROLES.index(current.playing_role) if current.playing_role in ROLES else 0)
            batting_style = c2.selectbox("Batting style", BAT_STYLES, index=BAT_STYLES.index(current.batting_style) if current.batting_style in BAT_STYLES else 0)
            bowl_idx = BOWL_STYLES.index(current.bowling_style) if current.bowling_style in BOWL_STYLES else 0
            bowling_style = c1.selectbox("Bowling style", BOWL_STYLES, index=bowl_idx)
            if st.form_submit_button("Save changes"):
                execute(
                    "UPDATE players SET full_name=?, country=?, playing_role=?, batting_style=?, bowling_style=? "
                    "WHERE player_id=?",
                    [name, country, role, batting_style, bowling_style or None, pid]
                )
                st.success(f"Updated player_id {pid}.")
                st.rerun()

with tab_delete:
    players_df = run_query("SELECT player_id, full_name FROM players ORDER BY full_name")
    if players_df.empty:
        st.info("No players yet.")
    else:
        options = dict(zip(players_df.full_name + " (ID " + players_df.player_id.astype(str) + ")", players_df.player_id))
        pick = st.selectbox("Player to delete", list(options.keys()), key="delete_pick")
        pid = int(options[pick])
        st.warning(f"This will permanently delete player_id {pid} and cannot be undone.")
        if st.button("Delete player", type="primary"):
            execute("DELETE FROM players WHERE player_id = ?", [pid])
            st.success(f"Deleted player_id {pid}.")
            st.rerun()
