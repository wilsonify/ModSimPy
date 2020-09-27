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
# Chapter 4
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

# import functions from the modsim library
from modsim import *


# -

# ## Returning values

# Here's a simple function that returns a value:

def add_five(x):
    return x + 5


# And here's how we call it.

y = add_five(3)

# If you run a function on the last line of a cell, Jupyter displays the result:

add_five(5)

# But that can be a bad habit, because usually if you call a function and don't assign the result in a variable, the result gets discarded.
#
# In the following example, Jupyter shows the second result, but the first result just disappears.

add_five(3)
add_five(5)

# When you call a function that returns a variable, it is generally a good idea to assign the result to a variable.

# +
y1 = add_five(3)
y2 = add_five(5)

print(y1, y2)


# -

# **Exercise:** Write a function called `make_state` that creates a `State` object with the state variables `olin=10` and `wellesley=2`, and then returns the new `State` object.
#
# Write a line of code that calls `make_state` and assigns the result to a variable named `init`.

# +
# Solution goes here

# +
# Solution goes here
# -

# ## Running simulations

# Here's the code from the previous notebook.

# +
def step(state, p1, p2):
    """Simulate one minute of time.
    
    state: bikeshare State object
    p1: probability of an Olin->Wellesley customer arrival
    p2: probability of a Wellesley->Olin customer arrival
    """
    if flip(p1):
        bike_to_wellesley(state)
    
    if flip(p2):
        bike_to_olin(state)
        
def bike_to_wellesley(state):
    """Move one bike from Olin to Wellesley.
    
    state: bikeshare State object
    """
    if state.olin == 0:
        state.olin_empty += 1
        return
    state.olin -= 1
    state.wellesley += 1
    
def bike_to_olin(state):
    """Move one bike from Wellesley to Olin.
    
    state: bikeshare State object
    """
    if state.wellesley == 0:
        state.wellesley_empty += 1
        return
    state.wellesley -= 1
    state.olin += 1
    
def decorate_bikeshare():
    """Add a title and label the axes."""
    decorate(title='Olin-Wellesley Bikeshare',
             xlabel='Time step (min)', 
             ylabel='Number of bikes')


# -

# Here's a modified version of `run_simulation` that creates a `State` object, runs the simulation, and returns the `State` object.

def run_simulation(p1, p2, num_steps):
    """Simulate the given number of time steps.
    
    p1: probability of an Olin->Wellesley customer arrival
    p2: probability of a Wellesley->Olin customer arrival
    num_steps: number of time steps
    """
    state = State(olin=10, wellesley=2, 
                  olin_empty=0, wellesley_empty=0)
                    
    for i in range(num_steps):
        step(state, p1, p2)
        
    return state


# Now `run_simulation` doesn't plot anything:

state = run_simulation(0.4, 0.2, 60)

# But after the simulation, we can read the metrics from the `State` object.

state.olin_empty

# Now we can run simulations with different values for the parameters.  When `p1` is small, we probably don't run out of bikes at Olin.

state = run_simulation(0.2, 0.2, 60)
state.olin_empty

# When `p1` is large, we probably do.

state = run_simulation(0.6, 0.2, 60)
state.olin_empty

# ## More for loops

# `linspace` creates a NumPy array of equally spaced numbers.

p1_array = linspace(0, 1, 5)

# We can use an array in a `for` loop, like this:

for p1 in p1_array:
    print(p1)

# This will come in handy in the next section.
#
# `linspace` is defined in `modsim.py`.  You can get the documentation using `help`.

help(linspace)

# `linspace` is based on a NumPy function with the same name.  [Click here](https://docs.scipy.org/doc/numpy/reference/generated/numpy.linspace.html) to read more about how to use it.

# **Exercise:** 
# Use `linspace` to make an array of 10 equally spaced numbers from 1 to 10 (including both).

# +
# Solution goes here
# -

# **Exercise:** The `modsim` library provides a related function called `linrange`.  You can view the documentation by running the following cell:

help(linrange)

# Use `linrange` to make an array of numbers from 1 to 11 with a step size of 2.

# +
# Solution goes here
# -

# ## Sweeping parameters

# `p1_array` contains a range of values for `p1`.

p2 = 0.2
num_steps = 60
p1_array = linspace(0, 1, 11)

# The following loop runs a simulation for each value of `p1` in `p1_array`; after each simulation, it prints the number of unhappy customers at the Olin station:

for p1 in p1_array:
    state = run_simulation(p1, p2, num_steps)
    print(p1, state.olin_empty)

# Now we can do the same thing, but storing the results in a `SweepSeries` instead of printing them.
#
#

# +
sweep = SweepSeries()

for p1 in p1_array:
    state = run_simulation(p1, p2, num_steps)
    sweep[p1] = state.olin_empty
# -

# And then we can plot the results.

# +
plot(sweep, label='Olin')

decorate(title='Olin-Wellesley Bikeshare',
         xlabel='Arrival rate at Olin (p1 in customers/min)', 
         ylabel='Number of unhappy customers')
# -

# ## Exercises
#
# **Exercise:** Wrap this code in a function named `sweep_p1` that takes an array called `p1_array` as a parameter.  It should create a new `SweepSeries`, run a simulation for each value of `p1` in `p1_array`, store the results in the `SweepSeries`, and return the `SweepSeries`.
#
# Use your function to plot the number of unhappy customers at Olin as a function of `p1`.  Label the axes.

# +
# Solution goes here

# +
# Solution goes here
# -

# **Exercise:** Write a function called `sweep_p2` that runs simulations with `p1=0.5` and a range of values for `p2`.  It should store the results in a `SweepSeries` and return the `SweepSeries`.
#

# +
# Solution goes here

# +
# Solution goes here
# -

# ## Optional Exercises
#
# The following two exercises are a little more challenging.  If you are comfortable with what you have learned so far, you should give them a try.  If you feel like you have your hands full, you might want to skip them for now.
#
# **Exercise:** Because our simulations are random, the results vary from one run to another, and the results of a parameter sweep tend to be noisy.  We can get a clearer picture of the relationship between a parameter and a metric by running multiple simulations with the same parameter and taking the average of the results.
#
# Write a function called `run_multiple_simulations` that takes as parameters `p1`, `p2`, `num_steps`, and `num_runs`.
#
# `num_runs` specifies how many times it should call `run_simulation`.
#
# After each run, it should store the total number of unhappy customers (at Olin or Wellesley) in a `TimeSeries`.  At the end, it should return the `TimeSeries`.
#
# Test your function with parameters
#
# ```
# p1 = 0.3
# p2 = 0.3
# num_steps = 60
# num_runs = 10
# ```
#
# Display the resulting `TimeSeries` and use the `mean` function provided by the `TimeSeries` object to compute the average number of unhappy customers (see Section 2.7).

# +
# Solution goes here

# +
# Solution goes here
# -

# **Exercise:**  Continuting the previous exercise, use `run_multiple_simulations` to run simulations with a range of values for `p1` and
#
# ```
# p2 = 0.3
# num_steps = 60
# num_runs = 20
# ```
#
# Store the results in a `SweepSeries`, then plot the average number of unhappy customers as a function of `p1`.  Label the axes.
#
# What value of `p1` minimizes the average number of unhappy customers?

# +
# Solution goes here

# +
# Solution goes here
