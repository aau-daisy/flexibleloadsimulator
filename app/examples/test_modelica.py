import time
from pymodelica import compile_fmu
from pyfmi.fmi import load_fmu
import numpy as np
import matplotlib.pyplot as plt

model_name = "ApplianceModels.Toaster"
file_path = "resources/appliance_models.mo"
output_dir = "output/"
sim_fmu = compile_fmu(model_name, file_path, version="1.0", compile_to=output_dir)
mod = load_fmu(sim_fmu, log_file_name=output_dir+model_name+'.log')

vars = mod.get_model_variables()
vars = [x for x in vars if not x.startswith('_')]
vars_in = mod.get_model_variables(causality = 0)
vars_out = mod.get_model_variables(causality = 1)
vars_state = mod.get_model_variables(causality = 2,variability=3)

print vars
print vars_in
print vars_out
print vars_state

# prepare input signal vector
steps = 10
t = time.time()
#t = 0
tt = np.linspace(t, t+steps, steps)
#u = np.array([1]*(total_steps/4) + [0]*(total_steps/4) + [1]*(total_steps/4) + [0]*(total_steps/4))
u = np.array([1]*(steps/2) + [0]*(steps/2))
u_traj = np.transpose(np.vstack((tt,u)))
print u_traj
input_obj = ('u', u_traj)

mod.set('start_time', t)

print "mod.time", mod.time
opts = mod.simulate_options()
opts['ncp'] = steps
opts['result_file_name'] = output_dir+model_name+'.mat'
#res = mod.simulate(final_time = total_steps, input=input_obj, options=opts)
res = mod.simulate(t, t+10, input=input_obj, options=opts)
y = res["y"]
t = res["time"]
plt.figure()
plt.plot(t,y)
plt.legend(['y'])
plt.show()
