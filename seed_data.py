"""
Populates cricbuzz_livestats.db with a realistic-shaped sample dataset so the
whole app (Top Stats, all 25 SQL queries, CRUD) works out of the box, before
you've wired in your own Cricbuzz API key.

Run once with:  python data/seed_data.py
"""
import sys, os, random, datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_connection import get_connection, init_schema, db_is_empty

random.seed(42)

COUNTRIES = ["India", "Australia", "England", "South Africa", "New Zealand", "Pakistan", "Sri Lanka", "West Indies"]
FORMATS = ["Test", "ODI", "T20I"]
FORMAT_OVERS = {"Test": 90, "ODI": 50, "T20I": 20}

FIRST_NAMES = ["Rohan", "Arjun", "Vikram", "Aditya", "Kabir", "Steve", "James", "Ben", "Joe", "Sam",
               "Marcus", "Quinton", "Kagiso", "Faf", "Temba", "Kane", "Trent", "Tim", "Devon", "Mitchell",
               "Babar", "Shaheen", "Shadab", "Mohammad", "Wanindu", "Dimuth", "Kusal", "Nicholas", "Shai", "Jason"]
LAST_NAMES = ["Sharma", "Kumar", "Singh", "Patel", "Smith", "Anderson", "Stokes", "Root", "Curran", "Williams",
              "Labuschagne", "de Kock", "Rabada", "du Plessis", "Bavuma", "Williamson", "Boult", "Southee",
              "Conway", "Starc", "Azam", "Afridi", "Khan", "Rizwan", "Fernando", "Karunaratne", "Mendis",
              "Pooran", "Hope", "Holder"]

random_used_names = set()

def unique_name():
    while True:
        n = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        if n not in random_used_names:
            random_used_names.add(n)
            return n

ROLES = ["Batsman", "Bowler", "All-rounder", "Wicket-keeper"]
BAT_STYLES = ["Right-hand bat", "Left-hand bat"]
BOWL_STYLES = ["Right-arm fast", "Left-arm fast", "Right-arm off-break", "Left-arm orthodox",
               "Right-arm leg-break", "Right-arm medium"]

VENUES = [
    ("Melbourne Cricket Ground", "Melbourne", "Australia", 100024),
    ("Eden Gardens", "Kolkata", "India", 68000),
    ("Lord's", "London", "England", 30000),
    ("Wankhede Stadium", "Mumbai", "India", 33108),
    ("Newlands", "Cape Town", "South Africa", 25000),
    ("Basin Reserve", "Wellington", "New Zealand", 11600),
    ("Gaddafi Stadium", "Lahore", "Pakistan", 27000),
    ("R Premadasa Stadium", "Colombo", "Sri Lanka", 35000),
    ("Kensington Oval", "Bridgetown", "West Indies", 28000),
    ("Narendra Modi Stadium", "Ahmedabad", "India", 132000),
]


def build_players():
    players = []
    pid = 1
    for country in COUNTRIES:
        for _ in range(9):
            role = random.choices(ROLES, weights=[35, 30, 25, 10])[0]
            bowling_style = None if role == "Batsman" else random.choice(BOWL_STYLES)
            players.append({
                "player_id": pid,
                "full_name": unique_name(),
                "country": country,
                "playing_role": role,
                "batting_style": random.choice(BAT_STYLES),
                "bowling_style": bowling_style,
            })
            pid += 1
    return players


def build_venues():
    return [{"venue_id": i + 1, "venue_name": v[0], "city": v[1], "country": v[2], "capacity": v[3]}
            for i, v in enumerate(VENUES)]


def build_series():
    series = []
    sid = 1
    for year in range(2019, 2026):
        for fmt in FORMATS:
            host = random.choice(COUNTRIES)
            n_matches = {"Test": random.choice([2, 3, 5]), "ODI": random.choice([3, 5]), "T20I": random.choice([3, 5])}[fmt]
            series.append({
                "series_id": sid,
                "series_name": f"{host} Tour {year} ({fmt})",
                "host_country": host,
                "match_type": fmt,
                "start_date": f"{year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
                "total_matches": n_matches,
            })
            sid += 1
    return series


def gen_batting_innings(match_id, team, players_pool, innings_no, overs_limit):
    """Returns list of batting rows for one team's innings."""
    order = random.sample(players_pool, min(11, len(players_pool)))
    rows = []
    balls_bucket = overs_limit * 6
    for pos, p in enumerate(order, start=1):
        if pos <= 6:
            runs = max(0, int(random.gauss(32, 28)))
        elif pos <= 8:
            runs = max(0, int(random.gauss(15, 14)))
        else:
            runs = max(0, int(random.gauss(6, 8)))
        balls = max(runs, int(runs / max(random.uniform(0.5, 1.6), 0.3))) if runs > 0 else random.randint(0, 6)
        balls = max(balls, 1)
        fours = min(runs // 4, random.randint(0, max(1, runs // 6 + 1)))
        sixes = min((runs - fours * 4) // 6, random.randint(0, 3)) if runs > 20 else 0
        sr = round((runs / balls) * 100, 2) if balls else 0.0
        dismissal = random.choice(["Caught", "Bowled", "LBW", "Run Out", "Stumped", "Not Out"])
        rows.append({
            "match_id": match_id, "player_id": p["player_id"], "team": team,
            "innings_no": innings_no, "batting_position": pos, "runs_scored": runs,
            "balls_faced": balls, "fours": fours, "sixes": sixes, "strike_rate": sr,
            "dismissal": dismissal,
        })
    return rows


def gen_bowling_innings(match_id, team, players_pool, innings_no, overs_limit):
    bowlers = [p for p in players_pool if p["playing_role"] in ("Bowler", "All-rounder")]
    if len(bowlers) < 4:
        bowlers = players_pool
    chosen = random.sample(bowlers, min(random.randint(4, 6), len(bowlers)))
    rows = []
    remaining_overs = overs_limit
    for i, p in enumerate(chosen):
        is_last = i == len(chosen) - 1
        max_share = remaining_overs if is_last else remaining_overs / (len(chosen) - i) * random.uniform(0.7, 1.3)
        overs = round(min(remaining_overs, max(1, max_share)), 1)
        remaining_overs = max(0, round(remaining_overs - overs, 1))
        econ = round(random.gauss(5.6 if overs_limit <= 20 else 4.5, 1.6), 2)
        econ = max(1.5, econ)
        runs_conceded = max(0, round(overs * econ))
        wickets = random.choices([0, 1, 2, 3, 4], weights=[35, 30, 20, 10, 5])[0]
        rows.append({
            "match_id": match_id, "player_id": p["player_id"], "team": team,
            "innings_no": innings_no, "overs": overs, "maidens": random.randint(0, 2) if overs >= 4 else 0,
            "runs_conceded": runs_conceded, "wickets_taken": wickets, "economy_rate": econ,
        })
        if remaining_overs <= 0:
            break
    return rows


def build_matches_and_scorecards(players, venues, series):
    players_by_country = {c: [p for p in players if p["country"] == c] for c in COUNTRIES}
    matches, batting_rows, bowling_rows = [], [], []
    match_id = 1

    for s in series:
        fmt = s["match_type"]
        host_players = players_by_country[s["host_country"]]
        opponents = [c for c in COUNTRIES if c != s["host_country"]]
        for _ in range(s["total_matches"]):
            opp_country = random.choice(opponents)
            team1, team2 = s["host_country"], opp_country
            venue = random.choice([v for v in venues if v["country"] == team1] or venues)
            year = int(s["start_date"][:4])
            match_date = (datetime.date(year, 1, 1) + datetime.timedelta(days=random.randint(0, 330))).isoformat()

            toss_winner = random.choice([team1, team2])
            toss_decision = random.choice(["bat", "bowl"])
            if fmt == "Test":
                winning_team = random.choices([team1, team2, "Draw"], weights=[45, 45, 10])[0]
            else:
                winning_team = random.choices([team1, team2], weights=[50, 50])[0]
            if fmt == "Test" and winning_team == "Draw":
                victory_margin, victory_type = 0, "draw"
            else:
                victory_type = random.choice(["runs", "wickets"])
                victory_margin = random.randint(5, 180) if victory_type == "runs" else random.randint(1, 9)

            innings_count = 2 if fmt in ("ODI", "T20I") else random.choice([2, 3, 4])
            overs_limit = FORMAT_OVERS[fmt]

            matches.append({
                "match_id": match_id, "series_id": s["series_id"],
                "match_desc": f"{team1} vs {team2}, {s['series_name']}",
                "team1": team1, "team2": team2, "venue_id": venue["venue_id"],
                "match_date": match_date, "match_format": fmt,
                "toss_winner": toss_winner, "toss_decision": toss_decision,
                "winning_team": winning_team, "victory_margin": victory_margin,
                "victory_type": victory_type, "match_status": "Completed",
            })

            opp_players = players_by_country[opp_country]
            for inn in range(1, innings_count + 1):
                batting_team, bowling_team = (team1, team2) if inn % 2 == 1 else (team2, team1)
                bat_pool = host_players if batting_team == team1 else opp_players
                bowl_pool = opp_players if batting_team == team1 else host_players
                batting_rows += gen_batting_innings(match_id, batting_team, bat_pool, inn, overs_limit)
                bowling_rows += gen_bowling_innings(match_id, bowling_team, bowl_pool, inn, overs_limit)

            match_id += 1

    return matches, batting_rows, bowling_rows


def build_fielding(players, batting_rows):
    fielding = []
    for p in players:
        fielding.append({
            "player_id": p["player_id"],
            "catches": random.randint(0, 45) if p["playing_role"] != "Wicket-keeper" else random.randint(20, 120),
            "stumpings": random.randint(0, 25) if p["playing_role"] == "Wicket-keeper" else 0,
        })
    return fielding


def seed():
    init_schema()
    if not db_is_empty():
        print("Database already has data — skipping seed. Delete cricbuzz_livestats.db to reseed.")
        return

    players = build_players()
    venues = build_venues()
    series = build_series()
    matches, batting_rows, bowling_rows = build_matches_and_scorecards(players, venues, series)
    fielding = build_fielding(players, batting_rows)

    conn = get_connection()
    cur = conn.cursor()

    cur.executemany(
        "INSERT INTO players VALUES (:player_id,:full_name,:country,:playing_role,:batting_style,:bowling_style)",
        players)
    cur.executemany(
        "INSERT INTO venues VALUES (:venue_id,:venue_name,:city,:country,:capacity)", venues)
    cur.executemany(
        "INSERT INTO series VALUES (:series_id,:series_name,:host_country,:match_type,:start_date,:total_matches)",
        series)
    cur.executemany("""INSERT INTO matches VALUES (:match_id,:series_id,:match_desc,:team1,:team2,:venue_id,
        :match_date,:match_format,:toss_winner,:toss_decision,:winning_team,:victory_margin,:victory_type,
        :match_status)""", matches)
    cur.executemany("""INSERT INTO batting_scorecard
        (match_id,player_id,team,innings_no,batting_position,runs_scored,balls_faced,fours,sixes,strike_rate,dismissal)
        VALUES (:match_id,:player_id,:team,:innings_no,:batting_position,:runs_scored,:balls_faced,:fours,:sixes,
        :strike_rate,:dismissal)""", batting_rows)
    cur.executemany("""INSERT INTO bowling_scorecard
        (match_id,player_id,team,innings_no,overs,maidens,runs_conceded,wickets_taken,economy_rate)
        VALUES (:match_id,:player_id,:team,:innings_no,:overs,:maidens,:runs_conceded,:wickets_taken,:economy_rate)""",
        bowling_rows)
    cur.executemany("INSERT INTO fielding_stats VALUES (:player_id,:catches,:stumpings)", fielding)

    conn.commit()
    conn.close()
    print(f"Seeded {len(players)} players, {len(venues)} venues, {len(series)} series, "
          f"{len(matches)} matches, {len(batting_rows)} batting rows, {len(bowling_rows)} bowling rows.")


if __name__ == "__main__":
    seed()
