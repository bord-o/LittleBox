import os
import shutil
import base64
import time
import datetime
from flask import Flask, flash, redirect, url_for, render_template, request, send_file
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy


# global configs
UPLOAD_FOLDER = "./media"
ALLOWED_EXTS = {'png', 'jpg', 'jpeg', 'pdf', 'mp4', 'iso'}
DOCKERDB_IP = os.getenv('DOCKERDB_IP') # get os environment variable for db ip
HOST_ADDR = os.getenv('HOST_ADDR') # get os env var for domain or ip:port


# app configs
app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://docker:docker@{DOCKERDB_IP}/dockerdb'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.urandom(16).hex()
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024    #  500Mb size limit

db = SQLAlchemy(app)

from models import File

# utility functions
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTS

def file_gc(upload_folder):
    active_hashes = os.listdir(upload_folder)
    for this_hash in active_hashes:
        found_file = File.query.filter_by(hash=this_hash).first()

        if found_file and \
            found_file.update_at < datetime.datetime.utcnow()+datetime.timedelta(seconds=-120):

            print(this_hash, "Created at: ", found_file.update_at)
            shutil.rmtree(os.path.join(upload_folder, found_file.hash)) # handle filesystem update

            db.session.delete(found_file) # handle db update
            db.session.commit()
        else:
            print(this_hash, "Not Found or Too Young")



def temp_hash(filename):
    namestamp = base64.b64encode(bytes(filename[:3], 'utf-8'))
    timestamp = base64.b64encode(bytes(str(time.time())[-6:], 'utf-8'))

    return (timestamp + namestamp).decode('utf-8')


@app.route("/")
def index():
    return redirect(url_for('upload'))

@app.route("/upload", methods=[ 'GET', 'POST'])
def upload():

    if request.method=='GET':
        return render_template('upload.html', url="Upload a file and share this link")

    if request.method=='POST':

        # handle no file chosen
        if not request.files['document']:
            flash('No file chosen...')
            return redirect(request.url)

        # handle successful file upload
        file = request.files['document']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            temphash = temp_hash(filename)

            #put together upload directory with hash as parent folder
            updir = os.path.join(app.config['UPLOAD_FOLDER'], temphash)
            os.mkdir(updir)
            file.save(os.path.join(updir, filename))

            newfile = File(hash=temphash, file_path=os.path.join(updir,filename))
            db.session.add(newfile)
            db.session.commit()

            file_gc(app.config['UPLOAD_FOLDER']) # run old file garbage coll at every upload

            return render_template('upload.html', url=f"{HOST_ADDR}/download/{temphash}")

        return render_template('upload.html', url="File extension not accepted")
    return render_template('upload.html', url="No file chosen")

@app.route("/download/<filehash>")
def download(filehash):

    file_gc(app.config['UPLOAD_FOLDER']) # run old file garbage coll at every download
    found_file = File.query.filter_by(hash=filehash).first()
    if found_file:
        return send_file(f"{found_file.file_path}", as_attachment=True)
    return redirect(url_for('upload'))

