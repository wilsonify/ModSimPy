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
# Case study
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

# ## Yo-yo
#
# Suppose you are holding a yo-yo with a length of string wound around its axle, and you drop it while holding the end of the string stationary.  As gravity accelerates the yo-yo downward, tension in the string exerts a force upward.  Since this force acts on a point offset from the center of mass, it exerts a torque that causes the yo-yo to spin.
#
# ![](diagrams/yoyo.png)
#
# This figure shows the forces on the yo-yo and the resulting torque.  The outer shaded area shows the body of the yo-yo.  The inner shaded area shows the rolled up string, the radius of which changes as the yo-yo unrolls.
#
# In this model, we can't figure out the linear and angular acceleration independently; we have to solve a system of equations:
#
# $\sum F = m a $
#
# $\sum \tau = I \alpha$
#
# where the summations indicate that we are adding up forces and torques.
#
# As in the previous examples, linear and angular velocity are related because of the way the string unrolls:
#
# $\frac{dy}{dt} = -r \frac{d \theta}{dt} $
#
# In this example, the linear and angular accelerations have opposite sign.  As the yo-yo rotates counter-clockwise, $\theta$ increases and $y$, which is the length of the rolled part of the string, decreases.
#
# Taking the derivative of both sides yields a similar relationship between linear and angular acceleration:
#
# $\frac{d^2 y}{dt^2} = -r \frac{d^2 \theta}{dt^2} $
#
# Which we can write more concisely:
#
# $ a = -r \alpha $
#
# This relationship is not a general law of nature; it is specific to scenarios like this where there is rolling without stretching or slipping.
#
# Because of the way we've set up the problem, $y$ actually has two meanings: it represents the length of the rolled string and the height of the yo-yo, which decreases as the yo-yo falls.  Similarly, $a$ represents acceleration in the length of the rolled string and the height of the yo-yo.
#
# We can compute the acceleration of the yo-yo by adding up the linear forces:
#
# $\sum F = T - mg = ma $
#
# Where $T$ is positive because the tension force points up, and $mg$ is negative because gravity points down.
#
# Because gravity acts on the center of mass, it creates no torque, so the only torque is due to tension:
#
# $\sum \tau = T r = I \alpha $
#
# Positive (upward) tension yields positive (counter-clockwise) angular acceleration.
#
# Now we have three equations in three unknowns, $T$, $a$, and $\alpha$, with $I$, $m$, $g$, and $r$ as known parameters.  It is simple enough to solve these equations by hand, but we can also get SymPy to do it for us.
#
#

# +
from sympy import init_printing, symbols, Eq, solve

init_printing()
# -

T, a, alpha, I, m, g, r = symbols('T a alpha I m g r')

eq1 = Eq(a, -r * alpha)

eq2 = Eq(T - m * g, m * a)

eq3 = Eq(T * r, I * alpha)

soln = solve([eq1, eq2, eq3], [T, a, alpha])

soln[T]

soln[a]

soln[alpha]

#
# The results are
#
# $T      = m g I / I^*   $
#
# $a      = -m g r^2 / I^* $
#
# $\alpha = m g r / I^*    $
#
# where $I^*$ is the augmented moment of inertia, $I + m r^2$.
#
# You can also see [the derivation of these equations in this video](https://www.youtube.com/watch?v=chC7xVDKl4Q).
#
# To simulate the system, we don't really need $T$; we can plug $a$ and $\alpha$ directly into the slope function.

radian = UNITS.radian
m = UNITS.meter
s = UNITS.second
kg = UNITS.kilogram
N = UNITS.newton

# **Exercise:**  Simulate the descent of a yo-yo.  How long does it take to reach the end of the string?
#
# I provide a `Params` object with the system parameters:
#
# * `Rmin` is the radius of the axle.  `Rmax` is the radius of the axle plus rolled string.
#
# * `Rout` is the radius of the yo-yo body.  `mass` is the total mass of the yo-yo, ignoring the string.  
#
# * `L` is the length of the string.
#
# * `g` is the acceleration of gravity.

params = Params(Rmin = 8e-3 * m,
                Rmax = 16e-3 * m,
                Rout = 35e-3 * m,
                mass = 50e-3 * kg,
                L = 1 * m,
                g = 9.8 * m / s**2,
                t_end = 1 * s)


# Here's a `make_system` function that computes `I` and `k` based on the system parameters.
#
# I estimated `I` by modeling the yo-yo as a solid cylinder with uniform density ([see here](https://en.wikipedia.org/wiki/List_of_moments_of_inertia)).
#
# In reality, the distribution of weight in a yo-yo is often designed to achieve desired effects.  But we'll keep it simple.

def make_system(params):
    """Make a system object.
    
    params: Params with Rmin, Rmax, Rout, 
                              mass, L, g, t_end
    
    returns: System with init, k, Rmin, Rmax, mass,
                         I, g, ts
    """
    L, mass = params.L, params.mass
    Rout, Rmax, Rmin = params.Rout, params.Rmax, params.Rmin 
    
    init = State(theta = 0 * radian,
                 omega = 0 * radian/s,
                 y = L,
                 v = 0 * m / s)
    
    I = mass * Rout**2 / 2
    k = (Rmax**2 - Rmin**2) / 2 / L / radian    
    
    return System(params, init=init, I=I, k=k)


# Testing `make_system`

system = make_system(params)

system.init


# Write a slope function for this system, using these results from the book:
#
# $ r = \sqrt{2 k y + R_{min}^2} $ 
#
# $ T      = m g I / I^*  $
#
# $ a      = -m g r^2 / I^* $
#
# $ \alpha  = m g r / I^*  $
#
# where $I^*$ is the augmented moment of inertia, $I + m r^2$.
#

# +
# Solution goes here
# -

# Test your slope function with the initial paramss.

# +
# Solution goes here
# -

# Write an event function that will stop the simulation when `y` is 0.

# +
# Solution goes here
# -

# Test your event function:

# +
# Solution goes here
# -

# Then run the simulation.

# +
# Solution goes here
# -

# Check the final state.  If things have gone according to plan, the final value of `y` should be close to 0.

# +
# Solution goes here
# -

# Plot the results.

# `theta` should increase and accelerate.

def plot_theta(results):
    plot(results.theta, color='C0', label='theta')
    decorate(xlabel='Time (s)',
             ylabel='Angle (rad)')
plot_theta(results)


# `y` should decrease and accelerate down.

# +
def plot_y(results):
    plot(results.y, color='C1', label='y')

    decorate(xlabel='Time (s)',
             ylabel='Length (m)')
    
plot_y(results)
# -

# Plot velocity as a function of time; is the yo-yo accelerating?

# +
# Solution goes here
# -

# Use `gradient` to estimate the derivative of `v`.  How does the acceleration of the yo-yo compare to `g`?

# +
# Solution goes here
# -


