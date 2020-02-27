import logging
import datetime

from data.model.device import Device
from data.model.device_consumption import DeviceConsumption
from data.model.device_model import DeviceModel
from data.repository import device_repo, user_repo
from service.user_service import UserService


LOGGER = logging.getLogger(__name__)


def user_repo_test():

    user_service = UserService()

    LOGGER.debug("=======USER REPO TEST=======")

    username = "muhaftab"
    password = "1234"
    first_name = "Muhammad"
    last_name = "Aftab"
    email = "muhaftab@cs.aau.dk"

    LOGGER.debug("adding a user")
    user, msg = user_service.add_user(username, password, first_name, last_name, email)
    LOGGER.debug(msg)

    if user is not None:
        LOGGER.debug("fetching the newly added user")
        LOGGER.debug(user_repo.find_by_username(user.username))

    LOGGER.debug("modifying user")
    new_user = {"first_name": "Aftab",
                "last_name": "Khan",
                "email": "muhaftab@cs.aau.dk",
                "password": "5678"}
    updated_user = user_repo.update_user(username, new_user)
    LOGGER.debug("the updated user is")
    LOGGER.debug(updated_user)

    LOGGER.debug("deleting user")
    status = user_repo.delete_user(username)
    LOGGER.debug(status)


def device_repo_test():

    user_service = UserService()

    print "\n\n\n=======DEVICE REPO TEST======="
    print "\ncreating a test user"
    user, msg = user_service.add_user("muhaftab", "1234", "Muhammad", "Aftab", "muhaftab@cs.aau.dk")
    print msg

    print "adding a new device for user:  %s" % user.username
    device1 = device_repo.add_device(user.username, "TableLamp")
    print "returned device is ", device1
    device2 = device_repo.add_device(user.username, "Kettle")
    print "returned device is ", device2

    print "\nfetching the new device from db"
    device = device_repo.find_device(user.username, device1.device_id)[0]
    print device

    print "\nfetching the user to see if device is added for user"
    user = user_service.get_user(user.username)
    print [d.serialize() for d in user.devices]

    print "\nadding some consumption data for the device"
    c1 = DeviceConsumption(10.0, 0.12, False, datetime.datetime.now())
    c2 = DeviceConsumption(11.0, 2.12, True, datetime.datetime.now())
    device_repo.add_device_consumption(device, c1)
    device_repo.add_device_consumption(device, c2)

    print "\ntesting if consumption data is added to device"
    print [c.serialize() for c in device.consumption]

    print "\nModifying device"
    new_device = Device("CoffeeMaker")
    updated_device = device_repo.update_device(user.username, device.device_id, new_device)
    print updated_device

    print "\ntesting if consumption data exists for updated device"
    print [c.serialize() for c in updated_device.consumption]

    print "\nadding device model to the device"
    json_params = {"p_peak": 80.8, "p_stable": 50.0, "lambda": 0.31}
    m1 = DeviceModel("ExponentialDecay", json_params)
    device_repo.add_device_model(updated_device, m1)
    print updated_device.serialize()

    print "\nfetching the user again to see if updated device is shown"
    user = user_service.get_user(user.username)
    print user.serialize()

    print "\nfetching list of devices for the user"
    print [device.serialize() for device in user_service.get_devices(user.username)]

    print "\ndeleting device"
    status = device_repo.delete_device(user.username, device.device_id)
    print status

    print "\nfetching the user agian to see if device is indeed deleted"
    user = user_service.get_user(user.username)
    print [d for d in user.devices]

    print "\nfinally deleting user"
    status = user_service.delete_user(user.username)
    print status
