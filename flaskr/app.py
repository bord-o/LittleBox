import os
import base64
import time
from flask import Flask, flash, redirect, url_for, render_template, request, send_file
from werkzeug.utils import secure_filename

from flask_sqlalchemy import SQLAlchemy


# global configs
UPLOAD_FOLDER = "./media"
ALLOWED_EXTS = {'png', 'jpg', 'jpeg', 'pdf', 'mp4', 'iso'}
DOCKERDB_ADDR = '172.17.0.2'
HOST_ADDR = '192.168.1.22:5000'


# app configs
app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://docker:docker@{DOCKERDB_ADDR}/dockerdb'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.urandom(16).hex()
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024    #  500Mb size limit

db = SQLAlchemy(app)

from .models import File
print(File.query.all())

# utility functions
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTS

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
            print('hmmm')
            
            #put together upload directory with hash as parent folder
            updir = os.path.join(app.config['UPLOAD_FOLDER'], temphash)
            print(updir)
            os.mkdir(updir)
            file.save(os.path.join(updir, filename))
            
            newfile = File(hash=temphash, file_path=os.path.join(updir,filename))
            db.session.add(newfile)
            db.session.commit()

            return render_template('upload.html', url=f"{HOST_ADDR}/download/{temphash}")

        return render_template('upload.html', url="File extension not accepted")
    return render_template('upload.html', url="No file chosen")

@app.route("/download/<filehash>")
def download(filehash):
    found_file = File.query.filter_by(hash=filehash).first()
    if found_file:
        print(found_file.file_path)
        print("found it !!!")
        return send_file(f"{found_file.file_path}", as_attachment=True)
    return redirect(url_for('upload'))