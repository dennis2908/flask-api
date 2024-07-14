from .accounts.controllers import token_required


def token_required_data(f):
    return token_required(f)
