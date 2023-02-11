import functions_framework
from google.cloud import bigquery


@functions_framework.http
def main(request):
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
    if lite == "true":
        more_except_cols = (
            ", game_id, play_id, score, season_period, completed_at_pacific"
        )
        top_except = " except (letter_match, tweet_text) "
    else:
        more_except_cols = ""
        top_except = ""

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
        before_ts = f" AND unix_seconds(completed_at) < {before_ts}"
    else:
        before_ts = ""

    client = bigquery.Client()
    query = f"""
     SELECT *{top_except}, case when letter_match = true then 
     regexp_extract_all(regexp_extract(tweet_text, 'name[^.]*.'), "[A-Z]")
     else null end as matching_letters
     from (
                SELECT * except
                (payload, deleted, deleted_at, deleted_reviewed, completed_at, tweet_id {more_except_cols}),
                unix_seconds(completed_at) completed_at,
                cast(tweet_id as string) tweet_id
                from
                (select *,  case when tweet_text like '%is still%' then false else true
                end as letter_match,
                DATETIME(completed_at, "America/Los_Angeles") as completed_at_pacific
                FROM mlb_alphabet_game.tweetable_plays)
                where deleted = false {sport} {before_ts} {matches_only}
                order by completed_at desc {limit}
            )
            """
    results = client.query(query).result()
    return (
        {"data": [dict(r.items()) for r in results]},
        200,
        {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
    )


# print(main(None))
