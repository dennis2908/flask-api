from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import uuid

from datetime import datetime


from ..config import config
from flask_mail import Mail, Message

from ..accounts.models import Account

import pika, os

from pusher import Pusher

from pymongo import MongoClient

app = Flask(__name__)
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
app.config["MAIL_PORT"] = os.getenv("MAIL_PORT")
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS")

pusher = Pusher(
    app_id="705473",
    key="b9e4d6190581d989a6e2",
    secret="629f95f4aa4563d80845",
    cluster="ap1",
    ssl=False,
)
client = MongoClient("mongodb://localhost:27017/")
db = client["demo"]
collection = db["data"]
mail = Mail(app)


# ----------------------------------------------- #

db = SQLAlchemy()
migrate = Migrate()


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()

    channel.queue_declare(queue="update.data")

    def callback(ch, method, properties, body):
        print(f" [x] Received {body}")
        update_account_controller_rw(eval(body))

    channel.basic_consume(
        queue="update.data",
        on_message_callback=callback,
        auto_ack=True,
    )

    print(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


def create_app(config_mode):

    app = Flask(__name__)
    app.config.from_object(config[config_mode])

    db.init_app(app)
    migrate.init_app(app, db)
    app.app_context().push()
    main()
    return app


def update_account_controller_rw(data):

    db.session.execute(
        db.text(
            "UPDATE account "
            "SET username = '"
            + data["username"]
            + "', dob = '"
            + data["dob"]
            + "', country = '"
            + data["country"]
            + "', phone_number = '"
            + data["phone_number"]
            + "'"
            "WHERE id ='" + data["id"] + "'",
        )
    )
    db.session.commit()


# ----------------------------------------------- #

# Migrate Commands:
# flask db init
# flask db migrate
# flask db upgrade
# ERROR [flask_migrate] Error: Can't locate revision identified by 'ID' => flask db revision --rev-id ID
