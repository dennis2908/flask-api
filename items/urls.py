from flask import request

from ..app import app

from .controllers import (
    list_all_items_controller,
    create_item_controller,
    retrieve_item_controller,
    update_item_controller,
    delete_item_controller,
)
from ..auth_middleware import token_required_data


@app.route("/items", methods=["GET", "POST"])
@token_required_data
def list_create_items():
    if request.method == "GET":
        return list_all_items_controller()
    if request.method == "POST":
        return create_item_controller()
    else:
        return "Method is Not Allowed"


@app.route("/items/<item_id>", methods=["GET", "PUT", "DELETE"])
@token_required_data
def retrieve_update_destroy_item(item_id):
    if request.method == "GET":
        return retrieve_item_controller(item_id)
    if request.method == "PUT":
        return update_item_controller(item_id)
    if request.method == "DELETE":
        return delete_item_controller(item_id)
    else:
        return "Method is Not Allowed"
