import os

import cv2
from flask import Blueprint, render_template, request, redirect, url_for, session, Response
import requests
from datetime import datetime, timedelta
from collections import Counter

routes = Blueprint('routes', __name__)
ANALYSES_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'analyses'))
API_BASE_URL = "http://127.0.0.1:5001/api"


@routes.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('routes.login'))

    # Fetch events from the API
    response = requests.get(f"{API_BASE_URL}/events")
    events = response.json() if response.status_code == 200 else []

    # Filter events from the last 24 hours
    now = datetime.now()
    recent_events = [
        event for event in events
        if datetime.strptime(event['date'], '%Y-%m-%d %H:%M:%S') >= now - timedelta(hours=24)
    ]

    # Generate dates for the last two weeks
    today = now.date()
    dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(13, -1, -1)]

    # Initialize a Counter for event counts per day
    event_counts_dict = Counter(
        datetime.strptime(event['date'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        for event in events if
        datetime.strptime(event['date'], '%Y-%m-%d %H:%M:%S').date() in [today - timedelta(days=i) for i in range(14)]
    )

    # Create a list of event counts corresponding to the `dates` list
    event_counts = [event_counts_dict.get(date, 0) for date in dates]

    return render_template('index.html',
                           recent_events=recent_events,
                           recent_events_count=len(recent_events),
                           dates=dates,
                           event_counts=event_counts)


@routes.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user', None)
    return redirect(url_for('routes.home'))


@routes.route('/browse-events')
def browse_events():
    if 'user' not in session:
        return redirect(url_for('routes.login'))

    # Fetch all events from the API
    response = requests.get(f"{API_BASE_URL}/get_events")
    events = response.json()['events'] if response.status_code == 200 else []
    events.sort(key=lambda x: x['timestamp'], reverse=True)

    return render_template('browse_events.html', events=events)


@routes.route('/event/<int:event_id>', methods=['GET'])
def event_details(event_id):
    if 'user' not in session:
        return redirect(url_for('routes.login'))

    # Fetch event details from the API
    response_event = requests.get(f"{API_BASE_URL}/get_event_details/{event_id}")
    event = response_event.json() if response_event.status_code == 200 else {}

    # If event details are fetched successfully, fetch the associated footage
    video_url = ''
    analysis = ''
    if event:
        footage_id = event.get('footage_id')
        if footage_id:
            response_footage = requests.get(f"{API_BASE_URL}/get_footage_details/{footage_id}")
            footage_path = response_footage.json() if response_footage.status_code == 200 else None
            video_url = url_for('routes.get_analysis_file', filename=footage_path['file_path'])
            base_name = os.path.splitext(footage_path['file_path'])[0].rsplit('_', 1)[0]
            new_filename = f"{base_name}_summary.txt"
            analysis_path = os.path.join(ANALYSES_FOLDER, new_filename)
            with open(analysis_path, 'r') as file:
                analysis = file.read()

        else:
            footage = None
    else:
        footage = None

    # Render a template with the event details, including the footage
    return render_template('event_details.html', event=event, video_url=video_url, analysis=analysis)


@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        response = requests.post(f"{API_BASE_URL}/login", json={'username': username, 'password': password})
        if response.status_code == 200:
            token = response.json().get('token')
            session['user'] = {'username': username, 'token': token, 'profile_photo': response.json().get('profile_photo')}
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
        # Handle profile update
        username = request.form.get('username')
        email = request.form.get('email')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        current_password = request.form.get('current_password')
        profile_picture = request.files.get('profile_picture')

        if new_password and (new_password != confirm_password):
            # Handle password mismatch error
            return render_template('profile.html', user=user, error="Passwords do not match")

        if current_password:
            # Validate current password if changing password
            response = requests.post(f"{API_BASE_URL}/validate_password",
                                     json={'password': current_password},
                                     headers={'Authorization': f"{user['token']}"})
            if response.status_code != 200:
                # Handle current password validation error
                return render_template('profile.html', user=user, error="Current password is incorrect")

        if username and username != user['username'] or email and email != user['email'] or new_password:
            user_update_payload = {'username': username, 'email': email}
            if new_password:
                user_update_payload['password'] = new_password

            response = requests.post(f"{API_BASE_URL}/user",
                                     json=user_update_payload,
                                     headers={'Authorization': f"{user['token']}"})
            if response.status_code == 200:
                user['username'] = username
                user['email'] = email
                if new_password:
                    # Log the user out if password changed (optional)
                    session.pop('user', None)
                    return redirect(url_for('routes.login'))

        # Handle profile picture upload
        if profile_picture:
            file = {'profile_picture': (profile_picture.filename, profile_picture.stream, profile_picture.content_type)}
            response = requests.post(f"{API_BASE_URL}/upload_profile_picture",
                                     files=file,
                                     headers={'Authorization': f"{user['token']}"})
            if response.status_code == 200:
                user['profile_photo'] = response.json().get('profile_photo_url')
            else:
                # Handle error
                return render_template('profile.html', user=user, error="Failed to upload profile picture")

        session['user'] = user
        return redirect(url_for('routes.profile'))

    response = requests.get(f"{API_BASE_URL}/user", headers={'Authorization': f"{user['token']}"})
    if response.status_code == 200:
        user_info = response.json()
        print(user_info)
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
        success, frame = False, False  # camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'

# camera = cv2.VideoCapture()
