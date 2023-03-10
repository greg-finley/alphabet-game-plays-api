import os

import functions_framework
import MySQLdb
from dotenv import load_dotenv


@functions_framework.http
def main(request):
    load_dotenv()
    limit = int(request.args.get("limit", 50))
    if limit == 0:
        limit = ""
    else:
        limit = f"limit {min(1000, int(limit))}"

    matches_only = request.args.get("matches_only", "false")
    if matches_only not in ["true", "false"]:
        return (
            {"error": "Invalid matches_only. Must be true or false."},
            400,
            {"Content-Type": "application/json"},
        )
    if matches_only == "true":
        matches_only = "AND letter_match = true"
    else:
        matches_only = ""

    lite = request.args.get("lite", "false")
    if lite not in ["true", "false"]:
        return (
            {"error": "Invalid lite. Must be true or false."},
            400,
            {"Content-Type": "application/json"},
        )

    sport = request.args.get("sport")
    if sport and sport not in ["NBA", "MLB", "NFL", "NHL"]:
        return (
            {"error": "Invalid sport. Options are: NHL, NBA, MLB, and NFL."},
            400,
            {"Content-Type": "application/json"},
        )
    if sport:
        sport = f" AND sport = '{sport}'"
    else:
        sport = ""

    before_ts = request.args.get("before_ts")
    if before_ts:
        if not before_ts.isdigit():
            return (
                {"error": "Invalid before_ts. Must be an integer timestamp."},
                400,
                {"Content-Type": "application/json"},
            )
        before_ts = f" AND unix_timestamp(completed_at) < {before_ts}"
    else:
        before_ts = ""

    mysql_connection = MySQLdb.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USERNAME"),
        passwd=os.getenv("MYSQL_PASSWORD"),
        db=os.getenv("MYSQL_DATABASE"),
        ssl_mode="VERIFY_IDENTITY",
        ssl={
            "ca": os.environ.get("SSL_CERT_FILE", "/etc/ssl/certs/ca-certificates.crt")
        },
    )
    mysql_connection.autocommit(True)
    query = f"""
     SELECT *, case when letter_match = true then 
     SUBSTRING_INDEX(SUBSTRING_INDEX(tweet_text, 'name', -1), '.', 1)
     else null end as matching_letters
     from (
                SELECT `game_id`, `play_id`, `sport`, `player_name`, `season_phrase`, `season_period`, `next_letter`, `times_cycled`, `score`, `tweet_text`, `player_id`, `team_id`,
                unix_timestamp(completed_at) completed_at,
                cast(tweet_id as char) tweet_id,
                completed_at_pacific,
                letter_match
                from
                (select *,  case when tweet_text like '%is still%' then false else true
                end as letter_match,
                cast(CONVERT_TZ(completed_at, 'UTC', 'America/Los_Angeles') as char) as completed_at_pacific
                FROM tweetable_plays) a
                where 1 = 1 {sport} {before_ts} {matches_only}
                order by completed_at desc {limit}
            ) b
            """
    print(query)
    mysql_connection.query(query)
    r = mysql_connection.store_result()
    rows = []
    for row in r.fetch_row(maxrows=0, how=1):
        row["matching_letters"] = (
            [c for c in row["matching_letters"] if c.isupper()]
            if row["matching_letters"]
            else []
        )
        if lite == "true":
            row.pop("game_id")
            row.pop("play_id")
            row.pop("score")
            row.pop("season_period")
            row.pop("completed_at_pacific")

        rows.append(row)
    return (
        {"data": rows},
        200,
        {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
    )


class Request:
    def __init__(self, args):
        self.args = args


# request = Request({"limit": 1, "matches_only": "true", "lite": "true"})


# print(main(request))
