from flask import Flask, send_from_directory
import os

from routes import routes

UPLOAD_FOLDER = '../uploads/profile_pictures'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = '2946230ef8345ecb6ea4a41ed4d8f0bb162a89e6dcf6c77a10c48c768ce85496'
app.register_blueprint(routes)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/uploads/profile_pictures/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
