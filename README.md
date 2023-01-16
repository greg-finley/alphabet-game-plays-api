# alphabet-game-plays-api

Cloud function to serve the data behind https://github.com/greg-finley/mlb-alphabet-game

# API

The tweeted plays are available from this API endpoint:

```shell
curl 'https://us-central1-greg-finley.cloudfunctions.net/alphabet-game-plays-api'
```

With the following optional query parameters:

- `limit`: How many tweets. If not specific, the max is 1000. Put 0 to get all tweets.
- `matches_only`: "true" to ignore tweets where player's name doesn't match the next letter
- `sport`: NFL, NHL, MLB, or NBA.
- `before_ts`: Tweets with `completed_at` before a certain epoch time. Use the `completed_at` value from the last tweet in the current results page to get the preceeding tweets.
- `lite`: "true" to omit some columns that are not needed by the website.

i.e. to get 2 tweets about the NFL from before 1667525177 that were matches, run:

```shell
curl 'https://us-central1-greg-finley.cloudfunctions.net/alphabet-game-plays-api?matches_only=true&limit=2&sport=NFL&before_ts=1667525177'
```
