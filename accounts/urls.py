from flask import request

from ..app import app
from .controllers import (
    list_all_accounts_controller,
    create_account_controller,
    retrieve_account_controller,
    update_account_controller,
    delete_account_controller,
    export_all_accounts_excel_controller,
    read_report_controller,
    login,
)

from ..auth_middleware import token_required_data


@app.route("/accounts/export_excel", methods=["GET"])
def export_all_accounts_excel():
    return export_all_accounts_excel_controller()


@app.route("/accounts/read_excel", methods=["GET"])
@token_required_data
def read_report_excel():
    return read_report_controller()


@app.route("/accounts/login", methods=["POST"])
def login_ctrl():
    return login()


@app.route("/accounts", methods=["GET", "POST"])
def list_create_accounts():
    if request.method == "GET":
        return list_all_accounts_controller()
    if request.method == "POST":
        return create_account_controller()
    else:
        return "Method is Not Allowed"


@app.route("/accounts/<account_id>", methods=["GET", "PUT", "DELETE"])
@token_required_data
def retrieve_update_destroy_account(account_id):
    if request.method == "GET":
        return retrieve_account_controller(account_id)
    if request.method == "PUT":
        return update_account_controller(account_id)
    if request.method == "DELETE":
        return delete_account_controller(account_id)
    else:
        return "Method is Not Allowed"
