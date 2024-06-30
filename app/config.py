# app/config.py
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    MAIL_SERVER = 'smtp.office365.com'  # SMTP server for Outlook/Office 365
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"
    DATABASE_URI = "sqlite:///finance.db"
