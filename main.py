from flask import Flask, redirect, request, jsonify, session, render_template
import requests
import urllib.parse
from datetime import datetime, timedelta
import base64
import json
import openai
import os



app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = "33d543126-671j0-132-r432-1o9543879"

openai.api_key = f"{os.getenv(openai_key)}"
CLIENT_ID = '830fb209bc8b452bb337ab47f6eca95b'
CLIENT_SECRET = '62cde0ae0c7845b5bf0a4d4d2bd1695c'
REDIRECT_URL = "https://spotify-descry.onrender.com/callback"


AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1"
conversation = []


@app.route('/')
def index():
    playlist = []
    return render_template('index.html', title = "spotify", background_class="background-with-image", playlist =playlist)
@app.route('/login')
def login():
    scope = "user-top-read user-read-email"

    params ={
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'scope':scope,
        'redirect_uri': REDIRECT_URL,
        'show_dialog': True
        
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

    return json.dumps({"auth_url": auth_url})

@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({"error:": request.args['error']})

    if 'code' in request.args:
        req_body = {
        'code': request.args['code'],
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URL,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        }
        client_credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
        encoded = base64.b64encode(client_credentials.encode()).decode()    
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic " + encoded
        }
        response = requests.post(TOKEN_URL, data=req_body, headers=headers)
        response.raise_for_status()
        token_info = response.json()
        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_in'] = datetime.now().timestamp() + token_info['expires_in']
    

        return redirect('/recomendation')
@app.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_in']:
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
        }
        client_credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
        encoded = base64.b64encode(client_credentials.encode()).decode() 
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic " + encoded
        }

        response = requests.post(TOKEN_URL, data=req_body, headers=headers)
        new_token_info = response.json()


        session['access_token'] = new_token_info['access_token']
        session['expires_in'] = datetime.now().timestamp() + new_token_info['expires_in']


        return redirect('/recomendation')
    
  

@app.route('/recomendation')
def get_songs():
    if 'access_token' not in session:
        return redirect('/login')
        
    if datetime.now().timestamp() > session['expires_in']:
        return redirect('/refresh-token')
    
    headers ={
        'Authorization' : f"Bearer {session['access_token']}"

    }

    response = requests.get(f'{API_BASE_URL}/me/top/tracks?time_range=short_term&limit=5&offset=0', headers=headers)
    response.raise_for_status()
    songs = response.json()
    songs_id = []
    for n in range(0,5):
        songs_id.append(songs["items"][n]['id'])
    session['songs_id'] = ','.join(songs_id)
    response2 = requests.get(f'{API_BASE_URL}/recommendations?limit=16&seed_tracks={session["songs_id"]}', headers=headers)
    recommendation = response2.json()
    playlist= []
    for n in range(0,15):
        gray = {}
        gray['link'] = (recommendation['tracks'][n]['external_urls']['spotify'])
        gray['name'] = (recommendation['tracks'][n]['artists'][0]['name']) + ' '+ (recommendation['tracks'][n]['name'])
        gray['image_src'] = (recommendation['tracks'][n]['album']['images'][0]['url'])
        playlist.append(gray)



    return render_template('logged_in.html', playlist=playlist, background_class="background-no-image")


@app.route('/ai')
def create_ai():
    return render_template("ai_search.html", background_class="background-no-image")



@app.route('/ai-search', methods=['POST'])
def ai():
    if request.method == 'POST':
        user_message = request.json.get('message')

       
        conversation.append({'role': 'user', 'content': user_message})

        
        system_content = "You are a spotify music helper. You only anwser the music related questions. You help the user find some new genres or songs he might like.On every other question you respond with: Sorry.im not made to handle this kind of questions!. "\

        
        messages = [
            {"role": "system", "content": system_content}
        ]

        
        for message in conversation:
            messages.append({"role": message['role'], "content": message['content']})

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
        )

        bot_message = response.choices[0].message['content']

       
        conversation.append({'role': 'assistant', 'content': bot_message})

        return jsonify({'message': bot_message})




    
    

if __name__ == '__main__':
    
    app.run(host='0.0.0.0', debug=True)

