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
# Chapter 16
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

# ## Code from previous notebooks

def update_func(state, t, system):
    """Update the thermal transfer model.
    
    state: State (temp)
    t: time
    system: System object
    
    returns: State (temp)
    """
    r, T_env, dt = system.r, system.T_env, system.dt
    
    T = state.T
    T += -r * (T - T_env) * dt
    
    return State(T=T)


def run_simulation(system, update_func):
    """Runs a simulation of the system.
    
    Add a TimeFrame to the System: results
    
    system: System object
    update_func: function that updates state
    """
    init = system.init
    t_0, t_end, dt = system.t_0, system.t_end, system.dt
    
    frame = TimeFrame(columns=init.index)
    frame.row[t_0] = init
    ts = linrange(t_0, t_end, dt)
    
    for t in ts:
        frame.row[t+dt] = update_func(frame.row[t], t, system)
    
    return frame


def make_system(T_init, r, volume, t_end):
    """Makes a System object with the given parameters.

    T_init: initial temperature in degC
    r: heat transfer rate, in 1/min
    volume: volume of liquid in mL
    t_end: end time of simulation
    
    returns: System object
    """
    init = State(T=T_init)
                   
    return System(init=init,
                  r=r, 
                  volume=volume,
                  temp=T_init,
                  t_0=0, 
                  t_end=t_end, 
                  dt=1,
                  T_env=22)


# ### Using `root_bisect`
#
# As a simple example, let's find the roots of this function; that is, the values of `x` that make the result 0.

def func(x):
    return (x-1) * (x-2) * (x-3)


# `modsim.py` provides `root_bisect`, which searches for a root by bisection.  The first argument is the function whose roots we want.  The second argument is an interval that contains a root.

res = root_bisect(func, [0.5, 1.5])

# The result is an object that contains the root that was found and other information.

res.root

# If we provide a different interval, we find a different root.

res = root_bisect(func, [1.5, 2.5])

res.root

# If the interval doesn't contain a root, the results explain the error.

res = root_bisect(func, [4, 5])


# We want to find the value of `r` that makes the final temperature 70, so we define an "error function" that takes `r` as a parameter and returns the difference between the final temperature and the goal.

def error_func1(r):
    """Runs a simulation and returns the `error`.
    
    r: heat transfer rate, in 1/min
    
    returns: difference between final temp and 70 C
    """
    system = make_system(T_init=90, r=r, volume=300, t_end=30)
    results = run_simulation(system, update_func)
    T_final = get_last_value(results.T)
    return T_final - 70


# With `r=0.01`, we end up a little too warm.

error_func1(r=0.01)

# With `r=0.02`, we end up too cold.

error_func1(r=0.02)

# The return value from `root_bisect` is an array with a single element, the estimated value of `r`.

res = root_bisect(error_func1, [0.01, 0.02])

r_coffee = res.root

# If we run the simulation with the estimated value of `r`, the final temperature is 70 C, as expected.

coffee = make_system(T_init=90, r=r_coffee, volume=300, t_end=30)
results = run_simulation(coffee, update_func)
T_final = get_last_value(results.T)

# **Exercise:**  When you call `root_bisect`, it calls `error_func1` several times.  To see how this works, add a print statement to `error_func1` and run `root_bisect` again.

# **Exercise:** Repeat this process to estimate `r_milk`, given that it starts at 5 C and reaches 20 C after 15 minutes.  
#
# Before you use `root_bisect`, you might want to try a few values for `r_milk` and see how close you can get by trial and error.  Here's an initial guess to get you started:

r_milk = 0.1
milk = make_system(T_init=5, r=r_milk, volume=50, t_end=15)
results = run_simulation(milk, update_func)
T_final = get_last_value(results.T)


# +
# Solution goes here

# +
# Solution goes here

# +
# Solution goes here

# +
# Solution goes here

# +
# Solution goes here

# +
# Solution goes here
# -

# ### Mixing liquids

# The following function takes `System` objects that represent two liquids, computes the temperature of the mixture, and returns a new `System` object that represents the mixture.

def mix(system1, system2):
    """Simulates the mixture of two liquids.
    
    system1: System representing coffee
    system2: System representing milk
    
    returns: System representing the mixture
    """
    assert system1.t_end == system2.t_end
    
    V1, V2 = system1.volume, system2.volume
    T1, T2 = system1.temp, system2.temp
    
    V_mix = V1 + V2
    T_mix = (V1 * T1 + V2 * T2) / V_mix
    
    return make_system(T_init=T_mix,
                       r=system1.r,
                       volume=V_mix,
                       t_end=30)


# `mix` requires the `System` objects to have `temp` as a system variable.  `make_system` initializes this variable;
# the following function makes sure it gets updated when we run a simulation.

def run_and_set(system):
    """Run a simulation and set the final temperature.
    
    system: System
    
    returns: TimeFrame
    """
    results = run_simulation(system, update_func)
    system.temp = get_last_value(results.T)
    return results


# ## Mixing immediately
#
# Next here's what we get if we add the milk immediately.

coffee = make_system(T_init=90, r=r_coffee, volume=300, t_end=30)
coffee.temp

milk = make_system(T_init=5, r=r_milk, volume=50, t_end=30)
milk.temp

mix_first = mix(coffee, milk)
mix_first.temp

mix_results = run_and_set(mix_first)
mix_first.temp

# ## Mixing at the end
#
# First we'll see what happens if we add the milk at the end.  We'll simulate the coffee and the milk separately.

coffee_results = run_and_set(coffee)
coffee.temp

milk_results = run_and_set(milk)
milk.temp

# Here's what the results look like.

# +
plot(coffee_results.T, label='coffee')
plot(milk_results.T, '--', label='milk')

decorate(xlabel='Time (minutes)',
         ylabel='Temperature (C)',
         loc='center left')

savefig('figs/chap16-fig01.pdf')
# -

# Here's what happens when we mix them.

mix_last = mix(coffee, milk)
mix_last.temp

mix_last.temp - mix_first.temp


# The following function takes `t_add`, which is the time when the milk is added, and returns the final temperature.

def run_and_mix(t_add, t_total):
    """Simulates two liquids and them mixes them at t_add.
    
    t_add: time in minutes
    t_total: total time to simulate, min
    
    returns: final temperature
    """
    coffee = make_system(T_init=90, r=r_coffee, volume=300, t_end=t_add)
    coffee_results = run_and_set(coffee)
    
    milk = make_system(T_init=5, r=r_milk, volume=50, t_end=t_add)
    milk_results = run_and_set(milk)
    
    mixture = mix(coffee, milk)
    mixture.t_end = t_total - t_add
    results = run_and_set(mixture)

    return mixture.temp


# We can try it out with a few values.

run_and_mix(t_add=0, t_total=30)

run_and_mix(t_add=15, t_total=30)

run_and_mix(t_add=30, t_total=30)

# And then sweep a range of values for `t_add`

sweep = SweepSeries()
for t_add in linspace(0, 30, 11):
    sweep[t_add] = run_and_mix(t_add, 30)

# Here's what the result looks like.

# +
plot(sweep, label='final temp', color='C2')
decorate(xlabel='Time added (min)',
         ylabel='Final temperature (C)')

savefig('figs/chap16-fig02.pdf')


# -

# ### Analysis

# Now we can use the analytic result to compute temperature as a function of time.  The following function is similar to `run_simulation`.

def run_analysis(system):
    """Computes temperature using the analytic solution.
        
    system: System object
    
    returns: TimeFrame
    """
    T_env, r = system.T_env, system.r
    
    T_init = system.init.T    
    ts = linspace(0, system.t_end)
    
    T_array = T_env + (T_init - T_env) * exp(-r * ts)
    
    # to be consistent with run_simulation,
    # we put the array into a TimeFrame
    return TimeFrame(T_array, index=ts, columns=['T'])


# Here's how we run it.  From the analysis (see `chap16sympy.ipynb`), we have the computed value of `r_coffee2`

r_coffee2 = 0.011610223142273859
coffee2 = make_system(T_init=90, r=r_coffee2, volume=300, t_end=30)

results = run_analysis(coffee2)
T_final_analysis = get_last_value(results.T)

# And we can compare to the results from simulation.

coffee = make_system(T_init=90, r=r_coffee, volume=300, t_end=30)
results = run_simulation(coffee, update_func)
T_final_simulation = get_last_value(results.T)

# They are identical except for a small roundoff error.

T_final_analysis - T_final_simulation

# ## Exercises
#
# **Exercise:**  Suppose the coffee shop won't let me take milk in a separate container, but I keep a bottle of milk in the refrigerator at my office.  In that case is it better to add the milk at the coffee shop, or wait until I get to the office?
#
# Hint: Think about the simplest way to represent the behavior of a refrigerator in this model.  The change you make to test this variation of the problem should be very small!

# +
# Solution goes here
# -


