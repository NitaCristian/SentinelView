import cv2
from flask import Flask, render_template, request, redirect, url_for, Response

app = Flask(__name__)

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


@app.route('/')
def home():
    clips = [
        {'id': 'CLP-123', 'description': 'Intruder detected in Living Room', 'camera': 'Cam1', 'date': 'Dec 5'},
        {'id': 'CLP-122', 'description': 'Intruder detected at Front Door', 'camera': 'Cam2', 'date': 'Dec 5'},
        {'id': 'CLP-121', 'description': 'Intruder detected in Living Room', 'camera': 'Cam1', 'date': 'Dec 5'}
    ]
    return render_template('index.html', clips=clips)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        return redirect(url_for('profile'))

    user = {
        'name': 'Helena Hills',
        'username': 'username123',
        'email': 'email@domain.com',
        'profile_photo': 'path/to/profile/photo.jpg'  # Placeholder path
    }
    return render_template('profile.html', user=user)


@app.route('/live-feed')
def live_feed():
    return render_template('live_feed.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)
