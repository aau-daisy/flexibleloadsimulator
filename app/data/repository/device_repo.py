import logging

from app.data.model.device import Device
from app.data.model.device_type_enum import DeviceTypeEnum
from app.data.repository import user_repo

LOGGER = logging.getLogger(__name__)


def add_device(username, device_name, session):
    """

    Creates and saves a new user to the database

    :param session:
    :param username: the user whose id to be used as foreign key
    :param device_name: the device name chosen from a set of available devices
    :return: device_id of the newly added device
    """

    new_device = Device(device_name)
    user = user_repo.find_by_username(username, session)
    # new_device.user_id = user.id
    # session.add(new_device)
    user.devices.append(new_device)
    session.commit()

    return new_device


def find_device_by_id(device_id, session):
    """

    Fetches a single device for the device_id

    :param session:
    :param device_id:
    :return:
    """

    devices = session.query(Device).filter(Device.device_id == device_id).all()
    return devices[0] if len(devices) > 0 else None


def find_all(session):
    """

    Fetches all devices for all users

    :return: all devices in db
    """

    devices = session.query(Device).all()
    return devices


def find_active(session):
    """

    Fetches active devices for all users

    :return: all active devices in db
    """

    devices = session.query(Device).filter(Device.device_state != DeviceTypeEnum.INACTIVE).all()
    return devices


def find_device(session, username, device_id=None, serialize=False):
    """

    Fetches a single device if device_id is supplied, else fetches all devices for the given user

    :param session:
    :param username:
    :param device_id:
    :param serialize: whether to return as dictionary or not
    :return: a single device if id specified else all devices for the given user
    """

    user = user_repo.find_by_username(username, session)

    if device_id is None:
        devices = session.query(Device).filter(Device.user_id == user.id).order_by(Device.device_name).all()
    else:
        devices = session.query(Device).filter(Device.user_id == user.id).filter(Device.device_id == device_id).all()

    if serialize:
        return [device.serialize() for device in devices]
    else:
        return devices


def update_device(username, device_id, new_device_name, session):
    """

    Update the details of a device

    :param session:
    :param username: the user that owns the device
    :param device_id:
    :param new_device_name:
    :return: the updated device
    """

    user = user_repo.find_by_username(username, session)

    devices = find_device(session, username, device_id)
    if len(devices) is not 1:
        return None

    device = devices[0]
    device.device_name = new_device_name
    device.device_id = device_id  # device_id should not change
    device.user_id = user.id  # user_id should not change

    session.add(device)
    session.commit()

    updated_device = find_device(session, username, device_id)[0]
    return updated_device


def delete_device(username, device_id, session):
    """

    Delete a device from the database

    :param session:
    :param username:
    :param device_id:
    :return: True if success else false
    """

    user = user_repo.find_by_username(username, session)
    if user is None:
        return False

    device = find_device(session, username, device_id)[0]

    # first approach (first delete related tables (relationships, foreign keys etc)
    device.roles = None
    device.consumption = []
    device.device_model = None
    session.commit()
    items_deleted = session.query(Device).filter(Device.user_id == user.id) \
        .filter(Device.device_id == device_id).delete()

    # # second approach (neater)
    # user = session.query(User).filter(User.id == user_id).all()[0]
    # user.devices.remove(device)

    session.commit()

    return items_deleted > 0


def add_device_model(device, model, session):
    """

    :param session:
    :param device:
    :param model:
    :return:
    """

    device.device_model = model
    session.commit()

    return device


def remove_device_model(device, session):
    """

    :param session:
    :param device:
    :return:
    """

    device.device_model = None
    session.commit()

    return device


def update_device_model(device, new_model, session):
    """

    :param session:
    :param device:
    :param new_model:
    :return:
    """

    remove_device_model(device, session)

    device.device_model = new_model
    session.commit()

    return device


def add_device_consumption(device, value, session):
    """

    :param session:
    :param device:
    :param value:
    :return:
    """

    device.consumption.append(value)
    session.commit()


def get_device_consumption(username, device_id, session):
    """

    Fetches all the consumption data for the given device

    :param session:
    :param username:
    :param device_id:
    :return:
    """

    user = user_repo.find_by_username(username, session)
    if user is None:
        return False

    device = find_device(session, user.username, device_id)[0]
    consumption = [con.serialize() for con in device.consumption]

    return consumption


def set_device_state(device, new_state, session):
    """

    :param session:
    :param device:
    :param new_state:
    :return:
    """

    device.device_state = new_state
    session.commit()

    return device
