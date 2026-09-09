"""
Thin wrapper around the Cricbuzz Cricket API on RapidAPI.
Get a key: rapidapi.com -> search "Cricbuzz Cricket" -> Subscribe (free tier) -> copy the X-RapidAPI-Key.

Set it as an environment variable CRICBUZZ_API_KEY, or in .streamlit/secrets.toml:
    CRICBUZZ_API_KEY = "your-key-here"
"""
import os
import requests
import streamlit as st

BASE_URL = "https://cricbuzz-cricket.p.rapidapi.com"


def get_api_key():
    try:
        if "CRICBUZZ_API_KEY" in st.secrets:
            return st.secrets["CRICBUZZ_API_KEY"]
    except Exception:
        pass
    return os.environ.get("CRICBUZZ_API_KEY")


def _headers():
    return {
        "X-RapidAPI-Key": get_api_key(),
        "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com",
    }


def has_api_key():
    return bool(get_api_key())


def get_live_matches():
    """GET /matches/v1/live"""
    r = requests.get(f"{BASE_URL}/matches/v1/live", headers=_headers(), timeout=10)
    r.raise_for_status()
    return r.json()


def get_recent_matches():
    """GET /matches/v1/recent"""
    r = requests.get(f"{BASE_URL}/matches/v1/recent", headers=_headers(), timeout=10)
    r.raise_for_status()
    return r.json()


def get_upcoming_matches():
    """GET /matches/v1/upcoming"""
    r = requests.get(f"{BASE_URL}/matches/v1/upcoming", headers=_headers(), timeout=10)
    r.raise_for_status()
    return r.json()


def get_match_scorecard(match_id):
    """GET /mcenter/v1/{match_id}/scard"""
    r = requests.get(f"{BASE_URL}/mcenter/v1/{match_id}/scard", headers=_headers(), timeout=10)
    r.raise_for_status()
    return r.json()
