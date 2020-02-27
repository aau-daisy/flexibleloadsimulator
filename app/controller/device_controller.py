import logging

from attrdict import AttrDict
from flask import request, Blueprint, json, url_for
from flask_jwt_extended import (
    jwt_required, get_jwt_identity
)

from app.data.database import session_scope
from app.data.model.device_model import DeviceModel
from app.service.device_service import DeviceService
from app.service.user_service import UserService
from app.util.app_config import params

from api_auth import *

device_blueprint = Blueprint('devices', __name__)

device_service = DeviceService()
user_service = UserService()

LOGGER = logging.getLogger(__name__)


@device_blueprint.route('/types/available', methods=['GET'])
@jwt_required
def get_available_device_types():
    """
    returns a list of devices that can be simulated
    """
    try:
        resp = {
            "status": "success",
            "msg": "found {} available models".format(len(params.model.available_models)),
            "data": params.model.available_models
        }
        return make_response(jsonify(resp), status.HTTP_200_OK)
    except Exception as e:
        resp = {
            "status": "error",
            "msg": "%s" % str(e)
        }
        return make_response(jsonify(resp), status.HTTP_500_INTERNAL_SERVER_ERROR)


@device_blueprint.route('/types/examples', methods=['GET'])
@jwt_required
def get_example_device_types():
    """
    returns an example list of devices whose parameters are already set
    """
    try:
        resp = {
            "status": "success",
            "msg": "found {} example devices".format(len(params.model.example_devices)),
            "data": params.model.example_devices
        }
        return make_response(jsonify(resp), status.HTTP_200_OK)
    except Exception as e:
        resp = {
            "status": "error",
            "msg": "%s" % str(e)
        }
        return make_response(jsonify(resp), status.HTTP_500_INTERNAL_SERVER_ERROR)


@device_blueprint.route('', methods=['POST'])
@jwt_required
def create_device():
    """
    start simulating a new device for the given user
    """

    try:
        username = get_jwt_identity()

        # retrieve model parameters from request body and validate them
        req_params = AttrDict(json.loads(request.data))
        is_valid, resp = device_service.validate_device_params(req_params)
        if not is_valid:
            return make_response(jsonify(resp), status.HTTP_400_BAD_REQUEST)

        with session_scope() as session:
            user = user_service.get_user(username, session)
            if user.devices.count() == user.max_devices:
                resp = {
                    "status": "error",
                    "msg": "max active device limit reached for '{}'".format(username)
                }
                return make_response(jsonify(resp), status.HTTP_400_BAD_REQUEST)

            # create the device
            device = device_service.create_device(username, req_params.device_name, session)

            # add model to device
            model = DeviceModel(req_params.model_name, req_params.params)
            device_service.add_device_model(device, model, session)

            # start a simulating a new device
            device_service.start_simulation(device, session)
            # also turn it on
            device_service.turn_on_device(device, session)

            resp = {
                "status": "success",
                "msg": "created new device",
                "data": device.serialize()
            }
            return make_response(
                jsonify(resp),
                status.HTTP_201_CREATED,
                {'location': url_for(".get_device", device_id=device.device_id, _external=True)}
            )
    except Exception as e:
        resp = {
            "status": "error",
            "msg": "%s" % str(e)
        }
        return make_response(jsonify(resp), status.HTTP_500_INTERNAL_SERVER_ERROR)


@device_blueprint.route('', methods=['GET', 'POST'])
@jwt_required
def get_device():
    """

    :return a single device for the current user if 'device_id' provided in request body
            else return all devices for user
    """

    try:
        username = get_jwt_identity()

        with session_scope() as session:
            # return only requested device if 'device_id' was sent in req body
            if request.data and "device_id" in AttrDict(json.loads(request.data)):
                device_id = AttrDict(json.loads(request.data)).get("device_id")
                device = device_service.get_device(username, device_id, session)
                if device is None:
                    resp = {
                        "status": "error",
                        "msg": "no device with id '%s' exists for '%s'" % (device_id, username)
                    }
                    return make_response(jsonify(resp), status.HTTP_404_NOT_FOUND)

                resp = {
                    "status": "success",
                    "msg": "device found",
                    "data": device.serialize()
                }
                return make_response(jsonify(resp), status.HTTP_200_OK)
            else:  # return all devices for the user
                current_user_devices = device_service.get_all_devices(username, session)
                if len(current_user_devices) == 0:
                    resp = {
                        "status": "error",
                        "msg": "no devices exists for '%s'" % username
                    }
                    return make_response(jsonify(resp), status.HTTP_404_NOT_FOUND)

                resp = {
                    "status": "success",
                    "msg": "{} devices found for {}".format(len(current_user_devices), username),
                    "data": [device.serialize() for device in current_user_devices]
                }
                return make_response(jsonify(resp), status.HTTP_200_OK)
    except Exception as e:
        resp = {
            "status": "error",
            "msg": "%s" % str(e)
        }
        return make_response(jsonify(resp), status.HTTP_500_INTERNAL_SERVER_ERROR)


@device_blueprint.route('', methods=['PUT', 'PATCH'])
@jwt_required
def update_device():
    """

    updates a given device
    :return details of the updated device
    """

    try:
        username = get_jwt_identity()

        req_params = AttrDict(json.loads(request.data))
        device_id = req_params.get("device_id")
        if device_id is None:
            resp = {
                "status": "error",
                "msg": "request body must contain 'device_id'"
            }
            return make_response(jsonify(resp), status.HTTP_400_BAD_REQUEST)

        with session_scope() as session:
            device = device_service.get_device(username, device_id, session)
            if device is None:
                resp = {
                    "status": "error",
                    "msg": "no device with id '%s' exists for '%s'" % (device_id, username)
                }
                return make_response(jsonify(resp), status.HTTP_404_NOT_FOUND)

            # retrieve model parameters from request body and validate them
            is_valid, resp = device_service.validate_device_params(req_params)
            if not is_valid:
                return make_response(jsonify(resp), status.HTTP_400_BAD_REQUEST)

            # stop simulation if running
            DeviceService.stop_simulation(device)

            # update device_name
            updated_device = device_service.update_device(username, device_id, req_params.device_name, session)

            # add model to device
            new_model = DeviceModel(req_params.model_name, req_params.params)
            updated_device = device_service.update_device_model(updated_device, new_model, session)

            # restart simulating the updated device
            device_service.start_simulation(device, session)

            resp = {
                "status": "success",
                "msg": "updated device",
                "data": updated_device.serialize()
            }
            return make_response(
                jsonify(resp),
                status.HTTP_200_OK,
                {'location': url_for(".get_device", device_id=device.device_id)}
            )
    except Exception as e:
        resp = {
            "status": "error",
            "msg": "%s" % str(e)
        }
        return make_response(jsonify(resp), status.HTTP_500_INTERNAL_SERVER_ERROR)


@device_blueprint.route('', methods=['DELETE'])
@jwt_required
def delete_device():
    """
    delete active devices by:
     i)- first terminating their respective threads by setting the shutdown flag on thread to trigger a clean shutdown
     ii)- after stopping simulation, the device is deleted from db

    """
    try:
        username = get_jwt_identity()

        req_params = AttrDict(json.loads(request.data))
        device_id = req_params.get("device_id")
        if device_id is None:
            resp = {
                "status": "error",
                "msg": "request body must contain 'device_id'"
            }
            return make_response(jsonify(resp), status.HTTP_400_BAD_REQUEST)

        with session_scope() as session:
            device = device_service.get_device(username, device_id, session)
            if device is None:
                resp = {
                    "status": "error",
                    "msg": "no such device exists for '%s'" % username
                }
                return make_response(jsonify(resp), status.HTTP_404_NOT_FOUND)

            is_deleted = device_service.delete_device(username, device_id, session)

            if is_deleted:
                resp = {
                    "status": "success",
                    "msg": "deleted device with device_id '%s'" % device_id
                }
                return make_response(jsonify(resp), status.HTTP_200_OK)
            else:
                resp = {
                    "status": "error",
                    "msg": "failed ot delete device with device_id '%s'" % device_id
                }
                return make_response(jsonify(resp), status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        resp = {
            "status": "error",
            "msg": "%s" % str(e)
        }
        return make_response(jsonify(resp), status.HTTP_500_INTERNAL_SERVER_ERROR)


@device_blueprint.route('/all', methods=['GET'])
@admin_required
def get_all_devices_for_all_users():
    """
    :return: a list of all devices
    """
    try:
        with session_scope() as session:
            devices = device_service.get_all_devices_for_all_users(session)
            if len(devices) == 0:
                resp = {
                    "status": "error",
                    "msg": "no devices found in db"
                }
                return make_response(jsonify(resp), status.HTTP_404_NOT_FOUND)

            resp = {
                "status": "success",
                "msg": "found {} devices in db".format(len(devices)),
                "data": [device.serialize() for device in devices]
            }
            return make_response(jsonify(resp), status.HTTP_200_OK)
    except Exception as e:
        resp = {
            "status": "error",
            "msg": "%s" % str(e)
        }
        return make_response(jsonify(resp), status.HTTP_500_INTERNAL_SERVER_ERROR)


@device_blueprint.route('/deleteAll', methods=['DELETE'])
@jwt_required
def delete_all_devices_for_user():
    """
    delete all active devices for the given user
    """

    try:
        username = get_jwt_identity()

        with session_scope() as session:
            user = user_service.get_user(username, session)
            device_count = user.devices.count()
            if device_count == 0:
                resp = {
                    "status": "error",
                    "msg": "no devices found for '%s'" % username
                }
                return make_response(jsonify(resp), status.HTTP_404_NOT_FOUND)

            LOGGER.info("Deleting all devices for '%s'" % username)
            for device in user.devices:
                device_service.delete_device(user.username, device.device_id, session)
                LOGGER.info("Deleted " + device.device_name + ", with device id = " + device.device_id + "!")
            LOGGER.info("Deleted all devices for '%s'" % username)

            resp = {
                "status": "success",
                "msg": "deleted %d devices for '%s'" % (device_count, username)
            }
            return make_response(jsonify(resp), status.HTTP_200_OK)
    except Exception as e:
        resp = {
            "status": "error",
            "msg": "%s" % str(e)
        }
        return make_response(jsonify(resp), status.HTTP_500_INTERNAL_SERVER_ERROR)


@device_blueprint.route('/active', methods=['GET'])
@jwt_required
def get_active_devices_for_user():
    """
    show active devices for the given user
    """
    try:
        username = get_jwt_identity()
        with session_scope() as session:
            user = user_service.get_user(username, session)

            if user.devices.count() == 0:
                resp = {
                    "status": "error",
                    "msg": "no devices found for '%s' " % username
                }
                return make_response(jsonify(resp), status.HTTP_404_NOT_FOUND)

            active_devices = []
            for device in user.devices:
                if device_service.is_device_active(device) and device_service.is_device_simulating(device):
                    active_devices.append(device.serialize())
            resp = {
                "status": "success",
                "msg": "found {} active devices for '{}'".format(len(active_devices), username),
                "data": active_devices
            }
            return make_response(jsonify(resp), status.HTTP_200_OK)
    except Exception as e:
        resp = {
            "status": "error",
            "msg": "%s" % str(e)
        }
        return make_response(jsonify(resp), status.HTTP_500_INTERNAL_SERVER_ERROR)


@device_blueprint.route('/state', methods=['GET', 'POST'])
@device_blueprint.route('/status', methods=['GET', 'POST'])
@jwt_required
def get_device_state():
    """
    get the on/off or active/inactive status for the given device
    """
    try:
        username = get_jwt_identity()
        req_params = AttrDict(json.loads(request.data))
        device_id = req_params.get("device_id")
        if device_id is None:
            resp = {
                "status": "error",
                "msg": "request body must contain 'device_id'"
            }
            return make_response(jsonify(resp), status.HTTP_400_BAD_REQUEST)

        with session_scope() as session:
            device = device_service.get_device(username, device_id, session)
            if device is None:
                resp = {
                    "status": "error",
                    "msg": "no device with device_id '%s' found for '%s'" % (device_id, username)
                }
                return make_response(jsonify(resp), status.HTTP_404_NOT_FOUND)

            if not device_service.is_device_simulating(device):
                resp = {
                    "status": "error",
                    "msg": "device with device_id '%s' not simulating. you need to start simulating it first" % device_id
                }
                return make_response(jsonify(resp), status.HTTP_400_BAD_REQUEST)

            resp = {
                "status": "success",
                "msg": "device power state fetched",
                "data": {
                    "power_state": device.device_state.value
                }
            }
            return make_response(jsonify(resp), status.HTTP_200_OK)
    except Exception as e:
        resp = {
            "status": "error",
            "msg": "%s" % str(e)
        }
        return make_response(jsonify(resp), status.HTTP_500_INTERNAL_SERVER_ERROR)


@device_blueprint.route('/start', methods=['GET', 'POST'])
@jwt_required
def turn_on_device():
    """
    turn on the given device
    """
    try:
        username = get_jwt_identity()

        req_params = AttrDict(json.loads(request.data))
        device_id = req_params.get("device_id")
        if device_id is None:
            resp = {
                "status": "error",
                "msg": "request body must contain 'device_id'"
            }
            return make_response(jsonify(resp), status.HTTP_400_BAD_REQUEST)

        LOGGER.info("start signal received for device_id:" + device_id)

        with session_scope() as session:
            device = device_service.get_device(username, device_id, session)
            if device is None:
                resp = {
                    "status": "error",
                    "msg": "no device with device_id '%s' found for '%s'" % (device_id, username)
                }
                return make_response(jsonify(resp), status.HTTP_404_NOT_FOUND)

            if not device_service.is_device_active(device):
                resp = {
                    "status": "error",
                    "msg": "device with device_id '%s' not active. you need to activate it first" % device_id
                }
                return make_response(jsonify(resp), status.HTTP_400_BAD_REQUEST)

            if not device_service.is_device_simulating(device):
                resp = {
                    "status": "error",
                    "msg": "device with device_id '%s' not simulating. you need to start simulating it first" % device_id
                }
                return make_response(jsonify(resp), status.HTTP_400_BAD_REQUEST)

            if device_service.is_device_turned_on(device):
                resp = {
                    "status": "success",
                    "msg": "device with device_id '%s' already turned on" % device_id
                }
                return make_response(jsonify(resp), status.HTTP_200_OK)

            device_service.turn_on_device(device, session)
            resp = {
                "status": "success",
                "msg": "turned on device with device_id '%s'" % device_id
            }
            return make_response(jsonify(resp), status.HTTP_200_OK)
    except Exception as e:
        resp = {
            "status": "error",
            "msg": "%s" % str(e)
        }
        return make_response(jsonify(resp), status.HTTP_500_INTERNAL_SERVER_ERROR)


@device_blueprint.route('/stop', methods=['GET', 'POST'])
@jwt_required
def turn_off_device():
    """
    turn off the given device
    """
    try:
        username = get_jwt_identity()

        req_params = AttrDict(json.loads(request.data))
        device_id = req_params.get("device_id")
        if device_id is None:
            resp = {
                "status": "error",
                "msg": "request body must contain 'device_id'"
            }
            return make_response(jsonify(resp), status.HTTP_400_BAD_REQUEST)

        LOGGER.info("stop signal received for device_id:" + device_id)

        with session_scope() as session:
            device = device_service.get_device(username, device_id, session)
            if device is None:
                resp = {
                    "status": "error",
                    "msg": "no device with device_id '%s' found for '%s'" % (device_id, username)
                }
                return make_response(jsonify(resp), status.HTTP_404_NOT_FOUND)

            if not device_service.is_device_active(device):
                resp = {
                    "status": "error",
                    "msg": "device with device_id '%s' not active. you need to activate it first" % device_id
                }
                return make_response(jsonify(resp), status.HTTP_400_BAD_REQUEST)

            if not device_service.is_device_simulating(device):
                resp = {
                    "status": "error",
                    "msg": "device with device_id '%s' not simulating. you need to start simulating it first" % device_id
                }
                return make_response(jsonify(resp), status.HTTP_400_BAD_REQUEST)

            if device_service.is_device_turned_off(device):
                resp = {
                    "status": "success",
                    "msg": "device with device_id '%s' already turned off" % device_id
                }
                return make_response(jsonify(resp), status.HTTP_200_OK)

            device_service.turn_off_device(device, session)
            resp = {
                "status": "success",
                "msg": "turned off device with device_id '%s'" % device_id
            }
            return make_response(jsonify(resp), status.HTTP_200_OK)
    except Exception as e:
        resp = {
            "status": "error",
            "msg": "%s" % str(e)
        }
        return make_response(jsonify(resp), status.HTTP_500_INTERNAL_SERVER_ERROR)


@device_blueprint.route('/energy', methods=['GET', 'POST'])
@jwt_required
def get_device_energy():
    """
    get the energy consumption (kWh or Wh) for the given device since start of current simulation session
    """
    try:
        username = get_jwt_identity()

        req_params = AttrDict(json.loads(request.data))
        device_id = req_params.get("device_id")
        if device_id is None:
            resp = {
                "status": "error",
                "msg": "request body must contain 'device_id'"
            }
            return make_response(jsonify(resp), status.HTTP_400_BAD_REQUEST)

        with session_scope() as session:
            device = device_service.get_device(username, device_id, session)
            if device is None:
                resp = {
                    "status": "error",
                    "msg": "no device with device_id '%s' found for '%s'" % (device_id, username)
                }
                return make_response(jsonify(resp), status.HTTP_404_NOT_FOUND)

            if not device_service.is_device_active(device):
                resp = {
                    "status": "error",
                    "msg": "device with device_id '%s' not active. you need to activate it first" % device_id
                }
                return make_response(jsonify(resp), status.HTTP_400_BAD_REQUEST)

            if not device_service.is_device_simulating(device):
                resp = {
                    "status": "error",
                    "msg": "device with device_id '%s' not simulating. you need to start simulating it first" % device_id
                }
                return make_response(jsonify(resp), status.HTTP_400_BAD_REQUEST)

            measurements = device_service.get_consumption_from_simulation(device)
            if measurements is None:
                resp = {
                    "status": "error",
                    "msg": "no simulator class instance associated with device_id '%s'" % device_id
                }
                return make_response(jsonify(resp), status.HTTP_404_NOT_FOUND)

            resp = {
                "status": "success",
                "msg": "fetched device energy consumption since start of current simulation session",
                "data": {
                    "energy": measurements["energy"]
                }
            }
            return make_response(jsonify(resp), status.HTTP_200_OK)
    except Exception as e:
        resp = {
            "status": "error",
            "msg": "%s" % str(e)
        }
        return make_response(jsonify(resp), status.HTTP_500_INTERNAL_SERVER_ERROR)


@device_blueprint.route('/live_power', methods=['GET', 'POST'])
@jwt_required
def get_device_live_power():
    """
    get live power consumption (W) for the given device directly from simulation
    """

    try:
        username = get_jwt_identity()

        req_params = AttrDict(json.loads(request.data))
        device_id = req_params.get("device_id")
        if device_id is None:
            resp = {
                "status": "error",
                "msg": "request body must contain 'device_id'"
            }
            return make_response(jsonify(resp), status.HTTP_400_BAD_REQUEST)

        with session_scope() as session:
            device = device_service.get_device(username, device_id, session)
            if device is None:
                resp = {
                    "status": "error",
                    "msg": "no device with device_id '%s' found for '%s'" % (device_id, username)
                }
                return make_response(jsonify(resp), status.HTTP_404_NOT_FOUND)

            if not device_service.is_device_active(device):
                resp = {
                    "status": "error",
                    "msg": "device with device_id '%s' not active. you need to activate it first" % device_id
                }
                return make_response(jsonify(resp), status.HTTP_400_BAD_REQUEST)

            if not device_service.is_device_simulating(device):
                resp = {
                    "status": "error",
                    "msg": "device with device_id '%s' not simulating. you need to start simulating it first" % device_id
                }
                return make_response(jsonify(resp), status.HTTP_400_BAD_REQUEST)

            measurements = device_service.get_consumption_from_simulation(device)
            if measurements is None:
                resp = {
                    "status": "error",
                    "msg": "no simulator class instance associated with device_id '%s'" % device_id
                }
                return make_response(jsonify(resp), status.HTTP_404_NOT_FOUND)

            resp = {
                "status": "success",
                "msg": "fetched device live power consumption directly from simulation (i.e., not from db)",
                "data": {
                    "live_power": measurements["power"]
                }
            }
            return make_response(jsonify(resp), status.HTTP_200_OK)
    except Exception as e:
        resp = {
            "status": "error",
            "msg": "%s" % str(e)
        }
        return make_response(jsonify(resp), status.HTTP_500_INTERNAL_SERVER_ERROR)


@device_blueprint.route('/consumption', methods=['GET', 'POST'])
@jwt_required
def get_device_consumption():
    """
    get all historical power consumption data for a device
    """

    try:
        username = get_jwt_identity()

        req_params = AttrDict(json.loads(request.data))
        device_id = req_params.get("device_id")
        if device_id is None:
            resp = {
                "status": "error",
                "msg": "request body must contain 'device_id'"
            }
            return make_response(jsonify(resp), status.HTTP_400_BAD_REQUEST)

        with session_scope() as session:
            device = device_service.get_device(username, device_id, session)
            if device is None:
                resp = {
                    "status": "error",
                    "msg": "no device with device_id '%s' found for '%s'" % (device_id, username)
                }
                return make_response(jsonify(resp), status.HTTP_404_NOT_FOUND)

            if not device_service.is_device_active(device):
                resp = {
                    "status": "error",
                    "msg": "device with device_id '%s' not active. you need to activate it first" % device_id
                }
                return make_response(jsonify(resp), status.HTTP_400_BAD_REQUEST)

            if not device_service.is_device_simulating(device):
                resp = {
                    "status": "error",
                    "msg": "device with device_id '%s' not simulating. you need to start simulating it first" % device_id
                }
                return make_response(jsonify(resp), status.HTTP_400_BAD_REQUEST)

            consumption = device_service.get_device_consumption(device)
            if consumption is None:
                resp = {
                    "status": "error",
                    "msg": "no power consumption data found for device with device_id '%s'" % device_id,
                }
                return make_response(jsonify(resp), status.HTTP_404_NOT_FOUND)

            resp = {
                "status": "success",
                "msg": "fetched {} consumption data records for device with device_id '{}'".format(len(consumption),
                                                                                                   device_id),
                "data": {
                    "consumption": consumption
                }
            }
            return make_response(jsonify(resp), status.HTTP_200_OK)
    except Exception as e:
        resp = {
            "status": "error",
            "msg": "%s" % str(e)
        }
        return make_response(jsonify(resp), status.HTTP_500_INTERNAL_SERVER_ERROR)


@device_blueprint.route('/restore_device_simulations', methods=['POST'])
@admin_required
def restore_device_simulations():
    """

    restore interrupted simulations due to system crash/restart

    :return: a list of restored devices
    """

    try:
        LOGGER.info('restoring simulations that were interrupted due to system crash/restart')
        device_service.restore_device_simulations()

        resp = {
            "status": "info",
            "msg": "Restored simulations that were interrupted due to system crash/restart."
        }

        LOGGER.debug(resp)

        return make_response(jsonify(resp), status.HTTP_200_OK)
    except Exception as e:
        resp = {
            "status": "error",
            "msg": "%s" % str(e)
        }
        return make_response(jsonify(resp), status.HTTP_500_INTERNAL_SERVER_ERROR)


@device_blueprint.route('/find_interrupted_device_simulations', methods=['GET'])
@admin_required
def find_interrupted_device_simulations():
    """

    :return:
    """
    try:
        with session_scope() as session:
            num_interrupted_devices = device_service.find_interrupted_device_simulations(session)

        resp = {
            "status": "info",
            "msg": "found {} devices whose simulation is interrupted due to system crash/restart".format(
                num_interrupted_devices)
        }

        LOGGER.debug(resp)

        return make_response(jsonify(resp), status.HTTP_200_OK)
    except Exception as e:
        resp = {
            "status": "error",
            "msg": "%s" % str(e)
        }
        return make_response(jsonify(resp), status.HTTP_500_INTERNAL_SERVER_ERROR)


@device_blueprint.route('/deactivate', methods=['POST'])
@jwt_required
def deactivate_device():
    """
    deactivate device by removing its id from running simulations dict() and also change device state in db

    """
    try:
        username = get_jwt_identity()

        req_params = AttrDict(json.loads(request.data))
        device_id = req_params.get("device_id")
        if device_id is None:
            resp = {
                "status": "error",
                "msg": "request body must contain 'device_id'"
            }
            return make_response(jsonify(resp), status.HTTP_400_BAD_REQUEST)

        with session_scope() as session:
            device = device_service.get_device(username, device_id, session)
            if device is None:
                resp = {
                    "status": "error",
                    "msg": "no such device exists for '%s'" % username
                }
                return make_response(jsonify(resp), status.HTTP_404_NOT_FOUND)

            is_deactivated, resp = device_service.deactivate_device(device, session)

            if is_deactivated:
                return make_response(jsonify(resp), status.HTTP_200_OK)
            else:
                resp = {
                    "status": "error",
                    "msg": "failed ot deactivate device with device_id '%s'" % device_id
                }
                return make_response(jsonify(resp), status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        resp = {
            "status": "error",
            "msg": "%s" % str(e)
        }
        return make_response(jsonify(resp), status.HTTP_500_INTERNAL_SERVER_ERROR)


@device_blueprint.route('/activate', methods=['POST'])
@jwt_required
def activate_device():
    """
    activate device by adding its id to running simulations dict() and also change device state in db

    """
    try:
        username = get_jwt_identity()

        req_params = AttrDict(json.loads(request.data))
        device_id = req_params.get("device_id")
        if device_id is None:
            resp = {
                "status": "error",
                "msg": "request body must contain 'device_id'"
            }
            return make_response(jsonify(resp), status.HTTP_400_BAD_REQUEST)

        with session_scope() as session:
            device = device_service.get_device(username, device_id, session)
            if device is None:
                resp = {
                    "status": "error",
                    "msg": "no such device exists for '%s'" % username
                }
                return make_response(jsonify(resp), status.HTTP_404_NOT_FOUND)

            is_activated, resp = device_service.activate_device(device, session)

            if is_activated:
                return make_response(jsonify(resp), status.HTTP_200_OK)
            else:
                resp = {
                    "status": "error",
                    "msg": "failed ot activate device with device_id '%s'" % device_id
                }
                return make_response(jsonify(resp), status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        resp = {
            "status": "error",
            "msg": "%s" % str(e)
        }
        return make_response(jsonify(resp), status.HTTP_500_INTERNAL_SERVER_ERROR)

