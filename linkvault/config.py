import os 
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'linkvault.db')
    SQLALCHEMY_TRACK_MODIFICATION = False
    SECRET_KEY = 'dev-secret-key-change-in-production'