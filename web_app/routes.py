import cv2
from flask import Blueprint, render_template, Response, request, redirect, url_for

routes = Blueprint('routes', __name__)

camera = cv2.VideoCapture(0)


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
