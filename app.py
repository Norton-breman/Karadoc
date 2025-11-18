import os
from dotenv import load_dotenv

from flask import Flask, render_template, request, redirect, url_for

from wifi import connection_bp, get_current_wifi
from bluetooth import  bluetooth_bp, get_connected_bluetooth_devices

from models import db

load_dotenv()

DATA_PATH = os.getenv('DATA_PATH')
DB_PATH = os.path.join(os.getenv('DB_PATH'), 'app.db')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+DB_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.register_blueprint(connection_bp)
app.register_blueprint(bluetooth_bp)

db.init_app(app)

if not os.path.exists(DB_PATH):
    with app.app_context():
        db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/parameters')
def parametres():
    current_wifi = get_current_wifi()
    connected_bluetooth = get_connected_bluetooth_devices()
    return render_template('parameters.html', current_wifi=current_wifi, connected_bluetooth=connected_bluetooth)

# @app.route('/bt_settings')
# def bt_settings():
#     pass


if __name__ == '__main__':
    app.run(debug=True)