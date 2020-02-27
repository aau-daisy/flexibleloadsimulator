import logging
import os
import signal
import sys

# os.chdir(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask import jsonify, make_response
from flask_api import status
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from werkzeug.exceptions import HTTPException

from app.data.database import session_scope

from app.simulator import create_fmu

from app.controller.device_controller import device_blueprint
from app.controller.user_controller import user_blueprint

from app.service.user_service import UserService
from app.service.device_service import DeviceService

from app.util import parser
from app.util.thread_exception import ThreadExit
from app.util.app_config import blacklist
from app.util.app_config import params


app = Flask(__name__, static_url_path='')

app.register_blueprint(user_blueprint, url_prefix='/api/v1.0/users')
app.register_blueprint(device_blueprint, url_prefix='/api/v1.0/devices')
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", params.jwt_secret_key)
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
jwt = JWTManager(app)

CORS(app)

# parse command line arguments
args = parser.parse_args(sys.argv[1:])
app_profile = args.profile if args.profile else params.profile
log_level = args.log_level if args.log_level else params(app_profile).log_level
host = args.host if args.host else params(app_profile).host
port = args.port if args.port else params(app_profile).port
debug = args.debug if args.debug else params(app_profile).debug
params(app_profile).db_url = args.db_url if args.db_url else params(app_profile).db_url
create_fmus = args.create_fmus if args.create_fmus else params(app_profile).create_fmus

logging.basicConfig(level=log_level)
LOGGER = logging.getLogger(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


# For this example, we are just checking if the tokens jti
# (unique identifier) is in the blacklist set. This could
# be made more complex, for example storing all tokens
# into the blacklist with a revoked status when created,
# and returning the revoked status in this call. This
# would allow you to have a list of all created tokens,
# and to consider tokens that aren't in the blacklist
# (aka tokens you didn't create) as revoked. These are
# just two options, and this can be tailored to whatever
# your application needs.
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist


# Create a function that will be called whenever create_access_token
# is used. It will take whatever object is passed into the
# create_access_token method, and lets us define what custom claims
# should be added to the access token.
@jwt.user_claims_loader
def add_claims_to_access_token(user):
    return {'roles': [role.name.value for role in user.roles]}


# Create a function that will be called whenever create_access_token
# is used. It will take whatever object is passed into the
# create_access_token method, and lets us define what the identity
# of the access token should be.
@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.username


# This function is called whenever a protected endpoint is accessed,
# and must return an object based on the tokens identity.
# This is called after the token is verified, so you can use
# get_jwt_claims() in here if desired. Note that this needs to
# return None if the user could not be loaded for any reason,
# such as not being found in the underlying data store
@jwt.user_loader_callback_loader
def user_loader_callback(username):
    with session_scope() as session:
        user = UserService.get_user(username, session)
        return user


# You can override the error returned to the user if the
# user_loader_callback returns None. If you don't override
# this, # it will return a 401 status code with the JSON:
# {"msg": "Error loading the user <identity>"}.
# You can use # get_jwt_claims() here too if desired
@jwt.user_loader_error_loader
def custom_user_loader_error(identity):
    resp = {
        "status": "error",
        "msg": "User {} not found".format(identity)
    }
    return make_response(jsonify(resp), status.HTTP_404_NOT_FOUND)


@app.route('/showargs')
def showargs():
    LOGGER.error("showarg")
    return "app_profile=%s, log_level=%s, host=%s, port=%s, debug=%s, db_url=%s, create_fmus=%s" % (
        app_profile, log_level, host, port, debug, params(app_profile).db_url, create_fmus)


@app.route('/')
@app.route('/apidocs')
def root():
    return app.send_static_file('index.html')


@app.route('/api/v1.0', methods=['GET'])
def list_routes():
    result = []
    for rt in app.url_map.iter_rules():
        result.append({
            'methods': list(rt.methods),
            'route': str(rt)
        })

    resp = {
        "status": "success",
        "msg": "found {} implemented routes".format(len(result)),
        "data": result
    }
    return make_response(jsonify(resp), status.HTTP_200_OK)


@app.errorhandler(status.HTTP_404_NOT_FOUND)
def url_not_found(error):
    resp = {
        "status": "error",
        "msg": "%s" % error
    }

    LOGGER.error(resp)
    return make_response(jsonify(resp), status.HTTP_404_NOT_FOUND)


@app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    resp = {
        "status": "error",
        "msg": "%s" % error
    }
    LOGGER.error(resp)
    return make_response(jsonify(resp), status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.errorhandler(Exception)
def unhandled_exception(e):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    if isinstance(e, HTTPException):
        status_code = e.code

    resp = {
        "status": "error",
        "msg": "{}".format(e)
    }
    LOGGER.error(e)

    return make_response(jsonify(resp), status_code)


def clean_exit(*args1):
    """
    perform proper cleanup e.g.,
    stop all active devices, delete created instances, etc.
    """

    signals = {
        signal.SIGHUP: "SIGHUP: Controlling Terminal Closed!",
        signal.SIGINT: "SIGINT: Keyboard_interrupt!",
        signal.SIGTERM: "SIGTERM: Process Killed or System Shutdown!",
    }

    LOGGER.error('Caught {}'.format(signals[args1[0]]))
    # DeviceService.stop_all_simulations()
    DeviceService.stop_threads()

    LOGGER.info('Exiting main program')

    signal.alarm(1)  # to avoid having to press CTRL+C twice in order to exit
    # raise ThreadExit


# create simulation output directory if not exists
# output_dir = os.getcwd() + "/" + params.model.output_dir
output_dir = params.model.output_dir
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
# fmu_dir = os.getcwd() + "/" + params.model.fmu_dir
fmu_dir = params.model.fmu_dir
if not os.path.exists(fmu_dir):
    os.makedirs(fmu_dir)

if create_fmus:
    LOGGER.info("Creating FMUs")
    create_fmu.create_fmu(params)

# register signal handlers
signal.signal(signal.SIGINT, clean_exit)  # keyboard interrupt
signal.signal(signal.SIGHUP, clean_exit)  # controlling terminal closed
signal.signal(signal.SIGTERM, clean_exit)  # process killed or system shutdown

# LOGGER.info('restoring simulations that were interrupted due to system crash/restart')
# DeviceService().restore_device_simulations()

LOGGER.info('Starting threads')
DeviceService.start_threads()

if __name__ == '__main__':
    try:
        LOGGER.info('Starting Flask Server')
        # add 'use_reloader=False' to disable the second server instance in debug mode
        app.run(host=host, port=port, debug=debug, use_reloader=False)
        # app.run(threaded=True)
    except ThreadExit:
        LOGGER.info("Exiting...")

