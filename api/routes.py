from flask import Blueprint, jsonify, request
from models import User, Camera, Event, Footage, Notification, db
from auth import generate_token, decode_token
from datetime import datetime

api_bp = Blueprint('api', __name__)


@api_bp.route('/', methods=['GET'])
def greet_user():
    return jsonify({'message': 'Welcome to the API!'})


@api_bp.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    new_user = User(username=data['username'], email=data['email'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'})


@api_bp.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    user = User.query.filter_by(username=data['username'], password=data['password']).first()
    if user:
        token = generate_token(user.id)
        return jsonify({'token': token})
    else:
        return jsonify({'message': 'Invalid credentials'}), 401


@api_bp.route('/user', methods=['GET'])
def get_user_details():
    token = request.headers.get('Authorization')
    user_id = decode_token(token)
    if user_id:
        user = User.query.get(user_id)
        if user:
            return jsonify({'username': user.username, 'email': user.email})
    return jsonify({'message': 'User not found'}), 404


@api_bp.route('/add_camera', methods=['POST'])
def add_camera():
    token = request.headers.get('Authorization')
    user_id = decode_token(token)
    if user_id:
        data = request.get_json()
        new_camera = Camera(name=data['name'], location=data['location'], ip_address=data['ip_address'])
        db.session.add(new_camera)
        db.session.commit()
        return jsonify({'message': 'Camera added successfully'})
    return jsonify({'message': 'User not authenticated'}), 401


@api_bp.route('/get_cameras', methods=['GET'])
def get_cameras():
    token = request.headers.get('Authorization')
    user_id = decode_token(token)
    if user_id:
        cameras = Camera.query.all()
        camera_list = [{'name': camera.name, 'location': camera.location, 'ip_address': camera.ip_address} for camera in
                       cameras]
        return jsonify({'cameras': camera_list})
    return jsonify({'message': 'User not authenticated'}), 401


@api_bp.route('/update_camera/<int:camera_id>', methods=['PUT'])
def update_camera(camera_id):
    token = request.headers.get('Authorization')
    user_id = decode_token(token)
    if user_id:
        camera = Camera.query.get(camera_id)
        if camera:
            data = request.get_json()
            camera.name = data.get('name', camera.name)
            camera.location = data.get('location', camera.location)
            camera.ip_address = data.get('ip_address', camera.ip_address)
            db.session.commit()
            return jsonify({'message': 'Camera updated successfully'})
        return jsonify({'message': 'Camera not found'}), 404
    return jsonify({'message': 'User not authenticated'}), 401


@api_bp.route('/delete_camera/<int:camera_id>', methods=['DELETE'])
def delete_camera(camera_id):
    token = request.headers.get('Authorization')
    user_id = decode_token(token)
    if user_id:
        camera = Camera.query.get(camera_id)
        if camera:
            db.session.delete(camera)
            db.session.commit()
            return jsonify({'message': 'Camera deleted successfully'})
        return jsonify({'message': 'Camera not found'}), 404
    return jsonify({'message': 'User not authenticated'}), 401


@api_bp.route('/get_events', methods=['GET'])
def get_events():
    events = Event.query.all()
    event_list = [{'event_type': event.event_type, 'timestamp': event.timestamp, 'description': event.description} for
                  event in events]
    return jsonify({'events': event_list})


@api_bp.route('/get_event_details/<int:event_id>', methods=['GET'])
def get_event_details(event_id):
    event = Event.query.get(event_id)
    if event:
        return jsonify({'event_type': event.event_type, 'timestamp': event.timestamp, 'description': event.description})
    return jsonify({'message': 'Event not found'}), 404


@api_bp.route('/insert_event', methods=['POST'])
def insert_event():
    data = request.get_json()
    new_event = Event(event_type=data['event_type'], timestamp=datetime.utcnow(), description=data.get('description'))
    db.session.add(new_event)
    db.session.commit()
    return jsonify({'message': 'Event inserted successfully'})


@api_bp.route('/get_footage', methods=['GET'])
def get_footage():
    footages = Footage.query.all()
    footage_list = [
        {'file_path': footage.file_path, 'duration': footage.duration, 'creation_timestamp': footage.creation_timestamp}
        for footage in footages]
    return jsonify({'footage': footage_list})


@api_bp.route('/get_footage_details/<int:footage_id>', methods=['GET'])
def get_footage_details(footage_id):
    footage = Footage.query.get(footage_id)
    if footage:
        return jsonify({'file_path': footage.file_path, 'duration': footage.duration,
                        'creation_timestamp': footage.creation_timestamp})
    return jsonify({'message': 'Footage not found'}), 404


@api_bp.route('/insert_footage', methods=['POST'])
def insert_footage():
    data = request.get_json()
    new_footage = Footage(file_path=data['file_path'], duration=data['duration'], creation_timestamp=datetime.utcnow())
    db.session.add(new_footage)
    db.session.commit()
    return jsonify({'message': 'Footage inserted successfully'})


@api_bp.route('/get_notifications', methods=['GET'])
def get_notifications():
    notifications = Notification.query.all()
    notification_list = [{'user_id': notification.user_id, 'event_id': notification.event_id,
                          'notification_type': notification.notification_type,
                          'creation_timestamp': notification.creation_timestamp} for notification in notifications]
    return jsonify({'notifications': notification_list})
