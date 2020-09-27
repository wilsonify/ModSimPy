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
# Chapter 25
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

# ### Teapots and Turntables

# Tables in Chinese restaurants often have a rotating tray or turntable that makes it easy for customers to share dishes.  These turntables are supported by low-friction bearings that allow them to turn easily and glide.  However, they can be heavy, especially when they are loaded with food, so they have a high moment of inertia.
#
# Suppose I am sitting at a table with a pot of tea on the turntable directly in front of me, and the person sitting directly opposite asks me to pass the tea.  I push on the edge of the turntable with 1 Newton of force until it has turned 0.5 radians, then let go.  The turntable glides until it comes to a stop 1.5 radians from the starting position.  How much force should I apply for a second push so the teapot glides to a stop directly opposite me?
#
# The following figure shows the scenario, where `F` is the force I apply to the turntable at the perimeter, perpendicular to the moment arm, `r`, and `tau` is the resulting torque.  The blue circle near the bottom is the teapot.
#
# ![](diagrams/teapot.png)
#
# We'll answer this question in these steps:
#
# 1.  We'll use the results from the first push to estimate the coefficient of friction for the turntable.
#
# 2.  We'll use that coefficient of friction to estimate the force needed to rotate the turntable through the remaining angle.
#
# Our simulation will use the following parameters:
#
# 1.  The radius of the turntable is 0.5 meters, and its weight is 7 kg.
#
# 2.  The teapot weights 0.3 kg, and it sits 0.4 meters from the center of the turntable.
#
# As usual, I'll get units from Pint.

radian = UNITS.radian
m = UNITS.meter
s = UNITS.second
kg = UNITS.kilogram
N = UNITS.newton

# And store the parameters in a `Params` object.

params = Params(radius_disk=0.5*m,
                mass_disk=7*kg,
                radius_pot=0.4*m,
                mass_pot=0.3*kg,
                force=1*N,
                torque_friction=0.2*N*m,
                theta_end=0.5*radian,
                t_end=20*s)


# `make_system` creates the initial state, `init`, and computes the total moment of inertia for the turntable and the teapot.

def make_system(params):
    """Make a system object.
    
    params: Params object
    
    returns: System object
    """
    mass_disk, mass_pot = params.mass_disk, params.mass_pot
    radius_disk, radius_pot = params.radius_disk, params.radius_pot
    
    init = State(theta=0*radian, omega=0*radian/s)
    
    I_disk = mass_disk * radius_disk**2 / 2
    I_pot = mass_pot * radius_pot**2
    
    return System(params, init=init, I=I_disk+I_pot)


# Here's the `System` object we'll use for the first phase of the simulation, while I am pushing the turntable.

system1 = make_system(params)


# ### Simulation
#
# When I stop pushing on the turntable, the angular acceleration changes abruptly.  We could implement the slope function with an `if` statement that checks the value of `theta` and sets `force` accordingly.  And for a coarse model like this one, that might be fine.  But we will get more accurate results if we simulate the system in two phases:
#
# 1.  During the first phase, force is constant, and we run until `theta` is 0.5 radians.
#
# 2.  During the second phase, force is 0, and we run until `omega` is 0.
#
# Then we can combine the results of the two phases into a single `TimeFrame`.
#
# Here's the slope function we'll use:

def slope_func(state, t, system):
    """Computes the derivatives of the state variables.
    
    state: State object
    t: time
    system: System object 
    
    returns: sequence of derivatives
    """
    theta, omega = state
    radius_disk, force = system.radius_disk, system.force
    torque_friction, I = system.torque_friction, system.I
    
    torque = radius_disk * force - torque_friction
    alpha = torque / I
    
    return omega, alpha 


# As always, we'll test the slope function before running the simulation.

slope_func(system1.init, 0, system1)


# Here's an event function that stops the simulation when `theta` reaches `theta_end`.

def event_func1(state, t, system):
    """Stops when theta reaches theta_end.
    
    state: State object
    t: time
    system: System object 
    
    returns: difference from target
    """
    theta, omega = state
    return theta - system.theta_end 


event_func1(system1.init, 0, system1)

# Now we can run the first phase.

results1, details1 = run_ode_solver(system1, slope_func, events=event_func1)
details1

# And look at the results.

results1.tail()

# ### Phase 2
#
# Before we run the second phase, we have to extract the final time and state of the first phase.

t_0 = results1.last_label() * s

# And make an initial `State` object for Phase 2.

init2 = results1.last_row()

# And a new `System` object with zero force.

system2 = System(system1, t_0=t_0, init=init2, force=0*N)


# Here's an event function that stops when angular velocity is 0.

def event_func2(state, t, system):
    """Stops when omega is 0.
    
    state: State object
    t: time
    system: System object 
    
    returns: omega
    """
    theta, omega = state
    return omega


event_func2(system2.init, 0, system2)

# Now we can run the second phase.

slope_func(system2.init, system2.t_0, system2)

results2, details2 = run_ode_solver(system2, slope_func, events=event_func2)
details2

# And check the results.

results2.tail()

# Pandas provides `combine_first`, which combines `results1` and `results2`.

results = results1.combine_first(results2)
results.tail()


# Now we can plot `theta` for both phases.

# +
def plot_theta(results):
    plot(results.theta, label='theta')
    decorate(xlabel='Time (s)',
             ylabel='Angle (rad)')
    
plot_theta(results)


# -

# And `omega`.

# +
def plot_omega(results):
    plot(results.omega, label='omega', color='C1')
    decorate(xlabel='Time (s)',
             ylabel='Angular velocity (rad/s)')
    
plot_omega(results)
# -

subplot(2, 1, 1)
plot_theta(results)
subplot(2, 1, 2)
plot_omega(results)
savefig('figs/chap25-fig01.pdf')


# ### Estimating friction
#
# Let's take the code from the previous section and wrap it in a function.

def run_two_phases(force, torque_friction, params):
    """Run both phases.
    
    force: force applied to the turntable
    torque_friction: friction due to torque
    params: Params object
    
    returns: TimeFrame of simulation results
    """
    # put the specified parameters into the Params object
    params = Params(params, force=force, torque_friction=torque_friction)

    # run phase 1
    system1 = make_system(params)
    results1, details1 = run_ode_solver(system1, slope_func, 
                                          events=event_func1)

    # get the final state from phase 1
    t_0 = results1.last_label() * s
    init2 = results1.last_row()
    
    # run phase 2
    system2 = System(system1, t_0=t_0, init=init2, force=0*N)
    results2, details2 = run_ode_solver(system2, slope_func, 
                                        events=event_func2)
    
    # combine and return the results
    results = results1.combine_first(results2)
    return TimeFrame(results)


# Let's test it with the same parameters.

force = 1*N
torque_friction = 0.2*N*m
results = run_two_phases(force, torque_friction, params)
results.tail()

# And check the results.

theta_final = results.last_row().theta


# Here's the error function we'll use with `root_bisect`.
#
# It takes a hypothetical value for `torque_friction` and returns the difference between `theta_final` and the observed duration of the first push, 1.5 radian.

def error_func1(torque_friction, params):
    """Error function for root_scalar.
    
    torque_friction: hypothetical value
    params: Params object
    
    returns: offset from target value
    """
    force = 1 * N
    results = run_two_phases(force, torque_friction, params)
    theta_final = results.last_row().theta
    print(torque_friction, theta_final)
    return theta_final - 1.5 * radian


# Testing the error function.

guess1 = 0.1*N*m
error_func1(guess1, params)

guess2 = 0.3*N*m
error_func1(guess2, params)

# And running `root_scalar`.

res = root_bisect(error_func1, [guess1, guess2], params)

# The result is the coefficient of friction that yields a total rotation of 1.5 radian.

torque_friction = res.root

# Here's a test run with the estimated value.

force = 1 * N
results = run_two_phases(force, torque_friction, params)
theta_final = get_last_value(results.theta)

# Looks good.

# ### Animation
#
#
# Here's a draw function we can use to animate the results.

# +
from matplotlib.patches import Circle
from matplotlib.patches import Arrow

def draw_func(state, t):
    theta, omega = state
    
    # draw a circle for the table
    radius_disk = magnitude(params.radius_disk)
    circle1 = Circle([0, 0], radius_disk)
    plt.gca().add_patch(circle1)
    
    # draw a circle for the teapot
    radius_pot = magnitude(params.radius_pot)
    center = pol2cart(theta, radius_pot)
    circle2 = Circle(center, 0.05, color='C1')
    plt.gca().add_patch(circle2)

    # make the aspect ratio 1
    plt.axis('equal')


# -

state = results.first_row()
draw_func(state, 0)

animate(results, draw_func)


#
# ### Exercises
#
# Now finish off the example by estimating the force that delivers the teapot to the desired position.
#
# Write an error function that takes `force` and `params` and returns the offset from the desired angle.

# +
# Solution

def error_func2(force, params):
    """Error function for root_scalar.
    
    force: hypothetical value
    params: Params object
    
    returns: offset from target value
    """
    # notice that this function uses the global value of torque_friction
    results = run_two_phases(force, torque_friction, params)
    theta_final = get_last_value(results.theta)
    print(force, theta_final)
    remaining_angle = np.pi - 1.5
    return theta_final - remaining_angle * radian


# -

# Test the error function with `force=1`

# +
# Solution

guess1 = 0.5 * N
error_func2(guess1, params)

# +
# Solution

guess2 = 2 * N
error_func2(guess2, params)
# -

# And run `root_bisect` to find the desired force.

# +
# Solution

res = root_bisect(error_func2, [guess1, guess2], params)
# -

force = res.root
results = run_two_phases(force, torque_friction, params)
theta_final = get_last_value(results.theta)

remaining_angle = np.pi - 1.5

# **Exercise:** Now suppose my friend pours 0.1 kg of tea and puts the teapot back on the turntable at distance 0.3 meters from the center.  If I ask for the tea back, how much force should they apply, over an arc of 0.5 radians, to make the teapot glide to a stop back in front of me?  You can assume that torque due to friction is proportional to the total mass of the teapot and the turntable.

# +
# Solution

mass_before = params.mass_pot + params.mass_disk

# +
# Solution

params2 = Params(params, mass_pot=0.2*kg, radius_pot=0.3*m)

# +
# Solution

mass_after = params2.mass_pot + params2.mass_disk

# +
# Solution

torque_friction

# +
# Solution

torque_friction2 = torque_friction * mass_after / mass_before

# +
# Solution

guess = 2 * N
results = run_two_phases(guess, torque_friction2, params2)
results.tail()

# +
# Solution

subplot(2, 1, 1)
plot_theta(results)
subplot(2, 1, 2)
plot_omega(results)


# +
# Solution

# Note: this is so similar to error_func2, it would be better
# to generalize it, but for expediency, I will make a modified
# verison.

def error_func3(force, params):
    """Error function for root_scalar.
    
    force: hypothetical value
    params: Params object
    
    returns: offset from target value
    """
    # notice that this function uses the global value of torque_friction2
    results = run_two_phases(force, torque_friction2, params)
    theta_final = get_last_value(results.theta)
    print(force, theta_final)
    remaining_angle = np.pi * radian
    return theta_final - remaining_angle


# +
# Solution

guess1 = 1 * N
error_func3(guess1, params)

# +
# Solution

guess2 = 3 * N
error_func3(guess2, params)

# +
# Solution

res = root_bisect(error_func3, [guess1, guess2], params2)

# +
# Solution

error_func3(res.root, params)
