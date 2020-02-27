from functools import wraps

from flask import jsonify, make_response
from flask_api import status
from flask_httpauth import HTTPBasicAuth
from flask_jwt_extended import (
    get_jwt_claims, verify_jwt_in_request
)

auth = HTTPBasicAuth()


# Here is a custom decorator that verifies the JWT is present in
# the request, as well as insuring that this user has a role of
# `admin` in the access token
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):

        verify_jwt_in_request()

        # user = get_current_user()
        # if 'admin' not in [role.name.value for role in user.roles]:
        claims = get_jwt_claims()
        if 'admin' not in claims['roles']:
            return make_response(
                jsonify(message='Admins only!'),
                status.HTTP_403_FORBIDDEN
            )
        else:
            return fn(*args, **kwargs)

    return wrapper
