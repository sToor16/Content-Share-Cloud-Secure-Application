from flask import Flask
from flask_bcrypt import Bcrypt
from controller.config import secretKeyConfig

import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'secure-assignment-acd7ad2495a8.json'

app = Flask('SP Secure')
app.secret_key = secretKeyConfig

bcrypt = Bcrypt(app)

from controller.common import common
from controller.admin import admin
from controller.nonAdmin import nonAdmin

app.register_blueprint(common)
app.register_blueprint(admin)
app.register_blueprint(nonAdmin)