import logging
import threading
import time
import numpy as np

from pyfmi.fmi import load_fmu

LOGGER = logging.getLogger(__name__)
Ws2kWh = 0.0000002777778  # 1 watt-second  =  2.777778e-7 kilowatt-hour


class DeviceSimulator:
    """This class provides a simulation of a physical electric device"""

    running_simulations = dict()

    def __init__(self, fmu_name, fmu_dir, device_name, device_id, model_params, output_dir):

        # load_fmu returns a class instance from a FMU
        # the class instance can be used for simulations
        self.model = load_fmu(
            fmu_name + ".fmu",
            path=fmu_dir,
            log_file_name=output_dir + device_name + '_' + device_id + '.log',
            log_level=2
        )

        self.model_params = model_params
        self.device_id = device_id
        self.device_name = device_name
        self.t = time.time()

        # set model parameters
        self.setup()

        # setup simulation options
        opts = self.model.simulate_options()
        # opts['ncp'] = total_steps # total generated output points
        opts['result_file_name'] = output_dir + device_name + '_' + device_id + '.mat'
        opts['initialize'] = False
        opts['CVode_options'] = {'verbosity': 50}
        self.opts = opts

        self.vars = self.model.get_model_variables().keys()

        # version == "1.0" in compile_fmu():
        # self.vars_in = self.model.get_model_variables(causality=0).keys()
        # self.vars_out = self.model.get_model_variables(causality=1).keys()
        # self.vars_state = self.model.get_model_variables(causality=2, variability=3).keys()

        # version == "2.0" in compile_fmu():
        self.vars_in = self.model.get_model_variables(causality=2).keys()
        self.vars_out = self.model.get_model_variables(causality=3).keys()
        self.vars_state = self.model.get_model_variables(causality=4, variability=4).keys()

        self.dt = 1
        self.control_signal = {v: 0 for v in self.vars_in}
        self.res = None

        self.power_state = 0
        self.just_turned_on = False
        self.total_power_reading = 0
        self.live_power_reading = 0

        ## Control period (not implemented yet)
        # self.control_period_start = time.time()
        # self.control_period_end = self.control_period_start
        # self.period_reading = None
        # self.period_target = None

        DeviceSimulator.running_simulations[self.device_id] = self

    def setup(self):
        self.model.reset()
        self.model.set('device_name', self.device_name)
        for param in self.model_params:
            self.model.set(param, self.model_params[param])
        self.model.time = self.t
        self.model.initialize()

    def set_control(self, new_control):
        new_state = bool(float(new_control['u']))
        self.just_turned_on = True if (not self.power_state and new_state) else False
        self.power_state = new_state
        self.control_signal = new_control

    def get_measurements(self):
        data = dict()
        data['power'] = self.live_power_reading
        data['energy'] = self.total_power_reading * Ws2kWh
        return data
        #if self.res:
        #    data['power'] = self.live_power_reading
        #    data['energy'] = self.total_power_reading * Ws2kWh
        #    return data
        #return {}

    def get_power_state(self):
        return self.power_state

    def run_step(self):
        """
        run simulation
        """

        LOGGER.debug("Running simulation step for device_id: '%s'" % self.device_id)
        try:
            ctrl = self.control_signal.items()
            ctrl_sig = ([k for k, v in ctrl], np.vstack([(self.t, v) for k, v in ctrl]))

            # reset model's internal clock every time device is turned on
            if self.just_turned_on:
                self.setup()
                self.just_turned_on = False

            self.res = self.model.simulate(self.t, self.t + self.dt, input=ctrl_sig, options=self.opts)
            output_values = {v: self.res.final(v) for v in self.vars_out}
            self.live_power_reading = output_values['y']
            self.total_power_reading += self.live_power_reading
        except Exception as e:
            LOGGER.error(e.message)
            LOGGER.error(self.model.get_log())

        self.t = self.t + self.dt

    def print_info(self, print_extra=False):
        LOGGER.debug("Power: {:.2f}\t Energy : {:.5f}"
                    .format(self.live_power_reading, self.total_power_reading * Ws2kWh))

        if print_extra:
            input_vals = {v: self.res.final(v) for v in self.vars_in}
            state_vals = {v: self.res.final(v) for v in self.vars_state}
            output_vals = {v: self.res.final(v) for v in self.vars_out}
            LOGGER.debug("Inputs: %s; States: %s; Outputs: %s",
                         ", ".join("{}={}".format(key, val) for key, val in input_vals.items()),
                         ", ".join("{}={}".format(key, val) for key, val in state_vals.items()),
                         ", ".join("{}={}".format(key, val) for key, val in output_vals.items()))

    def serialize(self):
        return {
            "device_name": self.device_name,
            "device_id": self.device_id,
            "model_params": self.model_params,
            "input_variables": self.vars_in,
            "output_variables": self.vars_out,
            "control_signal": self.control_signal,
            "power_state": self.power_state,
            "live_power": self.live_power_reading,
            "total_energy": self.total_power_reading * Ws2kWh
        }

    def __repr__(self):
        return "<%s(device_name='%s', device_id='%s', power_reading='%.1f', model_params='%s')>" \
               % (self.__class__.__name__, self.device_name, self.device_id,
                  self.live_power_reading, str(self.model_params))

    def __del__(self):
        LOGGER.debug("Deleted DeviceSimulator class instance")


class DeviceSimulatorThreaded(threading.Thread):
    """This class provides a simulation of a physical electric device"""

    def __init__(self, fmu_name, fmu_dir, device_name, device_id, model_params, output_dir):

        # setup threading
        threading.Thread.__init__(self)
        # A flag indicating whether the device simulation should be terminated
        self.stop = threading.Event()

        # load_fmu returns a class instance from a FMU
        # the class instance can be used for simulations
        self.model = load_fmu(
            fmu_name + ".fmu",
            path=fmu_dir,
            log_file_name=output_dir + device_name + '_' + device_id + '.log',
            log_level=7
        )

        self.model_params = model_params
        self.device_id = device_id
        self.device_name = device_name
        self.t = time.time()

        # set model parameters
        self.setup()

        # setup simulation options
        opts = self.model.simulate_options()
        # opts['ncp'] = total_steps # total generated output points
        opts['result_file_name'] = output_dir + device_name + '_' + device_id + '.mat'
        opts['initialize'] = False
        opts['CVode_options'] = {'verbosity': 50}
        self.opts = opts

        self.vars = self.model.get_model_variables().keys()
        self.vars_in = self.model.get_model_variables(causality=0).keys()
        self.vars_out = self.model.get_model_variables(causality=1).keys()
        self.vars_state = self.model.get_model_variables(causality=2, variability=3).keys()
        self.dt = 1
        self.control_signal = {v: 0 for v in self.vars_in}
        self.res = None

        self.power_state = 0
        self.just_turned_on = False
        self.total_power_reading = 0
        self.live_power_reading = 0

        #  #Control period (not implemented yet)
        # self.control_period_start = time.time()
        # self.control_period_end = self.control_period_start
        # self.period_reading = None
        # self.period_target = None

    def setup(self):
        self.model.reset()
        self.model.set('device_name', self.device_name)
        for param in self.model_params:
            self.model.set(param, self.model_params[param])
        self.model.time = self.t
        self.model.initialize()

    def set_control(self, new_control):
        new_state = bool(float(new_control['u']))
        self.just_turned_on = True if (not self.power_state and new_state) else False
        self.power_state = new_state
        self.control_signal = new_control

    def get_measurements(self):
        if self.res:
            data = dict()
            data['power'] = self.live_power_reading
            data['energy'] = self.total_power_reading * Ws2kWh
            return data
        return {}

    def get_power_state(self):
        return self.power_state

    def run_step(self):
        """
        run simulation
        """

        LOGGER.debug("Running simulation step for device_id: '%s'" % self.device_id)
        try:
            ctrl = self.control_signal.items()
            ctrl_sig = ([k for k, v in ctrl], np.vstack([(self.t, v) for k, v in ctrl]))

            # reset model's internal clock every time device is turned on
            if self.just_turned_on:
                self.setup()
                self.just_turned_on = False

            self.res = self.model.simulate(self.t, self.t + self.dt, input=ctrl_sig, options=self.opts)
            output_values = {v: self.res.final(v) for v in self.vars_out}
            self.live_power_reading = output_values['y']
            self.total_power_reading += self.live_power_reading
        except Exception as e:
            LOGGER.error(e.message)
            LOGGER.error(self.model.get_log())

        self.t = self.t + self.dt

    def run(self):
        LOGGER.info("Starting simulation of device with id: %s" % self.device_id)
        while not self.stop.is_set():
            # self.consume_messages() # get message from MQTT queue
            self.run_step()  # run simulation
            # self.produce_messages() # simulation done, add results to MQTT queue
            self.print_info(print_extra=False)  # print debug info
            t = time.time()
            if t < self.t:
                time.sleep(self.t - t)

        # self.model.terminate()
        LOGGER.info("Stopped simulation of device with id: %s" % self.device_id)

    def print_info(self, print_extra=False):
        LOGGER.debug("Power: %.1f\t Energy : %.5f" % (self.live_power_reading, self.total_power_reading * Ws2kWh))

        if print_extra:
            input_vals = {v: self.res.final(v) for v in self.vars_in}
            state_vals = {v: self.res.final(v) for v in self.vars_state}
            output_vals = {v: self.res.final(v) for v in self.vars_out}
            LOGGER.debug("Inputs: %s; States: %s; Outputs: %s",
                         ", ".join("{}={}".format(key, val) for key, val in input_vals.items()),
                         ", ".join("{}={}".format(key, val) for key, val in state_vals.items()),
                         ", ".join("{}={}".format(key, val) for key, val in output_vals.items()))

    def serialize(self):
        return {
            "device_name": self.device_name,
            "device_id": self.device_id,
            "model_params": self.model_params,
            "input_variables": self.vars_in,
            "output_variables": self.vars_out,
            "control_signal": self.control_signal,
            "power_state": self.power_state,
            "live_power": self.live_power_reading,
            "total_energy": self.total_power_reading * Ws2kWh
        }

    def __repr__(self):
        return "<%s(device_name='%s', device_id='%s', power_reading='%.1f', model_params='%s')>" \
               % (self.__class__.__name__, self.device_name, self.device_id,
                  self.live_power_reading, str(self.model_params))

    def __del__(self):
        LOGGER.debug("Deleted DeviceSimulator class instance")
