from flask import Flask
from flask_bcrypt import Bcrypt
from controller.config import hostConfig, dbConfig, passwordConfig, userConfig, secretKeyConfig

import pymysql.cursors

app = Flask('SP Secure')
app.secret_key = secretKeyConfig

connection = pymysql.connect(host= hostConfig,
                             user= userConfig,
                             password= passwordConfig,
                             db=dbConfig,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

bcrypt = Bcrypt(app)

from controller.common import common
from controller.admin import admin
from controller.nonAdmin import nonAdmin

app.register_blueprint(common)
app.register_blueprint(admin)
app.register_blueprint(nonAdmin)