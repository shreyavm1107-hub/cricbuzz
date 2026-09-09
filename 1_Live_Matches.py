import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.cricbuzz_api import has_api_key, get_live_matches, get_recent_matches, get_upcoming_matches

st.set_page_config(page_title="Live Matches", page_icon="🔴", layout="wide")
st.title("🔴 Live Matches")

if not has_api_key():
    st.error(
        "No Cricbuzz API key configured. Add `CRICBUZZ_API_KEY` to `.streamlit/secrets.toml` "
        "(local) or the app's Secrets panel (Streamlit Cloud) — see README.md for the exact steps."
    )
    st.info("Once the key is set, this page calls three endpoints: live matches, recent results, and "
            "upcoming fixtures, and renders each match as a scorecard.")
    st.stop()

tab1, tab2, tab3 = st.tabs(["Live", "Recent", "Upcoming"])


def render_matches(payload):
    type_matches = payload.get("typeMatches", [])
    if not type_matches:
        st.info("No matches returned right now.")
        return
    for tm in type_matches:
        st.subheader(tm.get("matchType", ""))
        for series in tm.get("seriesMatches", []):
            wrapper = series.get("seriesAdWrapper", {})
            for m in wrapper.get("matches", []):
                info = m.get("matchInfo", {})
                score = m.get("matchScore", {})
                t1, t2 = info.get("team1", {}), info.get("team2", {})
                with st.container(border=True):
                    st.markdown(f"**{t1.get('teamName','')} vs {t2.get('teamName','')}** — {info.get('matchDesc','')}")
                    st.caption(f"{info.get('venueInfo', {}).get('ground','')}, {info.get('venueInfo', {}).get('city','')}")
                    st.write(info.get("status", ""))
                    if score:
                        st.json(score, expanded=False)


try:
    with tab1:
        render_matches(get_live_matches())
    with tab2:
        render_matches(get_recent_matches())
    with tab3:
        render_matches(get_upcoming_matches())
except Exception as e:
    st.error(f"Couldn't reach the Cricbuzz API: {e}")
    st.caption("Double check your API key is valid and hasn't hit its RapidAPI rate limit.")
