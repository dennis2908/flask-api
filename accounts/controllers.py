from flask import request, jsonify, Flask, send_file
import uuid

from .. import db
from .models import Account

import os
import pika
from flask_caching import Cache
import redis

import xlsxwriter

from openpyxl import load_workbook


# ----------------------------------------------- #

# Query Object Methods => https://docs.sqlalchemy.org/en/14/orm/query.html#sqlalchemy.orm.Query
# Session Object Methods => https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.Session
# How to serialize SqlAlchemy PostgreSQL Query to JSON => https://stackoverflow.com/a/46180522

app = Flask(__name__)

app.config["CACHE_TYPE"] = os.getenv("CACHE_TYPE")
app.config["CACHE_REDIS_HOST"] = os.getenv("CACHE_REDIS_HOST")
app.config["CACHE_REDIS_PORT"] = os.getenv("CACHE_REDIS_PORT")
app.config["CACHE_REDIS_DB"] = os.getenv("CACHE_REDIS_DB")

cache = Cache(app=app)
cache.init_app(app)

# Initialize Redis client
redis_client = redis.Redis(
    host=os.getenv("CACHE_REDIS_HOST"), port=os.getenv("CACHE_REDIS_PORT"), db=0
)


def list_all_accounts_controller():
    accounts = Account.query.all()
    response = []

    for account in accounts:
        response.append(account.toDict())
    redis_client.set(str(uuid.uuid4()), repr(response))
    return jsonify(response)


def read_report_controller():
    excelfile = "fileUpload/report.xlsx"
    wb = load_workbook(excelfile)
    ws = wb[wb.sheetnames[0]]
    data = {}
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()

    channel.queue_declare(queue="send.email.flask")
    for row in range(2, ws.max_row + 1):  # need +1 to get last row!
        for col in "A":  # A gets players for texted season
            cell_name = "{}{}".format(col, row)
            data["email"] = ws[cell_name].value
        for col in "B":  # A gets players for texted season
            cell_name = "{}{}".format(col, row)
            data["username"] = ws[cell_name].value
        for col in "C":  # A gets players for texted season
            cell_name = "{}{}".format(col, row)
            data["dob"] = ws[cell_name].value
        for col in "D":  # A gets players for texted season
            cell_name = "{}{}".format(col, row)
            data["country"] = ws[cell_name].value
        for col in "E":  # A gets players for texted season
            cell_name = "{}{}".format(col, row)
            data["phone_number"] = ws[cell_name].value
        channel.basic_publish(
            exchange="", routing_key="send.email.flask", body=repr(data)
        )
    return jsonify(data)


def createReport(data):
    fn = "report.xlsx"
    workbook = xlsxwriter.Workbook("fileUpload/" + fn)
    worksheet = workbook.add_worksheet()
    worksheet.write(0, 0, "No: ")
    worksheet.write(0, 1, "Email: ")
    worksheet.write(0, 2, "Username: ")
    worksheet.write(0, 3, "DOB: ")
    worksheet.write(0, 4, "Country: ")
    worksheet.write(0, 5, "Phone Number: ")
    row = 0
    for k in data:
        col = 0
        row += 1
        worksheet.write(row, col, row)
        col += 1
        worksheet.write(row, col, k["email"])
        col += 1
        worksheet.write_string(row, col, k["username"])
        col += 1
        worksheet.write_string(row, col, str(k["dob"]))
        col += 1
        worksheet.write_string(row, col, k["country"])
        col += 1
        worksheet.write_string(row, col, k["phone_number"])

    workbook.close()
    return fn


def export_all_accounts_excel_controller():

    accounts = Account.query.all()
    response = []
    for account in accounts:
        response.append(account.toDict())

    fn = "generated/" + createReport(response)
    return send_file(fn, mimetype="application/vnd.ms-excel")


# return jsonify(response)


def create_account_controller():
    # request_form = request.form.to_dict()

    data = request.get_json()
    # print(data["email"])

    id = str(uuid.uuid4())
    new_account = Account(
        id=id,
        email=data["email"],
        username=data["username"],
        dob=data["dob"],
        country=data["country"],
        phone_number=data["phone_number"],
    )
    db.session.add(new_account)

    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()

    channel.queue_declare(queue="send.email.flask")

    channel.basic_publish(exchange="", routing_key="send.email.flask", body=repr(data))
    print(data)

    # maildata(data)
    return jsonify("success")


def retrieve_account_controller(account_id):
    response = Account.query.get(account_id).toDict()
    return jsonify(response)


def update_account_controller(account_id):
    request_form = request.form.to_dict()
    account = Account.query.get(account_id)

    account.email = request_form["email"]
    account.username = request_form["username"]
    account.dob = request_form["dob"]
    account.country = request_form["country"]
    account.phone_number = request_form["phone_number"]
    db.session.commit()

    response = Account.query.get(account_id).toDict()
    return jsonify(response)


def delete_account_controller(account_id):
    Account.query.filter_by(id=account_id).delete()
    db.session.commit()

    return ('Account with Id "{}" deleted successfully!').format(account_id)
