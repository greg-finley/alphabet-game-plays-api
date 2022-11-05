import functions_framework
from google.cloud import bigquery


@functions_framework.http
def main(request):
    limit = request.args.get("limit", 50)
    limit = min(1000, int(limit))

    client = bigquery.Client()
    query = f"""
                SELECT * except
                (payload, deleted, deleted_at, deleted_reviewed, completed_at),
                unix_seconds(completed_at) completed_at,
                case when tweet_text like '%is still%' then false else true
                end as letter_match
                FROM mlb_alphabet_game.tweetable_plays
                where deleted = false
                order by completed_at desc limit {limit}
            """
    results = client.query(query).result()
    return (
        {"data": [dict(r.items()) for r in results]},
        200,
        {"Content-Type": "application/json"},
    )


# print(main(None))
