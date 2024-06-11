import cv2
from flask import Blueprint, render_template, Response, request, redirect, url_for, session
import requests

routes = Blueprint('routes', __name__)

camera = cv2.VideoCapture(0)

API_URL = 'http://localhost:5000/api'  # Update this with your API URL


def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@routes.route('/')
def home():
    clips = [
        {'id': 'CLP-123', 'description': 'Intruder detected in Living Room', 'camera': 'Cam1', 'date': 'Dec 5'},
        {'id': 'CLP-122', 'description': 'Intruder detected at Front Door', 'camera': 'Cam2', 'date': 'Dec 5'},
        {'id': 'CLP-121', 'description': 'Intruder detected in Living Room', 'camera': 'Cam1', 'date': 'Dec 5'}
    ]
    return render_template('index.html', clips=clips)


@routes.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        # Process the form data here (e.g., save to database)
        return redirect(url_for('routes.profile'))

    user = {
        'name': 'Helena Hills',
        'username': 'username123',
        'email': 'email@domain.com',
        'profile_photo': 'https://via.placeholder.com/80'  # Placeholder URL
    }
    return render_template('profile.html', user=user)


@routes.route('/live-feed')
def live_feed():
    return render_template('live_feed.html')


@routes.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        data = {'username': username, 'email': email, 'password': password}
        response = requests.post(f'{API_URL}/register', json=data)
        if response.status_code == 200:
            return redirect(url_for('routes.login'))
        else:
            return render_template('register.html', message='Registration failed. Please try again.')
    return render_template('register.html')


@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        data = {'username': username, 'password': password}
        response = requests.post(f'{API_URL}/login', json=data)
        if response.status_code == 200:
            session['token'] = response.json()['token']
            return redirect(url_for('routes.home'))
        else:
            return render_template('login.html', message='Invalid credentials. Please try again.')
    return render_template('login.html')


@routes.route('/logout')
def logout():
    session.pop('token', None)
    return redirect(url_for('routes.home'))
