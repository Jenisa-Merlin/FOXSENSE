from flask import Flask, session, redirect, url_for, abort, request
import os
import pathlib
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
from google.oauth2 import id_token
from pip._vendor import cachecontrol
import requests

def setupRoutes(app):
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    GOOGLE_CLIENT_ID = '314075154272-vjvt3bget3bu7snpg868hl5j2rk5i84s.apps.googleusercontent.com'
    client_secrets_file = os.path.join(pathlib.Path(__file__).parent,'client_secret.json')

    flow = Flow.from_client_secrets_file(
        client_secrets_file=client_secrets_file,
        scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
        redirect_uri="http://127.0.0.1:5000/callback")
    
    def loginRequired(function):
        def wrapper(*args, **kwargs):
            if 'google_id' not in session:
                return abort(401)
            else:
                return function()
        return wrapper

    @app.route('/')
    def index():
        return "<a href='/login'>Login</a><a href='/logout'>Logout</a>"

    @app.route('/login')
    def login():
        authorization_url, state = flow.authorization_url()
        session["state"] = state
        return redirect(authorization_url)

    @app.route('/callback')
    def callback():
        flow.fetch_token(authorization_response=request.url)
        if not session["state"] == request.args["state"]:
            abort(500)
        
        credentials = flow.credentials
        request_session = requests.session()
        cached_session = cachecontrol.CacheControl(request_session)
        token_request = google.auth.transport.requests.Request(session=cached_session)

        id_info = id_token.verify_oauth2_token(id_token=credentials._id_token, request=token_request, audience=GOOGLE_CLIENT_ID)

        session["google_id"] = id_info.get("sub")
        session["name"] = id_info.get("name")
        return redirect("/protected_area")
    
    @app.route('/logout')
    def logout():
        session.clear()
        return redirect('/')

    @app.route('/protected_area')
    @loginRequired
    def protected_area():
        return f"Hello {session['name']}<a href='/logout'>Logout</a>"