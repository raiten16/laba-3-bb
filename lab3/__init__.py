
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://lab3_yc5s_user:MTWf88j3aP3rToTHoCyujLF8ENg5NGtP@dpg-cmc15i6n7f5s7394tmag-a.oregon-postgres.render.com/lab3_yc5s"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

import lab3.views
import lab3.models