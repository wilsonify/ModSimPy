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
# Chapter 21
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

# ### With air resistance

# Next we'll add air resistance using the [drag equation](https://en.wikipedia.org/wiki/Drag_equation)

# I'll start by getting the units we'll need from Pint.

m = UNITS.meter
s = UNITS.second
kg = UNITS.kilogram

# Now I'll create a `Params` object to contain the quantities we need.  Using a Params object is convenient for grouping the system parameters in a way that's easy to read (and double-check).

params = Params(height = 381 * m,
                v_init = 0 * m / s,
                g = 9.8 * m/s**2,
                mass = 2.5e-3 * kg,
                diameter = 19e-3 * m,
                rho = 1.2 * kg/m**3,
                v_term = 18 * m / s)


# Now we can pass the `Params` object `make_system` which computes some additional parameters and defines `init`.
#
# `make_system` uses the given radius to compute `area` and the given `v_term` to compute the drag coefficient `C_d`.

def make_system(params):
    """Makes a System object for the given conditions.
    
    params: Params object
    
    returns: System object
    """
    diameter, mass = params.diameter, params.mass
    g, rho = params.g, params.rho, 
    v_init, v_term = params.v_init, params.v_term
    height = params.height
    
    area = np.pi * (diameter/2)**2
    C_d = 2 * mass * g / (rho * area * v_term**2)
    init = State(y=height, v=v_init)
    t_end = 30 * s
    dt = t_end / 100
    
    return System(params, area=area, C_d=C_d, 
                  init=init, t_end=t_end, dt=dt)


# Let's make a `System`

system = make_system(params)


# Here's the slope function, including acceleration due to gravity and drag.

def slope_func(state, t, system):
    """Compute derivatives of the state.
    
    state: position, velocity
    t: time
    system: System object
    
    returns: derivatives of y and v
    """
    y, v = state
    rho, C_d, g = system.rho, system.C_d, system.g
    area, mass = system.area, system.mass
    
    f_drag = rho * v**2 * C_d * area / 2
    a_drag = f_drag / mass
    
    dydt = v
    dvdt = -g + a_drag
    
    return dydt, dvdt


# As always, let's test the slope function with the initial conditions.

slope_func(system.init, 0, system)


# We can use the same event function as in the previous chapter.

def event_func(state, t, system):
    """Return the height of the penny above the sidewalk.
    """
    y, v = state
    return y


# And then run the simulation.

results, details = run_ode_solver(system, slope_func, events=event_func)
details

# Here are the results.

results.head()

results.tail()

# The final height is close to 0, as expected.
#
# Interestingly, the final velocity is not exactly terminal velocity, which suggests that there are some numerical errors.
#
# We can get the flight time from `results`.

t_sidewalk = get_last_label(results) * s


# Here's the plot of position as a function of time.

# +
def plot_position(results):
    plot(results.y)
    decorate(xlabel='Time (s)',
             ylabel='Position (m)')
    
plot_position(results)
savefig('figs/chap21-fig01.pdf')


# -

# And velocity as a function of time:

# +
def plot_velocity(results):
    plot(results.v, color='C1', label='v')
        
    decorate(xlabel='Time (s)',
             ylabel='Velocity (m/s)')
    
plot_velocity(results)
# -

# From an initial velocity of 0, the penny accelerates downward until it reaches terminal velocity; after that, velocity is constant.

# **Exercise:** Run the simulation with an initial velocity, downward, that exceeds the penny's terminal velocity.  Hint: You can create a new `Params` object based on an existing one, like this:
#
# `params2 = Params(params, v_init=-30 * m/s)`
#
# What do you expect to happen?  Plot velocity and position as a function of time, and see if they are consistent with your prediction.

# +
# Solution

v_init = -30 * m / s
params2 = Params(params, v_init=v_init)

# +
# Solution

system2 = make_system(params2)
results, details = run_ode_solver(system2, slope_func, events=event_func, max_step=0.5)
details.message
# -

plot_position(results)

# +
# Solution

plot_velocity(results)
# -

# **Exercise:** Suppose we drop a quarter from the Empire State Building and find that its flight time is 19.1 seconds.  Use this measurement to estimate the terminal velocity.
#
# 1. You can get the relevant dimensions of a quarter from https://en.wikipedia.org/wiki/Quarter_(United_States_coin).
#
# 2. Create a `Params` object with the system parameters.  We don't know `v_term`, so we'll start with the inital guess `v_term = 18 * m / s`.
#
# 3. Use `make_system` to create a `System` object.
#
# 4. Call `run_ode_solver` to simulate the system.  How does the flight time of the simulation compare to the measurement?
#
# 5. Try a few different values of `t_term` and see if you can get the simulated flight time close to 19.1 seconds.
#
# 6. Optionally, write an error function and use `root_scalar` to improve your estimate.
#
# 7. Use your best estimate of `v_term` to compute `C_d`.
#
# Note: I fabricated the observed flight time, so don't take the results of this exercise too seriously.

# +
# Solution

# Here's a `Params` object with the dimensions of a quarter,
# the observed flight time and our initial guess for `v_term`

params3 = Params(params,
                 mass = 5.67e-3 * kg,
                 diameter = 24.26e-3 * m,
                 v_term = 18 * m / s,
                 flight_time = 19.1 * s)

# +
# Solution

# Now we can make a `System` object

system3 = make_system(params3)

# +
# Solution

# Run the simulation

results, details = run_ode_solver(system3, slope_func, events=event_func)
details

# +
# Solution

# And get the flight time

flight_time = get_last_label(results) * s


# +
# Solution

# The flight time is a little long, so we could increase `v_term` and try again.

# Or we could write an error function

def error_func(guess, params):
    """Final height as a function of C_d.
    
    guess: guess at v_term
    params: Params object
    
    returns: height in m
    """
    print(guess)
    params = Params(params, v_term=guess)
    system = make_system(params)
    results, details = run_ode_solver(system, slope_func, events=event_func)
    flight_time = get_last_label(results) * s
    error = flight_time - params.flight_time
    return magnitude(error)


# +
# Solution

# We can test the error function like this
v_guess1 = 18 * m / s
error_func(v_guess1, params3)

# +
# Solution

v_guess2 = 22 * m / s
error_func(v_guess2, params3)

# +
# Solution

# Now we can use `root_scalar` to find the value of `v_term` that yields the measured flight time.

res = root_bisect(error_func, [v_guess1, v_guess2], params3)

# +
# Solution

v_term_solution = res.root

# +
# Solution

# Plugging in the estimated value, we can use `make_system` to compute `C_d`

params_solution = Params(params3, v_term=v_term_solution)
system = make_system(params_solution)
system.C_d
# -


