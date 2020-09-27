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
# Chapter 20
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

# ### Dropping pennies
#
# I'll start by getting the units we need from Pint.

m = UNITS.meter
s = UNITS.second

# And defining the initial state.

init = State(y=381 * m, 
             v=0 * m/s)

# Acceleration due to gravity is about 9.8 m / s$^2$.

g = 9.8 * m/s**2

# I'll start with a duration of 10 seconds and step size 0.1 second.

t_end = 10 * s

dt = 0.1 * s

# Now we make a `System` object.

system = System(init=init, g=g, t_end=t_end, dt=dt)


# And define the slope function.

def slope_func(state, t, system):
    """Compute derivatives of the state.
    
    state: position, velocity
    t: time
    system: System object containing `g`
    
    returns: derivatives of y and v
    """
    y, v = state
    g = system.g    

    dydt = v
    dvdt = -g
    
    return dydt, dvdt


# It's always a good idea to test the slope function with the initial conditions.

dydt, dvdt = slope_func(system.init, 0, system)
print(dydt)
print(dvdt)

# Now we're ready to call `run_ode_solver`

results, details = run_ode_solver(system, slope_func)
details

# Here are the results:

results.head()

results.tail()


# And here's position as a function of time:

# +
def plot_position(results):
    plot(results.y, label='y')
    decorate(xlabel='Time (s)',
             ylabel='Position (m)')

plot_position(results)
savefig('figs/chap20-fig01.pdf')
# -

# ### Onto the sidewalk
#
# To figure out when the penny hit the sidewalk, we can use `crossings`, which finds the times where a `Series` passes through a given value.

t_crossings = crossings(results.y, 0)

# For this example there should be just one crossing, the time when the penny hits the sidewalk.

t_sidewalk = t_crossings[0] * s

# We can compare that to the exact result.  Without air resistance, we have
#
# $v = -g t$
#
# and
#
# $y = 381 - g t^2 / 2$
#
# Setting $y=0$ and solving for $t$ yields
#
# $t = \sqrt{\frac{2 y_{init}}{g}}$

sqrt(2 * init.y / g)


# The estimate is accurate to about 9 decimal places.

# ## Events
#
# Instead of running the simulation until the penny goes through the sidewalk, it would be better to detect the point where the penny hits the sidewalk and stop.  `run_ode_solver` provides exactly the tool we need, **event functions**.
#
# Here's an event function that returns the height of the penny above the sidewalk:

def event_func(state, t, system):
    """Return the height of the penny above the sidewalk.
    """
    y, v = state
    return y


# And here's how we pass it to `run_ode_solver`.  The solver should run until the event function returns 0, and then terminate.

results, details = run_ode_solver(system, slope_func, events=event_func)
details

# The message from the solver indicates the solver stopped because the event we wanted to detect happened.
#
# Here are the results:

results.tail()

# With the `events` option, the solver returns the actual time steps it computed, which are not necessarily equally spaced. 
#
# The last time step is when the event occurred:

t_sidewalk = get_last_label(results) * s

# The result is accurate to about 4 decimal places.
#
# We can also check the velocity of the penny when it hits the sidewalk:

v_sidewalk = get_last_value(results.v)

# And convert to kilometers per hour.

km = UNITS.kilometer
h = UNITS.hour
v_sidewalk.to(km / h)

# If there were no air resistance, the penny would hit the sidewalk (or someone's head) at more than 300 km/h.
#
# So it's a good thing there is air resistance.

# ## Under the hood
#
# Here is the source code for `crossings` so you can see what's happening under the hood:

source_code(crossings)

# The [documentation of InterpolatedUnivariateSpline is here](https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.InterpolatedUnivariateSpline.html).

# ### Exercises
#
# **Exercise:** Here's a question from the web site [Ask an Astronomer](http://curious.astro.cornell.edu/about-us/39-our-solar-system/the-earth/other-catastrophes/57-how-long-would-it-take-the-earth-to-fall-into-the-sun-intermediate):
#
# "If the Earth suddenly stopped orbiting the Sun, I know eventually it would be pulled in by the Sun's gravity and hit it. How long would it take the Earth to hit the Sun? I imagine it would go slowly at first and then pick up speed."
#
# Use `run_ode_solver` to answer this question.
#
# Here are some suggestions about how to proceed:
#
# 1.  Look up the Law of Universal Gravitation and any constants you need.  I suggest you work entirely in SI units: meters, kilograms, and Newtons.
#
# 2.  When the distance between the Earth and the Sun gets small, this system behaves badly, so you should use an event function to stop when the surface of Earth reaches the surface of the Sun.
#
# 3. Express your answer in days, and plot the results as millions of kilometers versus days.
#
# If you read the reply by Dave Rothstein, you will see other ways to solve the problem, and a good discussion of the modeling decisions behind them.
#
# You might also be interested to know that [it's actually not that easy to get to the Sun](https://www.theatlantic.com/science/archive/2018/08/parker-solar-probe-launch-nasa/567197/).

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

# +
# Solution goes here

# +
# Solution goes here

# +
# Solution goes here
# -


