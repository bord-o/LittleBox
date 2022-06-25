from .app import db
import datetime

class File(db.Model):
    '''
    Simple model to relate file names to semi-unique hashes\n
    file_index, hash, file_path, update_at
    '''
    __tablename__ = 'files'

    file_index = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    hash = db.Column(db.Text, unique=False, nullable=False)
    file_path = db.Column(db.Text, unique=False, nullable=False)
    update_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, unique=False, nullable=True)

    def __repr__(self):
        return f'<File {self.file_path}>'
