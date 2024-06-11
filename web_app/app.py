from flask import Flask

from routes import routes

app = Flask(__name__)
app.config['SECRET_KEY'] = '2946230ef8345ecb6ea4a41ed4d8f0bb162a89e6dcf6c77a10c48c768ce85496'
app.register_blueprint(routes)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
