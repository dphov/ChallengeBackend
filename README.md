# ChallengeBackend

Your goal is to create an app using the [spotify web api](https://developer.spotify.com/documentation/web-api/). You can make for example a [Flask](https://flask.palletsprojects.com/en/1.1.x/) or [Django rest framework](https://www.django-rest-framework.org/) project, it has to be able to authenticate to Spotify to fetch the new releases. Your job is to add two new features:
- A way to fetch data from spotify’s new releases API (/v1/browse/new-releases) and persist in a Postgresql DB (mandatory)
- A route : `/api/artists/` returning a JSON containing informations about artists that have released new tracks recently, from your local copy of today’s spotify’s new releases.

## Project Structure
The spotify auth is provided by us: (follows spotify web api.): it is located in `spotify_auth.py`.
The flow ends with a call to `/auth/callback/` which will give you the necessary access tokens.
To use it, we will provide you with the necessary: CLIENT_ID and CLIENT_SECRET.
Feel free to move it and re-organise as you please, we expect a well organised and clean code. Keep in mind that we want an Authorization Code Flow to see how you handle user authorization.
  
  
## Tech Specifications
- Be smart in your token usage (no unnecessary refreshes)
- Don’t request spotify artists at each request we send you
- The way you store the artists in Postgresql DB is going to be important use an ORM.
- As stated above, to test your server we will `GET /api/artists/` and we expect a nicely organised payload of artists. Make sure to use proper serialization and handle http errors.

All stability, performance, efficiency adds-up are highly recommended.







## Pre-setup

Install redis, postgres, pipenv, python > 3.6


Please fill up your `.env` file before launch
You could find an example at `.env.example`

```
pip install pipenv
pipenv install
```

Run `init.py` to init database
```
python init.py
```

## Redis session keys

Redis is used as session storage for storing: 
- OAuth2 key in `access_token`
- Validity time in seconds in `expires_in`
- The time to refresh key in `refresh_token_at`
- Information about last data fetch from spotify in `last_data_fetch_date`


## Running instruction

```
python app.py
```


After first recieved request:

>DB will be populated with actual data from Spotify's `/v1/browse/new-releases` endpoint. And session keys will be set.

Every next request:
>System will check each if it have to update data from Spotify. It will look at date. If last update was more than 1 day, it will refetch the actual data in the moment then user will have a request.


### Example of response from `GET /api/artists/` request

```
[
  {
    "release_from_artist": "Petit Biscuit",
    "release_name": "Parachute",
    "release_release_date": "2020-10-30",
    "release_spotify_id": "3t4ZHswZdOfXd6TcZ51uHl",
    "release_total_tracks": 9,
    "release_url": "https://open.spotify.com/album/3t4ZHswZdOfXd6TcZ51uHl"
  },
  ...
]

```














