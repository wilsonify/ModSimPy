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
# Chapter 24
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

# ### Rolling paper
#
# We'll start by loading the units we need.

radian = UNITS.radian
m = UNITS.meter
s = UNITS.second

# And creating a `Params` object with the system parameters

params = Params(Rmin = 0.02 * m,
                Rmax = 0.055 * m,
                L = 47 * m,
                omega = 10 * radian / s,
                t_end = 130 * s,
                dt = 1*s)


# The following function estimates the parameter `k`, which is the increase in the radius of the roll for each radian of rotation. 

def estimate_k(params):
    """Estimates the parameter `k`.
    
    params: Params with Rmin, Rmax, and L
    
    returns: k in meters per radian
    """
    Rmin, Rmax, L = params.Rmin, params.Rmax, params.L
    
    Ravg = (Rmax + Rmin) / 2
    Cavg = 2 * pi * Ravg
    revs = L / Cavg
    rads = 2 * pi * revs
    k = (Rmax - Rmin) / rads
    return k


# As usual, `make_system` takes a `Params` object and returns a `System` object.

def make_system(params):
    """Make a system object.
    
    params: Params with Rmin, Rmax, and L
    
    returns: System with init, k, and ts
    """
    init = State(theta = 0 * radian,
                 y = 0 * m,
                 r = params.Rmin)
    
    k = estimate_k(params)

    return System(params, init=init, k=k)


# Testing `make_system`

system = make_system(params)

system.init


# Now we can write a slope function based on the differential equations
#
# $\omega = \frac{d\theta}{dt} = 10$
#
# $\frac{dy}{dt} = r \frac{d\theta}{dt}$
#
# $\frac{dr}{dt} = k \frac{d\theta}{dt}$
#

def slope_func(state, t, system):
    """Computes the derivatives of the state variables.
    
    state: State object with theta, y, r
    t: time
    system: System object with r, k
    
    returns: sequence of derivatives
    """
    theta, y, r = state
    k, omega = system.k, system.omega
    
    dydt = r * omega
    drdt = k * omega
    
    return omega, dydt, drdt


# Testing `slope_func`

slope_func(system.init, 0, system)


# We'll use an event function to stop when `y=L`.

def event_func(state, t, system):
    """Detects when we've rolled length `L`.
    
    state: State object with theta, y, r
    t: time
    system: System object with L
    
    returns: difference between `y` and `L`
    """
    theta, y, r = state
    
    return y - system.L


event_func(system.init, 0, system)

# Now we can run the simulation.

results, details = run_ode_solver(system, slope_func, events=event_func)
details

# And look at the results.

results.tail()

# The final value of `y` is 47 meters, as expected.

unrolled = get_last_value(results.y)

# The final value of radius is `R_max`.

radius = get_last_value(results.r)

# The total number of rotations is close to 200, which seems plausible.

radians = get_last_value(results.theta) 
rotations = magnitude(radians) / 2 / np.pi

# The elapsed time is about 2 minutes, which is also plausible.

t_final = get_last_label(results) * s


# ### Plotting

# Plotting `theta`

# +
def plot_theta(results):
    plot(results.theta, color='C0', label='theta')
    decorate(xlabel='Time (s)',
             ylabel='Angle (rad)')
    
plot_theta(results)


# -

# Plotting `y`

# +
def plot_y(results):
    plot(results.y, color='C1', label='y')

    decorate(xlabel='Time (s)',
             ylabel='Length (m)')
    
plot_y(results)


# -

# Plotting `r`

# +
def plot_r(results):
    plot(results.r, color='C2', label='r')

    decorate(xlabel='Time (s)',
             ylabel='Radius (m)')
    
plot_r(results)
# -

# We can also see the relationship between `y` and `r`, which I derive analytically in the book.

# +
plot(results.r, results.y, color='C3')

decorate(xlabel='Radius (m)',
         ylabel='Length (m)',
         legend=False)


# -

# And here's the figure from the book.

# +
def plot_three(results):
    subplot(3, 1, 1)
    plot_theta(results)

    subplot(3, 1, 2)
    plot_y(results)

    subplot(3, 1, 3)
    plot_r(results)

plot_three(results)
savefig('figs/chap24-fig01.pdf')
# -

# ### Animation
#
# Here's a draw function that animates the results using `matplotlib` patches.

# +
from matplotlib.patches import Circle
from matplotlib.patches import Arrow

def draw_func(state, t):
    # get radius in mm
    theta, y, r = state
    radius = r.magnitude * 1000
    
    # draw a circle with
    circle = Circle([0, 0], radius, fill=True)
    plt.gca().add_patch(circle)
    
    # draw an arrow to show rotation
    dx, dy = pol2cart(theta, radius)
    arrow = Arrow(0, 0, dx, dy)
    plt.gca().add_patch(arrow)

    # make the aspect ratio 1
    plt.axis('equal')


# -

animate(results, draw_func)

# **Exercise:** Run the simulation again with a smaller step size to smooth out the animation.

# ### Exercises
#
# **Exercise:** Since we keep `omega` constant, the linear velocity of the paper increases with radius.  Use `gradient` to estimate the derivative of `results.y`.  What is the peak linear velocity?

# +
# Solution

dydt = gradient(results.y);
# -

plot(dydt, label='dydt')
decorate(xlabel='Time (s)',
         ylabel='Linear velocity (m/s)')

# +
# Solution

linear_velocity = get_last_value(dydt) * m/s


# -

# Now suppose the peak velocity is the limit; that is, we can't move the paper any faster than that.
#
# Nevertheless, we might be able to speed up the process by keeping the linear velocity at the maximum all the time.
#
# Write a slope function that keeps the linear velocity, `dydt`, constant, and computes the angular velocity, `omega`, accordingly.
#
# Run the simulation and see how much faster we could finish rolling the paper.

# +
# Solution

def slope_func(state, t, system):
    """Computes the derivatives of the state variables.
    
    state: State object with theta, y, r
    t: time
    system: System object with r, k
    
    returns: sequence of derivatives
    """
    theta, y, r = state
    k, omega = system.k, system.omega
    
    dydt = linear_velocity
    omega = dydt / r
    drdt = k * omega
    
    return omega, dydt, drdt


# +
# Solution

slope_func(system.init, 0, system)

# +
# Solution

results, details = run_ode_solver(system, slope_func, events=event_func)
details

# +
# Solution

t_final = get_last_label(results) * s

# +
# Solution

plot_three(results)
# -


