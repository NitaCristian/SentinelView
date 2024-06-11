import json

import pytest

from app import create_app
from models import db


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_database.db'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


def test_register_user(client):
    data = {'username': 'test_user', 'email': 'test@example.com', 'password': 'pwd'}
    response = client.post('/api/register', json=data)
    assert response.status_code == 200
    assert b"User registered successfully" in response.data


def test_login_user(client):
    data = {'username': 'test_user', 'email': 'test@example.com', 'password': 'pwd'}
    client.post('/api/register', json=data)
    response = client.post('/api/login', json=data)
    assert response.status_code == 200
    assert b"token" in response.data


def test_get_user_details(client):
    user_data = {'username': 'test_user', 'email': 'test@example.com', 'password': 'pwd'}
    client.post('/api/register', json=user_data)
    login_data = {'username': 'test_user', 'password': 'pwd'}
    login_response = client.post('/api/login', json=login_data)
    token = json.loads(login_response.data)['token']

    response = client.get('/api/user', headers={'Authorization': f'{token}'})
    assert response.status_code == 200
    assert b"test_user" in response.data


def test_add_camera(client):
    # First, register a user and get the token
    user_data = {'username': 'test_user', 'email': 'test@example.com', 'password': 'pwd'}
    client.post('/api/register', json=user_data)
    login_data = {'username': 'test_user', 'password': 'pwd'}
    login_response = client.post('/api/login', json=login_data)
    token = json.loads(login_response.data)['token']

    # Add a camera
    camera_data = {'name': 'Test Camera', 'location': 'Test Location', 'ip_address': '192.168.1.1'}
    response = client.post('/api/add_camera', json=camera_data, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert b"Camera added successfully" in response.data


def test_get_cameras(client):
    # First, register a user and get the token
    user_data = {'username': 'test_user', 'email': 'test@example.com', 'password': 'pwd'}
    client.post('/api/register', json=user_data)
    login_data = {'username': 'test_user', 'password': 'pwd'}
    login_response = client.post('/api/login', json=login_data)
    token = json.loads(login_response.data)['token']

    # Add a camera
    camera_data = {'name': 'Test Camera', 'location': 'Test Location', 'ip_address': '192.168.1.1'}
    client.post('/api/add_camera', json=camera_data, headers={'Authorization': f'Bearer {token}'})

    # Get cameras
    response = client.get('/api/get_cameras', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert b"Test Camera" in response.data


def test_update_camera(client):
    # First, register a user and get the token
    user_data = {'username': 'test_user', 'email': 'test@example.com', 'password': 'pwd'}
    client.post('/api/register', json=user_data)
    login_data = {'username': 'test_user', 'password': 'pwd'}
    login_response = client.post('/api/login', json=login_data)
    token = json.loads(login_response.data)['token']

    # Add a camera
    camera_data = {'name': 'Test Camera', 'location': 'Test Location', 'ip_address': '192.168.1.1'}
    client.post('/api/add_camera', json=camera_data, headers={'Authorization': f'Bearer {token}'})

    # Update camera
    update_data = {'name': 'Updated Camera Name'}
    response = client.put('/api/update_camera/1', json=update_data, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert b"Camera updated successfully" in response.data


def test_delete_camera(client):
    # First, register a user and get the token
    user_data = {'username': 'test_user', 'email': 'test@example.com', 'password': 'pwd'}
    client.post('/api/register', json=user_data)
    login_data = {'username': 'test_user', 'password': 'pwd'}
    login_response = client.post('/api/login', json=login_data)
    token = json.loads(login_response.data)['token']

    # Add a camera
    camera_data = {'name': 'Test Camera', 'location': 'Test Location', 'ip_address': '192.168.1.1'}
    client.post('/api/add_camera', json=camera_data, headers={'Authorization': f'Bearer {token}'})

    # Delete camera
    response = client.delete('/api/delete_camera/1', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert b"Camera deleted successfully" in response.data


def test_get_events(client):
    # Get events
    response = client.get('/api/get_events')
    assert response.status_code == 200
    assert b"events" in response.data


def test_get_event_details(client):
    # First, insert an event
    event_data = {'event_type': 'Test Event', 'description': 'Test description'}
    client.post('/api/insert_event', json=event_data)

    # Get event details
    response = client.get('/api/get_event_details/1')
    assert response.status_code == 200
    assert b"Test Event" in response.data


def test_insert_event(client):
    # Insert event
    event_data = {'event_type': 'Test Event', 'description': 'Test description'}
    response = client.post('/api/insert_event', json=event_data)
    assert response.status_code == 200
    assert b"Event inserted successfully" in response.data


def test_get_footage(client):
    # Get footage
    response = client.get('/api/get_footage')
    assert response.status_code == 200
    assert b"footage" in response.data


def test_get_footage_details(client):
    # First, insert footage
    footage_data = {'file_path': '/path/to/footage.mp4', 'duration': 60}
    client.post('/api/insert_footage', json=footage_data)

    # Get footage details
    response = client.get('/api/get_footage_details/1')
    assert response.status_code == 200
    assert b"/path/to/footage.mp4" in response.data


def test_insert_footage(client):
    # Insert footage
    footage_data = {'file_path': '/path/to/footage.mp4', 'duration': 60}
    response = client.post('/api/insert_footage', json=footage_data)
    assert response.status_code == 200
    assert b"Footage inserted successfully" in response.data


def test_get_notifications(client):
    # Get notifications
    response = client.get('/api/get_notifications')
    assert response.status_code == 200
    assert b"notifications" in response.data
