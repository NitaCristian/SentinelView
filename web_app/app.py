from flask import Flask, send_from_directory
import os
import logging
from routes import routes

UPLOAD_FOLDER = '../uploads/profile_pictures'
ANALYSES_FOLDER = 'analyses/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True
app.logger.disabled = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ANALYSES_FOLDER'] = ANALYSES_FOLDER
app.config['SECRET_KEY'] = '2946230ef8345ecb6ea4a41ed4d8f0bb162a89e6dcf6c77a10c48c768ce85496'


@app.route('/uploads/profile_pictures/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@routes.route('/analyses/<filename>')
def get_analysis_file(filename):
    full_path = os.path.join(os.getcwd(), app.config['ANALYSES_FOLDER'])
    return send_from_directory(full_path, filename)


app.register_blueprint(routes)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
