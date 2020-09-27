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

# ### Earth orbit
#

# +
# Here are the units we'll need

s = UNITS.second
N = UNITS.newton
kg = UNITS.kilogram
m = UNITS.meter
year = UNITS.year

# +
# And an inition condition (with everything in SI units)

# distance from the sun to the earth at perihelion
R = Vector(147e9, 0) * m

# initial velocity
V = Vector(0, -30300) * m/s

init = State(R=R, V=V)

# +
# Making a system object

r_earth = 6.371e6 * m
r_sun = 695.508e6 * m

t_end = (1 * year).to_base_units()

system = System(init=init,
                G=6.674e-11 * N / kg**2 * m**2,
                m1=1.989e30 * kg,
                r_final=r_sun + r_earth,
                m2=5.972e24 * kg,
                t_end=t_end)


# +
# Here's a function that computes the force of gravity

def universal_gravitation(state, system):
    """Computes gravitational force.
    
    state: State object with distance r
    system: System object with m1, m2, and G
    
    returns: Vector
    """
    R, V = state
    G, m1, m2 = system.G, system.m1, system.m2
        
    # make sure the result is a vector, either
    # by forcing it, or by putting v.hat() on
    # the left
    
    force = -G * m1 * m2 / R.mag2 * R.hat()
    return Vector(force)

    force = -R.hat() * G * m1 * m2 / R.mag2
    return force


# -

universal_gravitation(init, system)


# +
# The slope function

def slope_func(state, t, system):
    """Compute derivatives of the state.
    
    state: position, velocity
    t: time
    system: System object containing `g`
    
    returns: derivatives of y and v
    """
    R, V = state

    F = universal_gravitation(state, system)
    A = F / system.m2
    
    return V, A


# +
# Always test the slope function!

slope_func(init, 0, system)


# +
# Here's an event function that stops the simulation
# before the collision

def event_func(state, t, system):
    R, V = state
    return R.mag - system.r_final


# +
# Always test the event function!

event_func(init, 0, system)

# +
# Finally we can run the simulation

system.set(dt=system.t_end/1000)
results, details = run_euler(system, slope_func)
details


# -

def plot_trajectory(R):
    x = R.extract('x') / 1e9
    y = R.extract('y') / 1e9

    plot(x, y)
    plot(0, 0, 'yo')

    decorate(xlabel='x distance (million km)',
             ylabel='y distance (million km)')


plot_trajectory(results.R)

error = results.last_row() - system.init

error.R.mag

error.V.mag

# +
# Ralston

system.set(dt=system.t_end/1000)
results, details = run_ralston(system, slope_func)
details
# -

plot_trajectory(results.R)

error = results.last_row() - system.init

error.R.mag

error.V.mag

# +
xs = results.R.extract('x') * 1.1
ys = results.R.extract('y') * 1.1

def draw_func(state, t):
    set_xlim(xs)
    set_ylim(ys)
    x, y = state.R
    plot(x, y, 'b.')
    plot(0, 0, 'yo')
    decorate(xlabel='x distance (million km)',
             ylabel='y distance (million km)')


# -

system.set(dt=system.t_end/100)
results, details = run_ralston(system, slope_func)
animate(results, draw_func)


