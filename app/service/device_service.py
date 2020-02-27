import datetime
import logging
import threading
import time
import gc

from app.data.database import session_scope
from app.data.model.device_consumption import DeviceConsumption
from app.data.model.device_type_enum import DeviceTypeEnum
from app.data.repository import device_repo
from app.service.user_service import UserService
from app.simulator.device_simulator import DeviceSimulator
from app.util.app_config import params
# from app.simulator.DeviceSimulator.running_simulations_dict import DeviceSimulator.running_simulations

LOGGER = logging.getLogger(__name__)

# t1 = None
t2 = None
stop_event = threading.Event()


class DeviceService:

    def __init__(self):
        self.device_repo = device_repo

    def create_device(self, username, device_name, session):
        """

        :param username:
        :param device_name:
        :param session:
        :return:
        """
        new_device = self.device_repo.add_device(username, device_name, session)
        return new_device

    def get_device(self, username, device_id, session):
        """

        :param username:
        :param device_id:
        :param session:
        :return:
        """
        new_device = self.device_repo.find_device(session, username, device_id)
        if len(new_device) > 0:
            return new_device[0]
        else:
            return None

    def get_all_devices(self, username, session):
        """

        :param username:
        :param session:
        :return:
        """
        return self.device_repo.find_device(session, username)

    def update_device(self, username, device_id, new_device_name, session):
        """

        :param username:
        :param device_id:
        :param new_device_name:
        :param session:
        :return:
        """
        return self.device_repo.update_device(username, device_id, new_device_name, session)

    def delete_device(self, username, device_id, session):
        """

        :param session:
        :param username:
        :param device_id:
        :return:
        """
        device = self.device_repo.find_device(session, username, device_id)[0]

        # first check if device simulation is running
        # if yes, first stop simulation
        if self.is_device_active(device):
            DeviceService.stop_simulation(device)

        # then delete the device
        return self.device_repo.delete_device(username, device_id, session)

    def add_device_model(self, device, model, session):
        """

        :param session:
        :param device:
        :param model:
        :return:
        """
        self.device_repo.add_device_model(device, model, session)
        return device

    def remove_device_model(self, device, session):
        """

        :param session:
        :param device:
        :return:
        """
        self.device_repo.remove_device_model(device, session)
        return device

    def update_device_model(self, device, new_model, session):
        """

        :param session:
        :param device:
        :param new_model:
        :return:
        """
        self.device_repo.update_device_model(device, new_model, session)
        return device

    def start_simulation(self, device, session):
        """

        start simulating the device to enable sending control command and query consumption data

        :param session:
        :param device:
        :return:
        """
        try:
            if device.device_id in DeviceSimulator.running_simulations:
                resp = {
                    "status": "info",
                    "msg": "simulation of device with id: '%s' already running" % device.device_id
                }
                LOGGER.debug(resp)
                return True, resp

            simulation = DeviceSimulator(
                fmu_name=params.model.package_name + "_" + device.device_model.model_name,
                fmu_dir=params.model.fmu_dir,
                device_name=device.device_name,
                device_id=device.device_id,
                model_params=device.device_model.params,
                output_dir=params.model.output_dir
            )
            # simulation.start() # commented as we moved away from thread based approach
            DeviceSimulator.running_simulations[device.device_id] = simulation

            if not self.is_device_active(device):
                self.device_repo.set_device_state(device, DeviceTypeEnum.ACTIVE, session)

            resp = {
                "status": "success",
                "msg": "restored device simulation",
                "data": device.serialize()
            }
            LOGGER.debug(resp)
            return True, resp

        except Exception as e:
            LOGGER.error(e)
            return False, e

    @staticmethod
    def stop_simulation(device):
        """

        :param device:
        :return:
        """
        try:
            if device.device_id not in DeviceSimulator.running_simulations:
                resp = {
                    "status": "info",
                    "msg": "simulation of device with id: '%s' already stopped" % device.device_id
                }
                LOGGER.debug(resp)
                return True, resp

            # DeviceSimulator.running_simulations[device.device_id].stop.set()
            # DeviceSimulator.running_simulations[device.device_id].join()
            del DeviceSimulator.running_simulations[device.device_id]
            # self.device_repo.set_device_state(device, DeviceTypeEnum.INACTIVE, session)

            resp = {
                "status": "success",
                "msg": "simulation of device with id: '%s' stopped" % device.device_id
            }
            LOGGER.debug(resp)
            return True, resp

        except Exception as e:
            LOGGER.error(e)
            return False, e

    def deactivate_device(self, device, session):
        """

        :param session:
        :param device:
        :return:
        """
        try:
            if not self.is_device_active(device):
                resp = {
                    "status": "info",
                    "msg": "Device with id: '%s' already deactivated" % device.device_id
                }
                LOGGER.debug(resp)
                return True, resp

            if device.device_id in DeviceSimulator.running_simulations:
                del DeviceSimulator.running_simulations[device.device_id]

            self.device_repo.set_device_state(device, DeviceTypeEnum.INACTIVE, session)

            resp = {
                "status": "success",
                "msg": "Device with id: '%s' deactivated" % device.device_id
            }
            LOGGER.debug(resp)
            return True, resp

        except Exception as e:
            LOGGER.error(e)
            return False, e

    def activate_device(self, device, session):
        """

        :param session:
        :param device:
        :return:
        """
        try:
            if self.is_device_active(device) and device.device_id in DeviceSimulator.running_simulations:
                resp = {
                    "status": "info",
                    "msg": "Device with id: '%s' already activated" % device.device_id
                }
                LOGGER.debug(resp)
                return True, resp

            self.start_simulation(device, session)

            resp = {
                "status": "success",
                "msg": "Device with id: '%s' activated" % device.device_id
            }
            LOGGER.debug(resp)
            return True, resp

        except Exception as e:
            LOGGER.error(e)
            return False, e

    def turn_on_device(self, device, session):
        DeviceSimulator.running_simulations[device.device_id].set_control({'u': 1.0})
        self.device_repo.set_device_state(device, DeviceTypeEnum.ON, session)

    def turn_off_device(self, device, session):
        DeviceSimulator.running_simulations[device.device_id].set_control({'u': 0.0})
        self.device_repo.set_device_state(device, DeviceTypeEnum.OFF, session)

    def get_all_devices_for_all_users(self, session):
        return self.device_repo.find_all(session)

    def find_interrupted_device_simulations(self, session):
        return len(self.device_repo.find_active(session)) - len(DeviceSimulator.running_simulations)

    @staticmethod
    def stop_all_active_devices(session):
        """
        Stop simulation of all active devices for the all users by stopping their respective threads
        """
        for device in DeviceSimulator.running_simulations:
            print device
        users = UserService.get_all_users(session)

        for user in users:
            if not user.devices.count() > 0:
                LOGGER.info("no active devices to stop for '{}'".format(user.username))
                continue

            LOGGER.info("Stopping simulation of all active devices for '{}'".format(user.username))
            for device in user.devices:
                DeviceService.stop_simulation(device)

            LOGGER.info("Stopped all active devices for '{}'".format(user.username))

    @staticmethod
    def validate_device_params(device_params):
        """
        :param device_params:
        :return:
        """
        try:
            model_name = device_params.model_name
            model_params = device_params.params

            available_models = [m.name for m in params.model.available_models]
            if model_name not in available_models:
                resp = {
                    "status": "error",
                    "msg": "invalid model_type. valid models are: %s" % available_models
                }
                return False, resp

            model = [m for m in params.model.available_models if m.name == model_name][0]
            for key in model_params:
                if key not in model.params.keys():
                    resp = {
                        "status": "error",
                        "msg": "invalid model parameters. valid parameters are: %s" % model.params.keys()
                    }
                    return False, resp
            for key, val in model_params.items():
                if val > model.params(key).max or val < model.params(key).min:
                    resp = {
                        "status": "error",
                        "msg": "parameter value out of range. parameter: %s, valid range: [min:%.1f, max:%.1f]" \
                               % (key, model.params(key).min, model.params(key).max)
                    }
                    return False, resp

            resp = {
                "status": "error",
                "msg": "device parameters are valid"
            }
            return True, resp
        except Exception as e:
            resp = {
                "status": "error",
                "msg": "{}".format(e)
            }

            return False, resp

    @staticmethod
    def is_device_active(device):
        """
        :param device:
        :return True if active:
        """
        return device.device_state != DeviceTypeEnum.INACTIVE

    @staticmethod
    def is_device_turned_on(device):
        return device.device_state == DeviceTypeEnum.ON

    @staticmethod
    def is_device_simulating(device):
        return device.device_id in DeviceSimulator.running_simulations

    @staticmethod
    def is_device_turned_off(device):
        return device.device_state == DeviceTypeEnum.OFF

    @staticmethod
    def get_consumption_from_simulation(device):
        try:
            return DeviceSimulator.running_simulations[device.device_id].get_measurements()
        except Exception as e:
            LOGGER.error(e)
            return None

    @staticmethod
    def stop_all_simulations():
        """
        Stop simulation of all devices
        """
        lock = threading.Lock()
        lock.acquire()
        for device_id in DeviceSimulator.running_simulations.keys():
            del DeviceSimulator.running_simulations[device_id]
        lock.release()
        LOGGER.info("Stopped all simulations")

    @staticmethod
    def get_device_consumption(device):
        """
        :param device:
        :return:
        """
        return [row.serialize() for row in device.consumption]

    def restore_device_simulations(self):
        """
        fetch all devices from the database, and start the device simulation if device state is 'active'
        but simulation is not running
        :return:
        """
        LOGGER.info('Restoring device simulations')
        lock = threading.Lock()
        lock.acquire()
        with session_scope() as session:
            all_devices = self.get_all_devices_for_all_users(session)
            for device in all_devices:
                if device.device_state != DeviceTypeEnum.INACTIVE \
                        and device.device_id not in DeviceSimulator.running_simulations:
                    LOGGER.debug("device_id={}, device_state={},  is_device__simulation_running={}".format(
                        device.device_id, device.device_state, device.device_id in DeviceSimulator.running_simulations))
                    self.start_simulation(device, session)
                    if device.device_state == DeviceTypeEnum.ON:
                        self.turn_on_device(device, session)
        lock.release()

    @staticmethod
    def store_device_consumption_data():
        """
        stores power consumption for each active device
        :return:
        """
        global t2
        if len(DeviceSimulator.running_simulations) > 0:
            with session_scope() as session:
                try:
                    LOGGER.info("Storing device consumption data")
                    for device_id in DeviceSimulator.running_simulations:

                        device = device_repo.find_device_by_id(device_id, session)
                        if device.device_state != DeviceTypeEnum.ON:
                            continue

                        measurement = DeviceSimulator.running_simulations[device_id].get_measurements()
                        power = measurement["power"]
                        energy = measurement["energy"]
                        state = DeviceSimulator.running_simulations[device_id].get_power_state()

                        device_consumption = DeviceConsumption(power, energy, state, datetime.datetime.now())
                        if device is not None:
                            device_repo.add_device_consumption(device, device_consumption, session)

                    LOGGER.debug("completed storing device consumption data")
                except Exception as e:
                    LOGGER.error(e)
        t2 = threading.Timer(params.device.storage_interval, DeviceService.store_device_consumption_data)
        t2.start()

    @staticmethod
    def run_simulation():
        # global t1
        while not stop_event.is_set():
            LOGGER.debug("Executing simulation step for all active loads!")
            start_time = time.time()
            lock = threading.Lock()
            lock.acquire()
            for device_id in DeviceSimulator.running_simulations.keys():
                LOGGER.debug("Running simulation of device with id: %s" % device_id)
                DeviceSimulator.running_simulations[device_id].run_step()  # run simulation
                DeviceSimulator.running_simulations[device_id].print_info(print_extra=False)  # print debug info
            lock.release()
            time.sleep(1.0)
            gc.collect()
            LOGGER.info("Simulation step completed. Time taken: {:.2f} seconds. Number of devices: {}".format(time.time()-start_time, len(DeviceSimulator.running_simulations)))
            # t1 = threading.Timer(15, DeviceService.run_simulation)
            # t1.start()
        LOGGER.warn("Simulation thread stopped")

    @staticmethod
    def start_threads():
        """
        threading.Timer run a function periodically. first param is interval in seconds
        second param is the target function
        :return:
        """
        LOGGER.info('Starting thread to restore simulations that were interrupted due to system crash/restart')
        t = threading.Thread(target=DeviceService().restore_device_simulations)
        t.setDaemon(True)
        t.start()

        LOGGER.info('Starting thread for periodic running of device simulations')
        tt = threading.Thread(target=DeviceService.run_simulation)
        tt.setDaemon(True)
        tt.start()
        # DeviceService.run_simulation()

        LOGGER.info('Starting thread for periodic storage of device consumption data')
        DeviceService.store_device_consumption_data()

    @staticmethod
    def stop_threads():
        # global t1
        global t2
        # t1.cancel()
        t2.cancel()
        stop_event.set()
        LOGGER.info('Stopped all threads')

