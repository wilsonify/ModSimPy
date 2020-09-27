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

# ### Low pass filter

#

with units_off():
    for i, name in enumerate(dir(UNITS)):
        unit = getattr(UNITS, name)
        try:
            res = 1*unit - 1
            if res == 0:
                print(name, 1*unit - 1)
        except TypeError:
            pass
        if i > 10000:
            break

with units_off():
    print(2 * UNITS.farad - 1)

with units_off():
    print(2 * UNITS.volt - 1)

with units_off():
    print(2 * UNITS.newton - 1)

mN = UNITS.gram * UNITS.meter / UNITS.second**2

with units_off():
    print(2 * mN - 1)

# Now I'll create a `Params` object to contain the quantities we need.  Using a Params object is convenient for grouping the system parameters in a way that's easy to read (and double-check).

params = Params(
    R1 = 1e6, # ohm
    C1 = 1e-9, # farad
    A = 5, # volt
    f = 1000, # Hz 
)


# Now we can pass the `Params` object `make_system` which computes some additional parameters and defines `init`.
#
# `make_system` uses the given radius to compute `area` and the given `v_term` to compute the drag coefficient `C_d`.

def make_system(params):
    """Makes a System object for the given conditions.
    
    params: Params object
    
    returns: System object
    """
    unpack(params)
    
    init = State(V_out = 0)
    omega = 2 * np.pi * f
    tau = R1 * C1
    cutoff = 1 / R1 / C1
    t_end = 3 / f
    
    return System(params, init=init, t_end=t_end,
                  omega=omega, cutoff=cutoff)


# Let's make a `System`

system = make_system(params)


# Here's the slope function,

def slope_func(state, t, system):
    """Compute derivatives of the state.
    
    state: position, velocity
    t: time
    system: System object
    
    returns: derivatives of y and v
    """
    V_out, = state
    unpack(system)
    
    V_in = A * np.cos(omega * t)
    
    V_R1 = V_in - V_out
    
    I_R1 = V_R1 / R1    
    I_C1 = I_R1

    dV_out = I_C1 / C1
    
    return dV_out


# As always, let's test the slope function with the initial conditions.

slope_func(system.init, 0, system)

# And then run the simulation.

ts = linspace(0, system.t_end, 301)
results, details = run_ode_solver(system, slope_func, t_eval=ts)
details


# Here are the results.

# +
# results
# -

#

# Here's the plot of position as a function of time.

# +
def plot_results(results):
    xs = results.V_out.index
    ys = results.V_out.values

    t_end = get_last_label(results)
    if t_end < 10:
        xs *= 1000
        xlabel = 'Time (ms)'
    else:
        xlabel = 'Time (s)'
        
    plot(xs, ys)
    decorate(xlabel=xlabel,
             ylabel='$V_{out}$ (volt)',
             legend=False)
    
plot_results(results)
# -

# And velocity as a function of time:

fs = [1, 10, 100, 1000, 10000, 100000]
for i, f in enumerate(fs):
    system = make_system(Params(params, f=f))
    ts = linspace(0, system.t_end, 301)
    results, details = run_ode_solver(system, slope_func, t_eval=ts)
    subplot(3, 2, i+1)
    plot_results(results)


