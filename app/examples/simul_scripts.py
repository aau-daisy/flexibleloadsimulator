import logging
import threading
import time

from flask import json
from pyfmi.fmi import load_fmu
from pymodelica import compile_fmu
import pika
import numpy as np


LOGGER = logging.getLogger(__name__)


class SimulationSystem:
    '''This is a simulated physical system'''

    def __init__(self, file_path, model_name, outvars=None):
        sim_fmu = compile_fmu(model_name, file_path, version="1.0")
        self.mod = load_fmu(sim_fmu)
        self.vars = self.mod.get_model_variables()
        self.vars_in = self.mod.get_model_variables(causality = 0)
        print self.vars_in
        if outvars:
            self.vars_out = outvars
        else:
            self.vars_out = self.mod.get_model_variables(causality = 1)
        print self.vars_out
        self.vars_state = self.mod.get_model_variables(causality = 2,variability=3)
        print(self.vars_state)
        self.t = time.time()
        self.dt = 1
        self.control_signal = {v: 0 for v in self.vars_in}
        print(self.control_signal)
        self.res = None
        self.mod.time = self.t
        self.mod.initialize()


        # Setup AMQP
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='test_system', durable=True)
        self.channel.basic_qos(prefetch_count=1)
        print("init done")

        # self.consumer_tag = self.channel.basic_consume(self.on_message, 'test_system')
        # self.channel.start_consuming()


    def consume_messages(self):
        # Get messages and break out

        method_frame, properties, body = self.channel.basic_get('test_system', no_ack=False)

        while method_frame:

            LOGGER.info('Message received')
            # # Acknowledge the message
            self.channel.basic_ack(method_frame.delivery_tag)

            payload = json.loads(body)

            # Process the message
            if isinstance(payload, dict) and 'control' in payload:
                LOGGER.info('A control signal received!')
                self.control_signal = payload['control']

            # Continue getting messages
            method_frame, properties, body = self.channel.basic_get('test_system', no_ack=False)
        print("consume_messages done")


    def getMeasurements(self):
        if self.res:
            return {v : self.res.final(v) for v in self.vars_out}
        return {}

    def setControl(self, new_control):
        self.control_signal = new_control

    def runStep(self):
        self.consume_messages()

        try:
            ctrl = self.control_signal.items()
            ctrl_sig = ([k for k,v in ctrl], np.vstack([(self.t, v) for k, v in ctrl]))
            print("before mod.simulate")
            print(ctrl_sig)
            self.res = self.mod.simulate(self.t, self.t + self.dt, input = ctrl_sig,
                                         options = {'initialize': False, 'CVode_options': {'verbosity': 50}})
            print("after mod.simulate")
        except Exception as e:
            LOGGER.error(e.message)
            LOGGER.error(self.mod.get_log())

        # Sent measurements
        self.channel.basic_publish(exchange='',
                       routing_key='test_system',
                       body=json.dumps({'measurements' : self.getMeasurements()}),
                       properties=pika.BasicProperties(content_type='application/json'))

        LOGGER.info('Measurements sent for time %d', self.t)

        input_vals = {v : self.res.final(v) for v in self.vars_in}
        state_vals = {v : self.res.final(v) for v in self.vars_state}
        output_vals = {v : self.res.final(v) for v in self.vars_out}

        LOGGER.info('Inputs: %s; States: %s; Outputs: %s',
                    ', '.join('{}={}'.format(key, val) for key, val in input_vals.items()),
                    ', '.join('{}={}'.format(key, val) for key, val in state_vals.items()),
                    ', '.join('{}={}'.format(key, val) for key, val in output_vals.items()))

        self.t = self.t + self.dt

    def __del__(self):
        # if self.consumer_tag:
        #     self.channel.basic_cancel(self.consumer_tag)
        self.connection.close()



if __name__ == '__main__':
    logging.basicConfig(level = 'INFO')

    s = SimulationSystem('test.mop', 'LagrangeCost.SimSystem', outvars = None)
    try:
        while True:
            s.runStep()
            t = time.time()
            if t < s.t:
                time.sleep(s.t-t)
    finally:
        del s
