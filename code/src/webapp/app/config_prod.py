import logging

from app.config_common import *


# DEBUG has to be to False in a production environment for security reasons
DEBUG = False

# Secret key for generating tokens
SECRET_KEY = 'houdini'

# Admin credentials
ADMIN_CREDENTIALS = ('admin', 'pa$$word')

DBUSER = 'marwa'
DBHOST = 'dbinstance.c6phnxzyppjs.us-west-2.rds.amazonaws.com'
DBPASS = 'muimuidb'
DBPORT = '5432'
DBNAME = 'muimui'

# Database choice
SQLALCHEMY_DATABASE_URI = f'postgresql://{DBUSER}:{DBPASS}@{DBHOST}:{DBPORT}/{DBNAME}'
SQLALCHEMY_TRACK_MODIFICATIONS = True

# Configuration of a Gmail account for sending mails
MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'flask.boilerplate'
MAIL_PASSWORD = 'flaskboilerplate123'
ADMINS = ['flask.boilerplate@gmail.com']

# Number of times a password is hashed
BCRYPT_LOG_ROUNDS = 12

LOG_LEVEL = logging.INFO
LOG_FILENAME = 'activity.log'
LOG_MAXBYTES = 1024
LOG_BACKUPS = 2
