from flask import Flask, request, jsonify, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import func, desc, exc
from datetime import datetime, timedelta, date

import json
import time
import requests

from spotify_auth import SpotifyAuth

app = Flask(__name__)
db = SQLAlchemy()
sess = Session()
ma = Marshmallow()

app.config.from_object("config.Config")

db.init_app(app)
sess.init_app(app)
ma.init_app(app)

spotify_auth = SpotifyAuth()


class Release(db.Model):
    release_spotify_id = db.Column(db.String, primary_key=True)
    release_name = db.Column(db.String, nullable=False)
    release_release_date = db.Column(db.Date, primary_key=False, nullable=False)
    release_total_tracks = db.Column(db.Integer, nullable=False)
    release_url = db.Column(db.String, nullable=False)
    release_from_artist = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())

    def __init__(
        self,
        release_spotify_id,
        release_name,
        release_release_date,
        release_total_tracks,
        release_url,
        release_from_artist,
    ):
        self.release_spotify_id = release_spotify_id
        self.release_name = release_name
        self.release_release_date = release_release_date
        self.release_total_tracks = release_total_tracks
        self.release_url = release_url
        self.release_from_artist = release_from_artist

    def toJson(self):
        return json.dumps(self, default=lambda obj: obj.__dict__)


class ReleaseSchema(ma.Schema):
    class Meta:
        fields = (
            "release_spotify_id",
            "release_name",
            "release_release_date",
            "release_total_tracks",
            "release_url",
            "release_from_artist",
        )


release_schema = ReleaseSchema()
releases_schema = ReleaseSchema(many=True)


def get_date_from_string(date_string):
    return datetime.strptime(date_string, "%Y-%m-%d")


def is_data_fetch_was_one_day_ago():
    last_fetch_date_str = session.get("last_data_fetch_date")
    if last_fetch_date_str is None:
        return True
    last_fetch_date = datetime.strptime(last_fetch_date_str, "%Y-%m-%d")

    data_fetch_was_last_day_or_before = last_fetch_date.date() <= (
        date.today() - timedelta(days=1)
    )

    return data_fetch_was_last_day_or_before


def get_artists_query():
    all_releases = Release.query.order_by(desc(Release.release_release_date)).all()
    result = releases_schema.dump(all_releases)
    return jsonify(result)


def update_fetch_date():
    now = datetime.now()
    session["last_data_fetch_date"] = now.strftime("%Y-%m-%d")


def set_auth_data_to_session(tokens_info):
    print("💾 set_auth_data_to_session", tokens_info)
    data = json.dumps(tokens_info)
    data_dict = json.loads(data)

    if "error" in data_dict:
        print("error in tokens info, cannot create a session")
        return False
    session["access_token"] = data_dict["access_token"]
    session["expires_in"] = data_dict["expires_in"]
    session["refresh_token_at"] = time.time() + data_dict["expires_in"]
    return True


def setup_session_if_needed():
    access_token = session.get("access_token")
    if access_token is None:
        print("No session, get session from spotify ")

        tokens_info = spotify_auth.getUserToken()
        print("tokens_info", tokens_info)
        set_auth_data_to_session(tokens_info)
    elif session.get("refresh_token_at") <= time.time():
        tokens_info = spotify_auth.getUserToken()
        set_auth_data_to_session(tokens_info)


def add_album_releases_to_db(album_releases):
    releases_obj = []

    for album_with_artists in album_releases:
        new_release = Release(
            album_with_artists["id"],
            album_with_artists["name"],
            get_date_from_string(album_with_artists["release_date"]),
            album_with_artists["total_tracks"],
            album_with_artists["external_urls"]["spotify"],
            album_with_artists["artists"][0]["name"],
        )
        releases_obj.append(new_release)

        for obj in releases_obj:
            assert obj not in session
            db.session.merge(obj)
        db.session.commit()


def get_artists_with_offset(next_url, request_header):
    request_result = requests.get(next_url, headers=request_header)
    request_json = json.loads(request_result.content)
    album_releases = request_json.get("albums").get("items")
    add_album_releases_to_db(album_releases)
    new_next_url = request_json.get("albums").get("next")
    if new_next_url:
        get_artists_with_offset(new_next_url, request_header)
    else:
        return


@app.route("/api/artists/", methods=["GET"])
def get_artists():
    if not is_data_fetch_was_one_day_ago():
        print("Data fetch was today !")
        return get_artists_query()

    update_fetch_date()
    setup_session_if_needed()
    access_token = session.get("access_token")
    request_header = {"Authorization": "Bearer " + access_token}
    row_dict = {"offset": u"0", "limit": u"50"}
    url_call = (
        "https://api.spotify.com/v1/browse/new-releases?offset={0}&limit={1}".format(
            row_dict["offset"], row_dict["limit"]
        )
    )
    request_result = requests.get(url_call, headers=request_header)
    request_json = json.loads(request_result.content)
    album_releases = request_json.get("albums").get("items")

    add_album_releases_to_db(album_releases)

    next_url = request_json.get("albums").get("next")
    if next_url:
        get_artists_with_offset(next_url, request_header)
    return get_artists_query()


# Run server
if __name__ == "__main__":
    app.run(debug=True)
