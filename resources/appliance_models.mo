// Warning: do not use /**/ style comments because Python will have trouble parsing this file
// to get package name and available models

package ApplianceModels

//////////////////////////////////////////////////////////////////////////////
//          Models
//////////////////////////////////////////////////////////////////////////////
model SISOLinearSystem "Heat pump like model" 
  parameter String model_name = "SISOLinearSystem";
  parameter String device_name;
  parameter Real A;
  parameter Real B;
  parameter Real C;
  parameter Real D;
  parameter Modelica.SIunits.Time start_time;
  Real x(start=0);  
  input Modelica.SIunits.Power v(min=-10, max=10);
  input Integer u "on/off control signal";
  output Modelica.SIunits.Power y;
equation
  der(x) = A*x + B*v;
  y = u*(C*x + D*v);  
end SISOLinearSystem;

model OnOff " appliances with two operating states (On/Off) only"
  parameter String model_name = "OnOff ";
  parameter String device_name;
  parameter Modelica.SIunits.Power p_on;
  parameter Modelica.SIunits.Time start_time;
  Real x(start = 0) "state";
  input Integer u "on/off control signal";
  output Modelica.SIunits.Power y "power consumption returned as output";
equation
  der(x) = 1-x; // somehow this is necessary to add
  y = u * p_on "constanct power consumption when control signal is HIGH";
end OnOff;

model ExponentialDecay "appliances whose power consumption follows exponential decay curve"
  parameter String model_name = "ExponentialDecay ";
  parameter String device_name;
  parameter Modelica.SIunits.Power p_peak;
  parameter Modelica.SIunits.Power p_active;
  parameter Real lambda;
  parameter Modelica.SIunits.Time start_time;
  Real x(start = 0);  
  input Integer u "on/off control signal";
  output Modelica.SIunits.Power y "power consumption returned as output";
equation
  der(x) = 1 - x;
  y = u * (p_active + (p_peak - p_active) * Modelica.Math.exp(-lambda * (time-start_time)));
end ExponentialDecay;

model LogarithmicGrowth "appliances whose power consumption follows logarithmic growth curve"
  parameter String model_name = "LogarithmicGrowth ";
  parameter String device_name;
  parameter Modelica.SIunits.Power p_base;
  parameter Real lambda = 0.02;
  parameter Modelica.SIunits.Time start_time;
  Real x(start = 0);  
  input Integer u "on/off control signal";
  output Modelica.SIunits.Power y "power consumption returned as output";
equation
  der(x) = 1 - x;
  y = u * (p_base + lambda*Modelica.Math.log(time-start_time));
end LogarithmicGrowth;

//////////////////////////////////////////////////////////////////////////////


// Derived devices
model HeatPump extends SISOLinearSystem(device_name="HeatPump", A=-0.01, B=0.002, C=1, D=0, start_time=time);
end HeatPump;
model Lamp extends OnOff(device_name="Lamp", p_on=40, start_time=time);
end Lamp;
model Toaster extends ExponentialDecay(device_name="Toaster", p_peak=1470, p_active=1433, lambda=0.02, start_time=time);
end Toaster;
model CoffeeMaker extends ExponentialDecay(device_name="CoffeeMaker", p_peak=990, p_active=905, lambda=0.045, start_time=time);
end CoffeeMaker;
model Refrigerator extends ExponentialDecay(device_name="Refrigerator", p_peak=650.5, p_active=126.19, lambda=0.27, start_time=time);
end Refrigerator;
model AirConditioner extends LogarithmicGrowth(device_name="AirConditioner", p_base=2120.46, lambda=13.78, start_time=time);
end AirConditioner;

end ApplianceModels;
