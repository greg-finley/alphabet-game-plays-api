import functions_framework
from google.cloud import bigquery


@functions_framework.http
def main(request):
    client = bigquery.Client()
    query = """
                SELECT * except
                (payload, deleted, deleted_at, deleted_reviewed, completed_at),
                unix_seconds(completed_at) completed_at
                FROM mlb_alphabet_game.tweetable_plays
                where deleted = false
                order by completed_at desc limit 50
            """
    results = client.query(query).result()
    return (
        {"data": [dict(r.items()) for r in results]},
        200,
        {"Content-Type": "application/json"},
    )


# print(main(None))
