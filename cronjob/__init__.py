from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


import uuid

import time


from ..config import config

from flask_apscheduler import APScheduler

app = Flask(__name__)
scheduler = APScheduler()

# ----------------------------------------------- #

db = SQLAlchemy()
migrate = Migrate()


@scheduler.task("interval", id="my_job", seconds=10)
def my_job():

    print("This job is executed every 10 seconds.")


def create_app(config_mode):

    app = Flask(__name__)
    app.config.from_object(config[config_mode])

    db.init_app(app)
    migrate.init_app(app, db)
    app.app_context().push()
    scheduler.init_app(app)

    scheduler.start()
    return app


def create_account_controller_rw(data):
    # request_form = request.form.to_dict()

    # print(data["email"])

    id = str(uuid.uuid4())

    # db.session.execute("select * from   ")

    result = db.session.execute(
        db.text("select * from account where email = '" + data["email"] + "'")
    )

    names = [row[0] for row in result]

    if len(names) == 0:

        insert_stmt = db.insert(Account).values(
            id=id,
            email=data["email"],
            username=data["username"],
            dob=data["dob"],
            country=data["country"],
            phone_number=data["phone_number"],
        )

        db.session.execute(insert_stmt)
        db.session.commit()
        print("Successfully insert data")
        pusher.trigger("accounts", "accounts-post-added", data)
        maildata(data)
        print("Successfully send email")
    else:
        print("Email exists")


def maildata(data):
    # request_form = request.form.to_dict()

    msg = Message(
        subject="Hello," + data["username"],
        sender="manullang_d@yahoo.com",
        recipients=[data["email"]],
    )
    msg.body = "Hey " + data["username"] + ", sending you this email from app. Welcome!"
    mail.send(msg)


# ----------------------------------------------- #

# Migrate Commands:
# flask db init
# flask db migrate
# flask db upgrade
# ERROR [flask_migrate] Error: Can't locate revision identified by 'ID' => flask db revision --rev-id ID
