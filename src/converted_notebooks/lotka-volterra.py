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
# Implementation of Lotka-Volterra using Euler and `run_ode_solver`
#
# Copyright 2018 Allen Downey
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

# ### Euler with implicit `dt=1`

def run_simulation(system, update_func):
    """Runs a simulation of the system.
        
    system: System object
    update_func: function that updates state
    
    returns: TimeFrame
    """
    unpack(system)
    
    frame = TimeFrame(columns=init.index)
    frame.row[t0] = init
    
    for t in linrange(t0, t_end):
        frame.row[t+1] = update_func(frame.row[t], t, system)
    
    return frame


def update_func(state, t, system):
    """Update the Lotka-Volterra model.
    
    state: State(x, y)
    t: time
    system: System object
    
    returns: State(x, y)
    """
    unpack(system)
    x, y = state

    dxdt = alpha * x - beta * x * y
    dydt = delta * x * y - gamma * y
    
    x += dxdt
    y += dydt
    
    return State(x=x, y=y)


init = State(x=1, y=1)

system = System(alpha=0.05,
                beta=0.1,
                gamma=0.1,
                delta=0.1,
                t0=0,
                t_end=200)

update_func(init, 0, system)

results = run_simulation(system, update_func)
results.head()

results.plot()


# ### Using the ODE solver

def slope_func(state, t, system):
    """Compute slopes for the Lotka-Volterra model.
    
    state: State(x, y)
    t: time
    system: System object
    
    returns: pair of derivatives
    """
    unpack(system)
    x, y = state

    dxdt = alpha * x - beta * x * y
    dydt = delta * x * y - gamma * y
    
    return dxdt, dydt


system.set(init=init, t_end=200)

results, details = run_ode_solver(system, slope_func)
details

results.plot()

system.set(init=init, t_end=200)
results, details = run_ode_solver(system, slope_func, max_step=2)
details

results.plot()

# ### Euler, running for a longer duration

system.set(t_end=2000)
results = run_simulation(system, update_func)
results.head()

results.plot()

# ### Running the ODE solver for a longer duration

results, details = run_ode_solver(system, slope_func)
details

results.plot()


