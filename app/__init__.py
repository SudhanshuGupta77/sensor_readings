from flask import Flask

from .auth import login_manager
from .data import db
from .sensors.views import sensors
from .users.views import users

app = Flask(__name__)
app.config.from_object('config.BaseConfiguration')


@app.context_processor
def provide_constants():
    return {"constants": {"TUTORIAL_PART": 2}}

db.init_app(app)

login_manager.init_app(app)

app.register_blueprint(sensors)
app.register_blueprint(users)