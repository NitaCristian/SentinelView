import cv2
from flask import Blueprint, render_template, request, redirect, url_for, session, Response
import requests
from datetime import datetime, timedelta

routes = Blueprint('routes', __name__)

API_BASE_URL = "http://127.0.0.1:5001/api"


@routes.route('/')
def home():
    # Fetch events from the API
    response = requests.get(f"{API_BASE_URL}/events")
    events = response.json() if response.status_code == 200 else []

    # Filter events from the last 24 hours
    now = datetime.now()
    recent_events = [
        event for event in events
        if datetime.strptime(event['date'], '%Y-%m-%d %H:%M:%S') >= now - timedelta(hours=24)
    ]

    return render_template('index.html', recent_events=recent_events, recent_events_count=len(recent_events))


@routes.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('routes.home'))


@routes.route('/browse-events')
def browse_events():
    if 'user' not in session:
        return redirect(url_for('routes.login'))

    # Fetch all events from the API
    response = requests.get(f"{API_BASE_URL}/get_events")
    events = response.json()['events'] if response.status_code == 200 else []

    return render_template('browse_events.html', events=events)


@routes.route('/event/<int:event_id>', methods=['GET'])
def event_details(event_id):
    if 'user' not in session:
        return redirect(url_for('routes.login'))

    # Fetch event details from the API
    response_event = requests.get(f"{API_BASE_URL}/get_event_details/{event_id}")
    event = response_event.json() if response_event.status_code == 200 else {}

    # If event details are fetched successfully, fetch the associated footage
    if event:
        footage_id = event.get('footage_id')
        if footage_id:
            response_footage = requests.get(f"{API_BASE_URL}/get_footage_details/{footage_id}")
            footage = response_footage.json() if response_footage.status_code == 200 else None
        else:
            footage = None
    else:
        footage = None

    # Render a template with the event details, including the footage
    return render_template('event_details.html', event=event, footage=footage)


@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        response = requests.post(f"{API_BASE_URL}/login", json={'username': username, 'password': password})
        if response.status_code == 200:
            token = response.json().get('token')
            session['user'] = {'username': username, 'token': token}
            return redirect(url_for('routes.home'))
        else:
            return render_template('login.html', message="Invalid credentials")

    return render_template('login.html')


@routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        response = requests.post(f"{API_BASE_URL}/register",
                                 json={'username': username, 'email': email, 'password': password})
        if response.status_code == 201:
            return redirect(url_for('routes.login'))
        else:
            return render_template('register.html', message="Registration failed")

    return render_template('register.html')


@routes.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' not in session:
        return redirect(url_for('routes.login'))

    user = session['user']
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        response = requests.post(f"{API_BASE_URL}/user",
                                 json={'username': username, 'email': email},
                                 headers={'Authorization': f"{user['token']}"})
        if response.status_code == 200:
            user['username'] = username
            session['user'] = user
            return redirect(url_for('routes.profile'))
        else:
            # Handle error, e.g., display error message
            pass  # Placeholder for error handling

    response = requests.get(f"{API_BASE_URL}/user", headers={'Authorization': f"{user['token']}"})
    if response.status_code == 200:
        user_info = response.json()
        return render_template('profile.html', user=user_info)

    return redirect(url_for('routes.login'))


@routes.route('/live-feed')
def live_feed():
    if 'user' not in session:
        return redirect(url_for('routes.login'))

    return render_template('live_feed.html')


@routes.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# Generate frames for live video feed
def generate_frames():
    while True:
        success, frame = False, False#camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'


#camera = cv2.VideoCapture()
