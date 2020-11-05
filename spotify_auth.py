import base64, json, requests, os


class SpotifyAuth(object):
    SPOTIFY_URL_AUTH = "https://accounts.spotify.com/authorize/"
    SPOTIFY_URL_TOKEN = "https://accounts.spotify.com/api/token/"
    RESPONSE_TYPE = "code"
    HEADER = "application/x-www-form-urlencoded"
    CLIENT_ID = os.environ.get("CLIENT_ID")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    CALLBACK_URL = "http://localhost:5000/auth"
    SCOPE = "user-read-email user-read-private"

    def getAuth(self, client_id, redirect_uri, scope):
        return (
            f"{self.SPOTIFY_URL_AUTH}"
            f"?client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={scope}"
            "&response_type=code"
        )

    def getToken(self, client_id, client_secret, redirect_uri):
        body = {
            "grant_type": "client_credentials",
        }

        encoded = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        headers = {
            "Content-Type": self.HEADER,
            "Authorization": f"Basic {encoded}",
        }

        post = requests.post(self.SPOTIFY_URL_TOKEN, data=body, headers=headers)
        return self.handleToken(json.dumps(post.json()))

    def handleToken(self, response):
        dict_data = json.loads(response)
        if "error" in dict_data:
            return response
        return {
            "access_token": dict_data["access_token"],
            "expires_in": dict_data["expires_in"],
        }

    def getUserToken(self):
        return self.getToken(
            self.CLIENT_ID, self.CLIENT_SECRET, f"{self.CALLBACK_URL}/callback"
        )
