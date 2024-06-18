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

    channel.queue_declare(queue="send.email.flask")

    def callback(ch, method, properties, body):
        print(f" [x] Received {body}")
        create_account_controller_rw(eval(body))

    channel.basic_consume(
        queue="send.email.flask", on_message_callback=callback, auto_ack=True
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
        dataMongo = {}
        dataMongo["type_operation"] = "insert data"
        dataMongo["table"] = "accounts"
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        dataMongo["datetime"] = dt_string
        collection.insert_one(dataMongo)
        print(collection.find_one())
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
