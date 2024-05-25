from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
import redislite

app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize redislite
redis_db = redislite.Redis(app.config['REDISLITE_DB_PATH'])

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
mail = Mail(app)
csrf = CSRFProtect(app)

from app import routes
