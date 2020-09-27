# -*- coding: utf-8 -*-
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
# Chapter 18
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

# ### Code from the previous chapter
#
# Read the data.

data = pd.read_csv('data/glucose_insulin.csv', index_col='time');

# Interpolate the insulin data.

I = interpolate(data.insulin)

# ### The glucose minimal model
#
# I'll cheat by starting with parameters that fit the data roughly; then we'll see how to improve them.

params = Params(G0 = 290,
                k1 = 0.03,
                k2 = 0.02,
                k3 = 1e-05)


# Here's a version of `make_system` that takes the parameters and data:

def make_system(params, data):
    """Makes a System object with the given parameters.
    
    params: sequence of G0, k1, k2, k3
    data: DataFrame with `glucose` and `insulin`
    
    returns: System object
    """
    G0, k1, k2, k3 = params
    
    Gb = data.glucose[0]
    Ib = data.insulin[0]
    I = interpolate(data.insulin)
    
    t_0 = get_first_label(data)
    t_end = get_last_label(data)

    init = State(G=G0, X=0)
    
    return System(params,
                  init=init, Gb=Gb, Ib=Ib, I=I,
                  t_0=t_0, t_end=t_end, dt=2)


system = make_system(params, data)


# And here's the update function.

def update_func(state, t, system):
    """Updates the glucose minimal model.
    
    state: State object
    t: time in min
    system: System object
    
    returns: State object
    """
    G, X = state
    k1, k2, k3 = system.k1, system.k2, system.k3 
    I, Ib, Gb = system.I, system.Ib, system.Gb
    dt = system.dt
        
    dGdt = -k1 * (G - Gb) - X*G
    dXdt = k3 * (I(t) - Ib) - k2 * X
    
    G += dGdt * dt
    X += dXdt * dt

    return State(G=G, X=X)


# Before running the simulation, it is always a good idea to test the update function using the initial conditions.  In this case we can veryify that the results are at least qualitatively correct.

update_func(system.init, system.t_0, system)


# Now `run_simulation` is pretty much the same as it always is.

def run_simulation(system, update_func):
    """Runs a simulation of the system.
        
    system: System object
    update_func: function that updates state
    
    returns: TimeFrame
    """
    init = system.init
    t_0, t_end, dt = system.t_0, system.t_end, system.dt
    
    frame = TimeFrame(columns=init.index)
    frame.row[t_0] = init
    ts = linrange(t_0, t_end, dt)
    
    for t in ts:
        frame.row[t+dt] = update_func(frame.row[t], t, system)
    
    return frame


# And here's how we run it.

results = run_simulation(system, update_func);

# The results are in a `TimeFrame` object with one column per state variable.

results

# The following plot shows the results of the simulation along with the actual glucose data.

# +
subplot(2, 1, 1)

plot(results.G, 'b-', label='simulation')
plot(data.glucose, 'bo', label='glucose data')
decorate(ylabel='Concentration (mg/dL)')

subplot(2, 1, 2)

plot(results.X, 'C1', label='remote insulin')

decorate(xlabel='Time (min)', 
         ylabel='Concentration (arbitrary units)')

savefig('figs/chap18-fig01.pdf')


# -

# ### Numerical solution
#
# Now let's solve the differential equation numerically using `run_ode_solver`, which is an implementation of Ralston's method.
#
# Instead of an update function, we provide a slope function that evaluates the right-hand side of the differential equations.
#
# We don't have to do the update part; the solver does it for us.

def slope_func(state, t, system):
    """Computes derivatives of the glucose minimal model.
    
    state: State object
    t: time in min
    system: System object
    
    returns: derivatives of G and X
    """
    G, X = state
    k1, k2, k3 = system.k1, system.k2, system.k3 
    I, Ib, Gb = system.I, system.Ib, system.Gb
    
    dGdt = -k1 * (G - Gb) - X*G
    dXdt = k3 * (I(t) - Ib) - k2 * X
    
    return dGdt, dXdt


# We can test the slope function with the initial conditions.

slope_func(system.init, 0, system)

# Here's how we run the ODE solver.

results2, details = run_ode_solver(system, slope_func)

# `details` is a `ModSimSeries` object with information about how the solver worked.

details

# `results` is a `TimeFrame` with one row for each time step and one column for each state variable:

results2

# Plotting the results from `run_simulation` and `run_ode_solver`, we can see that they are not very different.

# +
plot(results.G, 'C0', label='run_simulation')
plot(results2.G, 'C2--', label='run_ode_solver')

decorate(xlabel='Time (min)', ylabel='Concentration (mg/dL)')

savefig('figs/chap18-fig02.pdf')
# -

# The differences in `G` are less than 2%.

diff = results.G - results2.G
percent_diff = diff / results2.G * 100
percent_diff

max(abs(percent_diff))

# ### Exercises
#
# **Exercise:**  Our solution to the differential equations is only approximate because we used a finite step size, `dt=2` minutes.
#
# If we make the step size smaller, we expect the solution to be more accurate.  Run the simulation with `dt=1` and compare the results.  What is the largest relative error between the two solutions?

# +
# Solution

system3 = System(system, dt=1)
results3, details = run_ode_solver(system3, slope_func)
details

# +
# Solution

plot(results2.G, 'C2--', label='run_ode_solver (dt=2)')
plot(results3.G, 'C3:', label='run_ode_solver (dt=1)')

decorate(xlabel='Time (m)', ylabel='mg/dL')

# +
# Solution

diff = (results2.G - results3.G).dropna()
percent_diff = diff / results2.G * 100

# +
# Solution

max(abs(percent_diff))
# -

# ### Under the hood
#
# Here's the source code for `run_ode_solver` if you'd like to know how it works.
#
# Notice that `run_ode_solver` is another name for `run_ralston`, which implements [Ralston's method](https://en.wikipedia.org/wiki/List_of_Runge–Kutta_methods).

source_code(run_ode_solver)

# **Related reading:** You might be interested in this article about [people making a DIY artificial pancreas](https://www.bloomberg.com/news/features/2018-08-08/the-250-biohack-that-s-revolutionizing-life-with-diabetes).


