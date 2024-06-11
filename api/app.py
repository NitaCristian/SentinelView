from flask import Flask
from models import db
from routes import api_bp


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = '2946230ef8345ecb6ea4a41ed4d8f0bb162a89e6dcf6c77a10c48c768ce85496'
    db.init_app(app)
    app.register_blueprint(api_bp, url_prefix='/api')
    return app


if __name__ == '__main__':
    main = create_app()
    with main.app_context():
        db.create_all()
    main.run(debug=True, port=5001)
