from google.cloud import bigquery


def main(event, context):
    client = bigquery.Client()
    query = f"""
                SELECT * except (payload, deleted, deleted_at, deleted_reviewed)
                FROM mlb_alphabet_game.tweetable_plays
                where deleted = false
                order by completed_at desc limit 50
            """
    results = client.query(query).result()
    return list(results)


# main(None, None)