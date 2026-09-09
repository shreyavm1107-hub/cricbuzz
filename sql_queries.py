"""
The 25 SQL practice questions from the project brief, each mapped to a real
query against the schema in utils/db_connection.py (SQLite dialect).
"""

QUERIES = {
    "Beginner": {
        1: ("Players representing India", """
            SELECT full_name, playing_role, batting_style, bowling_style
            FROM players WHERE country = 'India';
        """),
        2: ("Matches played in the last 30 days", """
            SELECT match_desc, team1, team2, v.venue_name || ', ' || v.city AS venue, match_date
            FROM matches m JOIN venues v ON v.venue_id = m.venue_id
            WHERE date(match_date) >= date((SELECT max(match_date) FROM matches), '-30 days')
            ORDER BY match_date DESC;
        """),
        3: ("Top 10 highest run scorers (ODI)", """
            SELECT p.full_name,
                   SUM(b.runs_scored) AS total_runs,
                   ROUND(SUM(b.runs_scored)*1.0 / NULLIF(SUM(CASE WHEN b.dismissal <> 'Not Out' THEN 1 ELSE 0 END),0), 2) AS batting_average,
                   SUM(CASE WHEN b.runs_scored >= 100 THEN 1 ELSE 0 END) AS centuries
            FROM batting_scorecard b
            JOIN players p ON p.player_id = b.player_id
            JOIN matches m ON m.match_id = b.match_id
            WHERE m.match_format = 'ODI'
            GROUP BY p.player_id ORDER BY total_runs DESC LIMIT 10;
        """),
        4: ("Venues with capacity > 50,000", """
            SELECT venue_name, city, country, capacity FROM venues
            WHERE capacity > 50000 ORDER BY capacity DESC;
        """),
        5: ("Total wins per team", """
            SELECT winning_team AS team, COUNT(*) AS total_wins
            FROM matches WHERE winning_team NOT IN ('Draw')
            GROUP BY winning_team ORDER BY total_wins DESC;
        """),
        6: ("Player count by playing role", """
            SELECT playing_role, COUNT(*) AS player_count
            FROM players GROUP BY playing_role ORDER BY player_count DESC;
        """),
        7: ("Highest individual score per format", """
            SELECT m.match_format, MAX(b.runs_scored) AS highest_score
            FROM batting_scorecard b JOIN matches m ON m.match_id = b.match_id
            GROUP BY m.match_format;
        """),
        8: ("Series started in 2024", """
            SELECT series_name, host_country, match_type, start_date, total_matches
            FROM series WHERE start_date LIKE '2024%';
        """),
    },
    "Intermediate": {
        9: ("All-rounders: 1000+ runs AND 50+ wickets", """
            SELECT p.full_name,
                   SUM(DISTINCT_runs.total_runs) AS total_runs,
                   SUM(DISTINCT_wkts.total_wkts) AS total_wickets,
                   m.match_format
            FROM players p
            JOIN (SELECT player_id, match_id, SUM(runs_scored) AS total_runs FROM batting_scorecard GROUP BY player_id, match_id) DISTINCT_runs ON DISTINCT_runs.player_id = p.player_id
            JOIN (SELECT player_id, match_id, SUM(wickets_taken) AS total_wkts FROM bowling_scorecard GROUP BY player_id, match_id) DISTINCT_wkts ON DISTINCT_wkts.player_id = p.player_id AND DISTINCT_wkts.match_id = DISTINCT_runs.match_id
            JOIN matches m ON m.match_id = DISTINCT_runs.match_id
            GROUP BY p.player_id, m.match_format
            HAVING SUM(DISTINCT_runs.total_runs) > 1000 AND SUM(DISTINCT_wkts.total_wkts) > 50;
        """),
        10: ("Last 20 completed matches", """
            SELECT match_desc, team1, team2, winning_team, victory_margin, victory_type, v.venue_name
            FROM matches m JOIN venues v ON v.venue_id = m.venue_id
            WHERE match_status = 'Completed'
            ORDER BY match_date DESC LIMIT 20;
        """),
        11: ("Player performance across formats (2+ formats)", """
            SELECT p.full_name,
                   SUM(CASE WHEN m.match_format='Test' THEN b.runs_scored ELSE 0 END) AS test_runs,
                   SUM(CASE WHEN m.match_format='ODI' THEN b.runs_scored ELSE 0 END) AS odi_runs,
                   SUM(CASE WHEN m.match_format='T20I' THEN b.runs_scored ELSE 0 END) AS t20i_runs,
                   ROUND(AVG(b.runs_scored), 2) AS overall_batting_average
            FROM batting_scorecard b
            JOIN players p ON p.player_id = b.player_id
            JOIN matches m ON m.match_id = b.match_id
            GROUP BY p.player_id
            HAVING COUNT(DISTINCT m.match_format) >= 2;
        """),
        12: ("Home vs away win performance", """
            SELECT m.winning_team AS team,
                   SUM(CASE WHEN v.country = m.winning_team THEN 1 ELSE 0 END) AS home_wins,
                   SUM(CASE WHEN v.country <> m.winning_team THEN 1 ELSE 0 END) AS away_wins
            FROM matches m JOIN venues v ON v.venue_id = m.venue_id
            WHERE m.winning_team <> 'Draw'
            GROUP BY m.winning_team ORDER BY home_wins + away_wins DESC;
        """),
        13: ("Partnerships (consecutive batters) with 100+ combined runs", """
            SELECT p1.full_name AS batter_1, p2.full_name AS batter_2,
                   (b1.runs_scored + b2.runs_scored) AS partnership_runs, b1.innings_no
            FROM batting_scorecard b1
            JOIN batting_scorecard b2 ON b1.match_id = b2.match_id AND b1.innings_no = b2.innings_no
                 AND b2.batting_position = b1.batting_position + 1
            JOIN players p1 ON p1.player_id = b1.player_id
            JOIN players p2 ON p2.player_id = b2.player_id
            WHERE (b1.runs_scored + b2.runs_scored) >= 100
            ORDER BY partnership_runs DESC;
        """),
        14: ("Bowling performance by venue (3+ matches at venue)", """
            SELECT p.full_name, v.venue_name,
                   ROUND(AVG(bw.economy_rate), 2) AS avg_economy,
                   SUM(bw.wickets_taken) AS total_wickets,
                   COUNT(DISTINCT bw.match_id) AS matches_at_venue
            FROM bowling_scorecard bw
            JOIN players p ON p.player_id = bw.player_id
            JOIN matches m ON m.match_id = bw.match_id
            JOIN venues v ON v.venue_id = m.venue_id
            WHERE bw.overs >= 4
            GROUP BY p.player_id, v.venue_id
            HAVING COUNT(DISTINCT bw.match_id) >= 3
            ORDER BY total_wickets DESC;
        """),
        15: ("Performance in close matches (<50 runs or <5 wickets)", """
            SELECT p.full_name,
                   ROUND(AVG(b.runs_scored), 2) AS avg_runs_in_close_matches,
                   COUNT(DISTINCT m.match_id) AS close_matches_played,
                   SUM(CASE WHEN m.winning_team = b.team THEN 1 ELSE 0 END) AS close_matches_won_batting
            FROM batting_scorecard b
            JOIN players p ON p.player_id = b.player_id
            JOIN matches m ON m.match_id = b.match_id
            WHERE (m.victory_type = 'runs' AND m.victory_margin < 50)
               OR (m.victory_type = 'wickets' AND m.victory_margin < 5)
            GROUP BY p.player_id ORDER BY avg_runs_in_close_matches DESC;
        """),
        16: ("Yearly batting trend since 2020 (min 5 matches/year)", """
            SELECT p.full_name, strftime('%Y', m.match_date) AS year,
                   ROUND(AVG(b.runs_scored), 2) AS avg_runs,
                   ROUND(AVG(b.strike_rate), 2) AS avg_strike_rate,
                   COUNT(DISTINCT b.match_id) AS matches_played
            FROM batting_scorecard b
            JOIN players p ON p.player_id = b.player_id
            JOIN matches m ON m.match_id = b.match_id
            WHERE m.match_date >= '2020-01-01'
            GROUP BY p.player_id, year
            HAVING COUNT(DISTINCT b.match_id) >= 5
            ORDER BY year, avg_runs DESC;
        """),
    },
    "Advanced": {
        17: ("Toss impact on match outcome", """
            SELECT toss_decision,
                   ROUND(100.0 * SUM(CASE WHEN toss_winner = winning_team THEN 1 ELSE 0 END) / COUNT(*), 2) AS win_pct_after_winning_toss,
                   COUNT(*) AS matches
            FROM matches WHERE winning_team <> 'Draw'
            GROUP BY toss_decision;
        """),
        18: ("Most economical limited-overs bowlers (10+ matches)", """
            SELECT p.full_name,
                   ROUND(SUM(bw.runs_conceded)*1.0 / NULLIF(SUM(bw.overs),0), 2) AS overall_economy,
                   SUM(bw.wickets_taken) AS total_wickets,
                   COUNT(DISTINCT bw.match_id) AS matches_played
            FROM bowling_scorecard bw
            JOIN players p ON p.player_id = bw.player_id
            JOIN matches m ON m.match_id = bw.match_id
            WHERE m.match_format IN ('ODI', 'T20I')
            GROUP BY p.player_id
            HAVING COUNT(DISTINCT bw.match_id) >= 10 AND AVG(bw.overs) >= 2
            ORDER BY overall_economy ASC;
        """),
        19: ("Most consistent batsmen since 2022 (min 10 balls/innings)", """
            WITH innings AS (
                SELECT p.player_id, p.full_name, b.runs_scored
                FROM batting_scorecard b
                JOIN players p ON p.player_id = b.player_id
                JOIN matches m ON m.match_id = b.match_id
                WHERE b.balls_faced >= 10 AND m.match_date >= '2022-01-01'
            )
            SELECT full_name, ROUND(AVG(runs_scored), 2) AS avg_runs,
                   ROUND(
                     SQRT(AVG(runs_scored*runs_scored) - AVG(runs_scored)*AVG(runs_scored))
                   , 2) AS std_dev_runs,
                   COUNT(*) AS innings_played
            FROM innings GROUP BY player_id
            HAVING COUNT(*) >= 5
            ORDER BY std_dev_runs ASC;
        """),
        20: ("Format-wise match count & batting average (20+ total matches)", """
            SELECT p.full_name,
                   COUNT(DISTINCT CASE WHEN m.match_format='Test' THEN b.match_id END) AS test_matches,
                   COUNT(DISTINCT CASE WHEN m.match_format='ODI' THEN b.match_id END) AS odi_matches,
                   COUNT(DISTINCT CASE WHEN m.match_format='T20I' THEN b.match_id END) AS t20i_matches,
                   ROUND(AVG(CASE WHEN m.match_format='Test' THEN b.runs_scored END), 2) AS test_avg,
                   ROUND(AVG(CASE WHEN m.match_format='ODI' THEN b.runs_scored END), 2) AS odi_avg,
                   ROUND(AVG(CASE WHEN m.match_format='T20I' THEN b.runs_scored END), 2) AS t20i_avg
            FROM batting_scorecard b
            JOIN players p ON p.player_id = b.player_id
            JOIN matches m ON m.match_id = b.match_id
            GROUP BY p.player_id
            HAVING COUNT(DISTINCT b.match_id) >= 20;
        """),
        21: ("Composite performance ranking (bat + bowl + field)", """
            WITH bat AS (
                SELECT player_id, SUM(runs_scored) AS runs, AVG(runs_scored) AS avg_runs, AVG(strike_rate) AS sr
                FROM batting_scorecard GROUP BY player_id
            ), bowl AS (
                SELECT player_id, SUM(wickets_taken) AS wkts,
                       SUM(runs_conceded)*1.0/NULLIF(SUM(wickets_taken),0) AS bowl_avg,
                       SUM(runs_conceded)*1.0/NULLIF(SUM(overs),0) AS econ
                FROM bowling_scorecard GROUP BY player_id
            )
            SELECT p.full_name,
                   ROUND(COALESCE(bat.runs,0)*0.01 + COALESCE(bat.avg_runs,0)*0.5 + COALESCE(bat.sr,0)*0.3, 2) AS batting_points,
                   ROUND(COALESCE(bowl.wkts,0)*2 + (50 - COALESCE(bowl.bowl_avg,50))*0.5 + (6 - COALESCE(bowl.econ,6))*2, 2) AS bowling_points,
                   ROUND(COALESCE(f.catches,0)*3 + COALESCE(f.stumpings,0)*5, 2) AS fielding_points
            FROM players p
            LEFT JOIN bat ON bat.player_id = p.player_id
            LEFT JOIN bowl ON bowl.player_id = p.player_id
            LEFT JOIN fielding_stats f ON f.player_id = p.player_id
            ORDER BY (batting_points + bowling_points + fielding_points) DESC;
        """),
        22: ("Head-to-head analysis (5+ matches, last 3 years)", """
            SELECT team1, team2, COUNT(*) AS total_matches,
                   SUM(CASE WHEN winning_team = team1 THEN 1 ELSE 0 END) AS team1_wins,
                   SUM(CASE WHEN winning_team = team2 THEN 1 ELSE 0 END) AS team2_wins,
                   ROUND(AVG(victory_margin), 1) AS avg_victory_margin
            FROM matches
            WHERE match_date >= date((SELECT max(match_date) FROM matches), '-3 years')
            GROUP BY team1, team2
            HAVING COUNT(*) >= 5;
        """),
        23: ("Recent player form (last 10 innings)", """
            WITH ranked AS (
                SELECT b.player_id, p.full_name, b.runs_scored, b.strike_rate,
                       ROW_NUMBER() OVER (PARTITION BY b.player_id ORDER BY m.match_date DESC) AS rn
                FROM batting_scorecard b
                JOIN players p ON p.player_id = b.player_id
                JOIN matches m ON m.match_id = b.match_id
            )
            SELECT full_name,
                   ROUND(AVG(CASE WHEN rn <= 5 THEN runs_scored END), 2) AS avg_last_5,
                   ROUND(AVG(CASE WHEN rn <= 10 THEN runs_scored END), 2) AS avg_last_10,
                   ROUND(AVG(CASE WHEN rn <= 10 THEN strike_rate END), 2) AS recent_strike_rate,
                   SUM(CASE WHEN rn <= 10 AND runs_scored >= 50 THEN 1 ELSE 0 END) AS scores_above_50,
                   CASE
                     WHEN AVG(CASE WHEN rn <= 10 THEN runs_scored END) >= 45 THEN 'Excellent Form'
                     WHEN AVG(CASE WHEN rn <= 10 THEN runs_scored END) >= 30 THEN 'Good Form'
                     WHEN AVG(CASE WHEN rn <= 10 THEN runs_scored END) >= 15 THEN 'Average Form'
                     ELSE 'Poor Form'
                   END AS form_category
            FROM ranked WHERE rn <= 10
            GROUP BY player_id
            ORDER BY avg_last_10 DESC;
        """),
        24: ("Best batting partnerships (5+ partnerships)", """
            SELECT p1.full_name AS batter_1, p2.full_name AS batter_2,
                   ROUND(AVG(b1.runs_scored + b2.runs_scored), 2) AS avg_partnership_runs,
                   SUM(CASE WHEN (b1.runs_scored + b2.runs_scored) > 50 THEN 1 ELSE 0 END) AS partnerships_over_50,
                   MAX(b1.runs_scored + b2.runs_scored) AS highest_partnership,
                   COUNT(*) AS total_partnerships,
                   ROUND(100.0 * SUM(CASE WHEN (b1.runs_scored + b2.runs_scored) > 50 THEN 1 ELSE 0 END) / COUNT(*), 2) AS success_rate_pct
            FROM batting_scorecard b1
            JOIN batting_scorecard b2 ON b1.match_id = b2.match_id AND b1.innings_no = b2.innings_no
                 AND b2.batting_position = b1.batting_position + 1
            JOIN players p1 ON p1.player_id = b1.player_id
            JOIN players p2 ON p2.player_id = b2.player_id
            GROUP BY b1.player_id, b2.player_id
            HAVING COUNT(*) >= 5
            ORDER BY avg_partnership_runs DESC;
        """),
        25: ("Quarterly performance trajectory", """
            WITH quarterly AS (
                SELECT p.player_id, p.full_name,
                       strftime('%Y', m.match_date) || '-Q' ||
                         ((CAST(strftime('%m', m.match_date) AS INTEGER) - 1) / 3 + 1) AS quarter,
                       AVG(b.runs_scored) AS avg_runs, AVG(b.strike_rate) AS avg_sr,
                       COUNT(*) AS matches_in_quarter
                FROM batting_scorecard b
                JOIN players p ON p.player_id = b.player_id
                JOIN matches m ON m.match_id = b.match_id
                GROUP BY p.player_id, quarter
                HAVING COUNT(*) >= 3
            ),
            trajectory AS (
                SELECT player_id, full_name, quarter, avg_runs,
                       LAG(avg_runs) OVER (PARTITION BY player_id ORDER BY quarter) AS prev_avg_runs,
                       COUNT(*) OVER (PARTITION BY player_id) AS n_quarters
                FROM quarterly
            )
            SELECT full_name, COUNT(*) AS quarters_tracked,
                   ROUND(AVG(avg_runs), 2) AS overall_avg_runs,
                   CASE
                     WHEN AVG(avg_runs - COALESCE(prev_avg_runs, avg_runs)) > 3 THEN 'Career Ascending'
                     WHEN AVG(avg_runs - COALESCE(prev_avg_runs, avg_runs)) < -3 THEN 'Career Declining'
                     ELSE 'Career Stable'
                   END AS career_phase
            FROM trajectory
            WHERE n_quarters >= 6
            GROUP BY player_id;
        """),
    },
}
