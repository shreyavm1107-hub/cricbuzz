"""
Centralized SQLite connection handling for Cricbuzz LiveStats.
Swap this out for psycopg2 / mysql-connector by changing get_connection()
if you outgrow SQLite — every page just calls get_connection() and run_query().
"""
import sqlite3
import os
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cricbuzz_livestats.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    country TEXT NOT NULL,
    playing_role TEXT NOT NULL,     -- Batsman, Bowler, All-rounder, Wicket-keeper
    batting_style TEXT,
    bowling_style TEXT
);

CREATE TABLE IF NOT EXISTS venues (
    venue_id INTEGER PRIMARY KEY,
    venue_name TEXT NOT NULL,
    city TEXT,
    country TEXT,
    capacity INTEGER
);

CREATE TABLE IF NOT EXISTS series (
    series_id INTEGER PRIMARY KEY,
    series_name TEXT NOT NULL,
    host_country TEXT,
    match_type TEXT,                -- Test / ODI / T20I
    start_date TEXT,
    total_matches INTEGER
);

CREATE TABLE IF NOT EXISTS matches (
    match_id INTEGER PRIMARY KEY,
    series_id INTEGER REFERENCES series(series_id),
    match_desc TEXT,
    team1 TEXT NOT NULL,
    team2 TEXT NOT NULL,
    venue_id INTEGER REFERENCES venues(venue_id),
    match_date TEXT,
    match_format TEXT,              -- Test / ODI / T20I
    toss_winner TEXT,
    toss_decision TEXT,             -- bat / bowl
    winning_team TEXT,
    victory_margin INTEGER,
    victory_type TEXT,              -- runs / wickets
    match_status TEXT DEFAULT 'Completed'
);

CREATE TABLE IF NOT EXISTS batting_scorecard (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER REFERENCES matches(match_id),
    player_id INTEGER REFERENCES players(player_id),
    team TEXT,
    innings_no INTEGER,
    batting_position INTEGER,
    runs_scored INTEGER,
    balls_faced INTEGER,
    fours INTEGER,
    sixes INTEGER,
    strike_rate REAL,
    dismissal TEXT
);

CREATE TABLE IF NOT EXISTS bowling_scorecard (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER REFERENCES matches(match_id),
    player_id INTEGER REFERENCES players(player_id),
    team TEXT,
    innings_no INTEGER,
    overs REAL,
    maidens INTEGER,
    runs_conceded INTEGER,
    wickets_taken INTEGER,
    economy_rate REAL
);

CREATE TABLE IF NOT EXISTS fielding_stats (
    player_id INTEGER PRIMARY KEY REFERENCES players(player_id),
    catches INTEGER DEFAULT 0,
    stumpings INTEGER DEFAULT 0
);
"""


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_schema():
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def run_query(sql, params=None):
    """Run a SELECT and return a pandas DataFrame."""
    conn = get_connection()
    try:
        df = pd.read_sql_query(sql, conn, params=params or [])
    finally:
        conn.close()
    return df


def execute(sql, params=None):
    """Run an INSERT / UPDATE / DELETE."""
    conn = get_connection()
    try:
        cur = conn.execute(sql, params or [])
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def db_is_empty():
    conn = get_connection()
    try:
        n = conn.execute("SELECT COUNT(*) FROM players").fetchone()[0]
    except sqlite3.OperationalError:
        n = 0
    conn.close()
    return n == 0
