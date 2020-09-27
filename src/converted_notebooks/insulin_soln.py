# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.4.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # Modeling and Simulation in Python
#
# Insulin minimal model
#
# Copyright 2017 Allen Downey
#
# License: [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0)
#

# +
# Configure Jupyter so figures appear in the notebook
# %matplotlib inline

# Configure Jupyter to display the assigned value after an assignment
# %config InteractiveShell.ast_node_interactivity='last_expr_or_assign'

# import functions from the modsim.py module
from modsim import *
# -

# ### Data
#
# We have data from Pacini and Bergman (1986), "MINMOD: a computer program to calculate insulin sensitivity and pancreatic responsivity from the frequently sampled intravenous glucose tolerance test", *Computer Methods and Programs in Biomedicine*, 23: 113-122..

data = pd.read_csv('data/glucose_insulin.csv', index_col='time');

# ### The insulin minimal model
#
# In addition to the glucose minimal mode, Pacini and Bergman present an insulin minimal model, in which the concentration of insulin, $I$, is governed by this differential equation:
#
# $ \frac{dI}{dt} = -k I(t) + \gamma (G(t) - G_T) t $

# **Exercise:**  Write a version of `make_system` that takes the parameters of this model, `I0`, `k`, `gamma`, and `G_T` as parameters, along with a `DataFrame` containing the measurements, and returns a `System` object suitable for use with `run_simulation` or `run_odeint`.
#
# Use it to make a `System` object with the following parameters:

params = Params(I0 = 360,
                k = 0.25,
                gamma = 0.004,
                G_T = 80)


# +
# Solution

def make_system(params, data):
    # params might be a Params object or an array,
    # so we have to unpack it like this
    I0, k, gamma, G_T = params
    
    init = State(I=I0)
    
    t_0 = get_first_label(data)
    t_end = get_last_label(data)
    G=interpolate(data.glucose)
    
    system = System(I0=I0, k=k, gamma=gamma, G_T=G_T, G=G,
                    init=init, t_0=t_0, t_end=t_end, dt=1)

    return system


# +
# Solution

system = make_system(params, data)


# -

# **Exercise:** Write a slope function that takes state, t, system as parameters and returns the derivative of `I` with respect to time.  Test your function with the initial condition $I(0)=360$.

# +
# Solution

def slope_func(state, t, system):
    [I] = state
    k, gamma = system.k, system.gamma
    G, G_T = system.G, system.G_T
        
    dIdt = -k * I + gamma * (G(t) - G_T) * t
    
    return [dIdt]


# +
# Solution

slope_func(system.init, system.t_0, system)
# -

# **Exercise:** Run `run_ode_solver` with your `System` object and slope function, and plot the results, along with the measured insulin levels.

# +
# Solution

results, details = run_ode_solver(system, slope_func)
details

# +
# Solution

results.tail()

# +
# Solution

plot(results.I, 'g-', label='simulation')
plot(data.insulin, 'go', label='insulin data')

decorate(xlabel='Time (min)',
         ylabel='Concentration ($\mu$U/mL)')


# -

# **Exercise:**  Write an error function that takes a sequence of parameters as an argument, along with the `DataFrame` containing the measurements.  It should make a `System` object with the given parameters, run it, and compute the difference between the results of the simulation and the measured values.  Test your error function by calling it with the parameters from the previous exercise.
#
# Hint: As we did in a previous exercise, you might want to drop the errors for times prior to `t=8`.

# +
# Solution

def error_func(params, data):
    """Computes an array of errors to be minimized.
    
    params: sequence of parameters
    actual: array of values to be matched
    
    returns: array of errors
    """
    print(params)
    
    # make a System with the given parameters
    system = make_system(params, data)

    # solve the ODE
    results, details = run_ode_solver(system, slope_func)

    # compute the difference between the model
    # results and actual data
    errors = (results.I - data.insulin).dropna()
    return TimeSeries(errors.loc[8:])


# +
# Solution

error_func(params, data)
# -

# **Exercise:** Use `leastsq` to find the parameters that best fit the data.  Make a `System` object with those parameters, run it, and plot the results along with the measurements.

# +
# Solution

best_params, details = leastsq(error_func, params, data)
print(details.mesg)

# +
# Solution

system = make_system(best_params, data)

# +
# Solution

results, details = run_ode_solver(system, slope_func, t_eval=data.index)
details

# +
# Solution

plot(results.I, 'g-', label='simulation')
plot(data.insulin, 'go', label='insulin data')

decorate(xlabel='Time (min)',
         ylabel='Concentration ($\mu$U/mL)')
# -

# **Exercise:** Using the best parameters, estimate the sensitivity to glucose of the first and second phase pancreatic responsivity:
#
# $ \phi_1 = \frac{I_{max} - I_b}{k (G_0 - G_b)} $
#
# $ \phi_2 = \gamma \times 10^4 $
#
# For $G_0$, use the best estimate from the glucose model, 290.  For $G_b$ and $I_b$, use the inital measurements from the data.
#

# +
# Solution

I0, k, gamma, G_T = best_params

# +
# Solution

I_max = data.insulin.max()
Ib = data.insulin[0]
I_max, Ib

# +
# Solution

# The value of G0 is the best estimate from the glucose model
G0 = 289
Gb = data.glucose[0]
G0, Gb

# +
# Solution

phi_1 = (I_max - Ib) / k / (G0 - Gb)
phi_1

# +
# Solution

phi_2 = gamma * 1e4
phi_2
# -


