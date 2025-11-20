import os
from dotenv import load_dotenv
from pathlib import Path

from flask import Flask, render_template, redirect, url_for, request, send_from_directory

from karapp.wifi import connection_bp, get_current_wifi
from karapp.bluetooth import  bluetooth_bp, get_connected_bluetooth_devices
from karapp.models import db, FileModel
from karapp.tools.music import get_metadata
from karapp.tools.photo import make_artwork_base64
from karapp.tools import rss

load_dotenv()

DATA_PATH = os.getenv('DATA_PATH')
DB_PATH = os.path.join(os.getenv('DB_PATH'), 'karapp.db')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+DB_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.register_blueprint(connection_bp)
app.register_blueprint(bluetooth_bp)

db.init_app(app)

# if not os.path.exists(DB_PATH):
with app.app_context():
    # db.drop_all()
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/parameters')
def parametres():
    current_wifi = get_current_wifi()
    connected_bluetooth = get_connected_bluetooth_devices()
    return render_template('parameters.html', current_wifi=current_wifi, connected_bluetooth=connected_bluetooth)

@app.route('/sync_db', endpoint='db_sync')
def synd_db():
    cat = os.listdir(DATA_PATH)
    for each in cat:
        p = Path(DATA_PATH)/each
        # ajouter les nouveaux fichiers
        for f in p.rglob('*'):
            model = FileModel.query.filter_by(path=str(f)).all()
            if len(model)==0:
                artwork = None
                name = None
                artist = None
                album = None
                if f.is_file():
                    ftype = 'file'
                    if each == 'musique':
                        meta = get_metadata(str(f))
                        artwork = meta['artwork']
                        artist = meta['artist']
                        name = meta['title']
                        album = meta['album']
                    elif each == 'photo':
                        name = f.name.split('.')[0]
                        artwork = make_artwork_base64(str(f))
                else:
                    ftype = 'dir'
                    name = f.name

                fmodel = FileModel(
                    type=ftype,
                    category = each,
                    path = str(f),
                    name = name,
                    artwork = artwork,
                    artist = artist,
                    album=album

                )
                parent = FileModel.query.filter_by(path=str(f.parent)).first()
                if parent is not None:
                    fmodel.parent = parent.id
                db.session.add(fmodel)

        # retirer ceux qui n'existent plus
        all_files = FileModel.query.all()
        for f in all_files:
            if not os.path.exists(f.path):
                FileModel.query.filter(FileModel.id == f.id).delete()
        db.session.commit()
    return redirect(url_for('parametres'))

@app.route('/categorie/<nom>')
def categorie(nom):
    print(nom)
    parent_id = request.args.get('parent_id')
    models = FileModel.query.filter_by(category=nom, parent=parent_id).all()
    return render_template('files.html', cat=nom, items=models)

@app.route("/categorie/<path:filename>")
def serve_file(filename):
    ftype = request.args.get('type')
    if not filename.startswith('/'):
        filename = '/' + filename
    directory = os.path.dirname(filename)
    file_name = os.path.basename(filename)
    if ftype == 'music':
        return send_from_directory(directory, file_name, mimetype='audio/mpeg')
    else:
        return send_from_directory(directory, file_name, mimetype='image/jpeg')

@app.route('/add_podcast', methods=['GET', 'POST'])
def add_podcast():
    if request.method == 'POST':
        return render_template('files.html', cat='podcast', items=[])
    else:
        tool_list = rss.list_tools()
        return render_template('add_rss.html', searchtools=tool_list)


@app.template_filter('basename')
def basename_filter(path):
    p = Path(path).name
    return p.split('.')[0]


if __name__ == '__main__':
    app.run(debug=True)