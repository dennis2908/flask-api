import os

# App Initialization
from . import create_app  # from __init__ file

from .__init__ import *

from flask_apscheduler import APScheduler


app = create_app(os.getenv("CONFIG_MODE"))

SECRET_KEY = os.environ.get("SECRET_KEY") or "this is a secret"

print(SECRET_KEY)

app.config["SECRET_KEY"] = SECRET_KEY

# ----------------------------------------------- #


# ----------------------------------------------- #

if __name__ == "__main__":
    # To Run the Server in Terminal => flask run -h localhost -p 5000
    # To Run the Server with Automatic Restart When Changes Occurred => FLASK_DEBUG=1 flask run -h localhost -p 5000

    app.run()
