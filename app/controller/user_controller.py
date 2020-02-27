import datetime
import logging

from attrdict import AttrDict
from flask import (
    request, Blueprint, json, abort, url_for
)
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_raw_jwt)

from api_auth import *
from app.data.database import session_scope
from app.service.device_service import DeviceService
from app.service.user_service import UserService
from app.util.app_config import blacklist
from app.util.app_config import params

user_blueprint = Blueprint('users', __name__)

device_service = DeviceService()
user_service = UserService()

LOGGER = logging.getLogger(__name__)

jwt_days = params.jwt_access_token_expires.days
jwt_hours = params.jwt_access_token_expires.hours
jwt_minutes = params.jwt_access_token_expires.minutes


# Provide a method to create access tokens. The create_access_token()
# function is used to actually generate the token, and you can return
# it to the caller however you choose.
@user_blueprint.route('/login', methods=['POST'])
@user_blueprint.route('/get_token', methods=['GET'])
@auth.login_required
def login():
    username = request.authorization["username"]

    with session_scope() as session:
        user = user_service.get_user(username, session)

        # create authentication token
        # Identity can be any data that is json serializable
        exp_delta = datetime.datetime.utcnow() + datetime.timedelta(days=jwt_days, hours=jwt_hours, minutes=jwt_minutes)
        access_token = create_access_token(
            identity=user,
            expires_delta=datetime.timedelta(days=jwt_days, hours=jwt_hours, minutes=jwt_minutes)
        )

        resp = {
            "token": access_token,
            "exp": exp_delta,
            "username": user.username
        }
        return make_response(jsonify(resp), status.HTTP_200_OK)


@user_blueprint.route('/get_dev_token', methods=['GET'])
@auth.login_required
def get_dev_token():
    username = request.authorization["username"]
    with session_scope() as session:
        user = user_service.get_user(username, session)

        # create authentication token
        # Identity can be any data that is json serializable
        exp_delta = datetime.datetime.utcnow() + datetime.timedelta(days=7, hours=0, minutes=0)
        access_token = create_access_token(
            identity=user,
            expires_delta=datetime.timedelta(days=7, hours=0, minutes=0)
        )

        resp = {
            "token": access_token,
            "exp": exp_delta,
            "username": user.username
        }
        return make_response(jsonify(resp), status.HTTP_200_OK)


@user_blueprint.route('/logout', methods=['DELETE'])
@jwt_required
def logout():
    """

    Endpoint for revoking the current users access token
    :return:
    """
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)

    resp = {
        "status": "success",
        "msg": "user logged out"
    }
    return make_response(jsonify(resp), status.HTTP_200_OK)


@user_blueprint.route('/add_role', methods=['POST'])
@admin_required
def add_role():
    """

    :return:
    """

    try:
        username = request.json.get("username", get_jwt_identity())

        new_role = request.json.get("role", None)
        if not new_role:
            resp = {
                "status": "error",
                "msg": "you must provide a role"
            }
            return make_response(jsonify(resp), status.HTTP_400_BAD_REQUEST)

        with session_scope() as session:
            user = user_service.get_user(username, session)

            if user is None:
                resp = {
                    "status": "error",
                    "msg": "User '{}' doesn't exist".format(username),
                }
                return make_response(jsonify(resp), status.HTTP_400_BAD_REQUEST)

            if new_role in [role.name.value for role in user.roles]:
                resp = {
                    "status": "error",
                    "msg": "'{}' role already added for '{}'".format(new_role, username),
                }
                return make_response(jsonify(resp), status.HTTP_400_BAD_REQUEST)

            updated_user = user_service.add_role(username, new_role, session)

            resp = {
                "status": "success",
                "msg": "added '{}' role for '{}'".format(new_role, username),
                "data": {
                    "updated_roles": [role.serialize() for role in updated_user.roles]
                }
            }

            return make_response(jsonify(resp), status.HTTP_200_OK)

    except Exception as e:
        resp = {
            "status": "error",
            "msg": "{}".format(e)
        }
        return make_response(jsonify(resp), status.HTTP_500_INTERNAL_SERVER_ERROR)


@user_blueprint.route('/revoke_role', methods=['POST'])
@admin_required
def revoke_role():
    """

    :return:
    """

    try:
        username = request.json.get("username", get_jwt_identity())

        role_to_revoke = request.json.get("role", None)
        if not role_to_revoke:
            resp = {
                "status": "error",
                "msg": "you must provide a role"
            }
            return make_response(jsonify(resp), status.HTTP_400_BAD_REQUEST)

        with session_scope() as session:
            user = user_service.get_user(username, session)

            if user is None:
                resp = {
                    "status": "error",
                    "msg": "User '{}' doesn't exist".format(username),
                }
                return make_response(jsonify(resp), status.HTTP_400_BAD_REQUEST)

            if role_to_revoke not in [role.name.value for role in user.roles]:
                resp = {
                    "status": "error",
                    "msg": "'{}' role not present for '{}'".format(role_to_revoke, username),
                }
                return make_response(jsonify(resp), status.HTTP_400_BAD_REQUEST)

            updated_user = user_service.revoke_role(username, role_to_revoke, session)

            resp = {
                "status": "success",
                "msg": "revoked '{}' role from '{}'".format(role_to_revoke, username),
                "data": {
                    "updated_roles": [role.serialize() for role in updated_user.roles]
                }
            }

            return make_response(jsonify(resp), status.HTTP_200_OK)

    except Exception as e:
        resp = {
            "status": "error",
            "msg": "{}".format(e)
        }
        return make_response(jsonify(resp), status.HTTP_500_INTERNAL_SERVER_ERROR)


@user_blueprint.route('', methods=['POST'])
def register_user():
    """
    register a new user
    """

    try:

        if not request.json:
            abort(400)

        username = request.json.get('username', None)
        password = request.json.get('password', None)
        first_name = request.json.get('first_name', None)
        last_name = request.json.get('last_name', None)
        email = request.json.get('email', None)

        if username is None or password is None:
            abort(status.HTTP_400_BAD_REQUEST)

        with session_scope() as session:
            new_user, resp = user_service.add_user(username, password, first_name, last_name, email, session)

            if new_user is None:
                return make_response(jsonify(resp), status.HTTP_409_CONFLICT)

            # other roles should be added by users with admin privileges
            user_service.add_role(new_user.username, "end-user", session)
            if username == "admin":
                user_service.add_role(new_user.username, "admin", session)

            # create authentication token
            exp_delta = datetime.datetime.utcnow() + datetime.timedelta(days=jwt_days, hours=jwt_hours,
                                                                        minutes=jwt_minutes)
            access_token = create_access_token(
                identity=new_user,
                expires_delta=datetime.timedelta(days=jwt_days, hours=jwt_hours, minutes=jwt_minutes)
            )

            resp = {
                "status": "success",
                "msg": "new user created",
                "data": {
                    "user": new_user.serialize(),
                    "auth": {
                        "token": access_token,
                        "exp": exp_delta,
                    }
                }
            }

            LOGGER.debug(resp)
            return make_response(
                jsonify(resp),
                status.HTTP_201_CREATED,
                {'location': url_for('.get_user', username=new_user.username, _external=True)}
            )
    except Exception as e:
        resp = {
            "status": "error",
            "msg": "%s" % str(e)
        }
        return make_response(jsonify(resp), status.HTTP_500_INTERNAL_SERVER_ERROR)


@user_blueprint.route('', methods=['GET'])
@jwt_required
def get_user():
    """

    get a user

    return: details of the user with the given username
    """

    try:
        with session_scope() as session:
            user = user_service.get_user(get_jwt_identity(), session)

            if user is None:
                resp = {
                    "status": "error",
                    "msg": "user not found"
                }
                return make_response(jsonify(resp), status.HTTP_404_NOT_FOUND)

            resp = {
                "status": "success",
                "msg": "user found",
                "data": user.serialize()
            }
            return make_response(jsonify(resp), status.HTTP_200_OK)
    except Exception as e:
        resp = {
            "status": "error",
            "msg": "%s" % str(e)
        }
        return make_response(jsonify(resp), status.HTTP_500_INTERNAL_SERVER_ERROR)


@user_blueprint.route('', methods=['PUT', 'PATCH'])
@jwt_required
def update_user():
    """

    updates a user

    return: a message indicating the result of the update operation
    """

    try:
        with session_scope() as session:
            user = user_service.get_user(get_jwt_identity(), session)
            if user is None:
                resp = {
                    "success": "error",
                    "msg": "user not found"
                }
                return make_response(jsonify(resp), status.HTTP_404_NOT_FOUND)

            if not request.json:
                abort(400)

            req_body = AttrDict(json.loads(request.data))
            updated_user, resp = user_service.update_user(user, req_body, session)

            if updated_user is None:
                return make_response(jsonify(resp), status.HTTP_409_CONFLICT)

            resp = {
                "status": "success",
                "msg": "user updated",
                "data": {
                    "user": updated_user.serialize()
                }
            }

            LOGGER.debug(resp)
            return make_response(jsonify(resp), status.HTTP_200_OK)
    except Exception as e:
        resp = {"msg": "error: %s" % str(e)}
        return make_response(jsonify(resp), status.HTTP_500_INTERNAL_SERVER_ERROR)


@user_blueprint.route('', methods=['DELETE'])
@jwt_required
def delete_user():
    """

    delete a user

    return: a message indicating the deletion result
    """

    try:

        username = get_jwt_identity()

        with session_scope() as session:
            devices = user_service.get_devices(username, session)

            for device in devices:
                device_service.delete_device(username, device.device_id, session)

            is_deleted = user_service.delete_user(username, session)
            if not is_deleted:
                resp = {
                    "status": "error",
                    "msg": "no user with username: '%s' found to delete" % username
                }
                return make_response(jsonify(resp), status.HTTP_404_NOT_FOUND)

            resp = {
                "status": "success",
                "msg": "deleted user with username: '%s'" % username
            }
            return make_response(jsonify(resp), status.HTTP_200_OK)
    except Exception as e:
        resp = {
            "status": "error",
            "msg": "%s" % str(e)
        }
        return make_response(jsonify(resp), status.HTTP_500_INTERNAL_SERVER_ERROR)


@user_blueprint.route('all', methods=['GET'])
@admin_required
def get_all_users():
    """
    return: list of registered users
    """

    try:

        with session_scope() as session:
            users = user_service.get_all_users(session)

            if not len(users) > 0:
                resp = {
                    "success": "error",
                    "msg": "no users found"
                }
                return make_response(jsonify(resp), status.HTTP_404_NOT_FOUND)

            resp = {
                "status": "success",
                "msg": "found {} users".format(len(users)),
                "data": [user.serialize() for user in users]
            }
            return make_response(jsonify(resp), status.HTTP_200_OK)
    except Exception as e:
        resp = {
            "status": "error",
            "msg": "%s" % str(e)
        }
        return make_response(jsonify(resp), status.HTTP_500_INTERNAL_SERVER_ERROR)


@auth.verify_password
def verify_password(username, password):
    with session_scope() as session:
        if not user_service.is_user_valid(username, password, session):
            return False
        return True


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), status.HTTP_401_UNAUTHORIZED)
