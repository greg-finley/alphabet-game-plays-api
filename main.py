import functions_framework
from google.cloud import bigquery


@functions_framework.http
def main(request):
    limit = request.args.get("limit", 50)
    limit = min(1000, int(limit))

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

    client = bigquery.Client()
    query = f"""
                SELECT * except
                (payload, deleted, deleted_at, deleted_reviewed, completed_at),
                unix_seconds(completed_at) completed_at,
                case when tweet_text like '%is still%' then false else true
                end as letter_match
                FROM mlb_alphabet_game.tweetable_plays
                where deleted = false {sport}
                order by completed_at desc limit {limit}
            """
    results = client.query(query).result()
    return (
        {"data": [dict(r.items()) for r in results]},
        200,
        {"Content-Type": "application/json"},
    )


# print(main(None))
