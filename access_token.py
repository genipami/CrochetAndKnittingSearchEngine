# pip install requests requests-oauthlib
import webbrowser
from requests_oauthlib import OAuth1Session
from urllib.parse import parse_qs

CONSUMER_KEY = "15c948c58a84cc81c3cd01df60d40a28"
CONSUMER_SECRET = "uqlkk_iRsKsluJHDEyJABKcLsutsxupvWjduE38M"

REQUEST_TOKEN_URL = "https://www.ravelry.com/oauth/request_token"
AUTHORIZE_URL     = "https://www.ravelry.com/oauth/authorize"
ACCESS_TOKEN_URL  = "https://www.ravelry.com/oauth/access_token"

CALLBACK_URI = "http://127.0.0.1:9876/callback" 

# 1) Obtain an unauthorized request token, *including* oauth_callback
oauth = OAuth1Session(CONSUMER_KEY, client_secret=CONSUMER_SECRET, callback_uri=CALLBACK_URI)
fetch_resp = oauth.fetch_request_token(REQUEST_TOKEN_URL)  # adds oauth_callback under the hood
resource_owner_key = fetch_resp.get("oauth_token")
resource_owner_secret = fetch_resp.get("oauth_token_secret")

# 2) Send the user to authorize
auth_url = oauth.authorization_url(AUTHORIZE_URL)  # ?oauth_token=...
print("Open this URL and approve:", auth_url)
webbrowser.open(auth_url)

# 3) Capture the callback (run a tiny HTTP server to read the query string)
# For simplicity, paste the full callback URL after approval:
redirect_resp = input("Paste the full callback URL: ").strip()

# 4) Exchange request token + verifier for access token
oauth = OAuth1Session(
    CONSUMER_KEY,
    client_secret=CONSUMER_SECRET,
    resource_owner_key=resource_owner_key,
    resource_owner_secret=resource_owner_secret,
    verifier=parse_qs(redirect_resp.split("?", 1)[1])["oauth_verifier"][0]
)
tokens = oauth.fetch_access_token(ACCESS_TOKEN_URL)
ACCESS_TOKEN        = tokens["oauth_token"]
ACCESS_TOKEN_SECRET = tokens["oauth_token_secret"]
print("Access token:", ACCESS_TOKEN)
print("Access secret:", ACCESS_TOKEN_SECRET)
