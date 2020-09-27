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
# Experiments with different ODE solvers
#
# Copyright 2019 Allen Downey
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

init = State(y = 2)
system = System(init=init, t_0=1, t_end=3)


def slope_func(state, t, system):
    [y] = state
    dydt = y + t
    return [dydt]


results, details = run_euler(system, slope_func)

get_last_value(results.y)

# ### Glucose minimal model
#
# Read the data.

data = pd.read_csv('data/glucose_insulin.csv', index_col='time');

# Interpolate the insulin data.

I = interpolate(data.insulin)

# Initialize the parameters

G0 = 290
k1 = 0.03
k2 = 0.02
k3 = 1e-05

# To estimate basal levels, we'll use the concentrations at `t=0`.

Gb = data.glucose[0]
Ib = data.insulin[0]

# Create the initial condtions.

init = State(G=G0, X=0)

# Make the `System` object.

t_0 = get_first_label(data)
t_end = get_last_label(data)

system = System(G0=G0, k1=k1, k2=k2, k3=k3,
                init=init, Gb=Gb, Ib=Ib, I=I,
                t_0=t_0, t_end=t_end, dt=2)


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


def run_simulation(system, update_func):
    """Runs a simulation of the system.
        
    system: System object
    update_func: function that updates state
    
    returns: TimeFrame
    """
    t_0, t_end, dt = system.t_0, system.t_end, system.dt
    
    frame = TimeFrame(columns=init.index)
    frame.row[t_0] = init
    ts = linrange(t_0, t_end, dt)
    
    for t in ts:
        frame.row[t+dt] = update_func(frame.row[t], t, system)
    
    return frame


# %time results = run_simulation(system, update_func);

results


# ### Numerical solution
#
# In the previous chapter, we approximated the differential equations with difference equations, and solved them using `run_simulation`.
#
# In this chapter, we solve the differential equation numerically using `run_euler`...
#
# Instead of an update function, we provide a slope function that evaluates the right-hand side of the differential equations.  We don't have to do the update part; the solver does it for us.

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

slope_func(init, 0, system)

# Here's how we run the ODE solver.

# +
system = System(G0=G0, k1=k1, k2=k2, k3=k3,
                init=init, Gb=Gb, Ib=Ib, I=I,
                t_0=t_0, t_end=t_end, dt=1)

# %time results2, details = run_euler(system, slope_func)
# -

# `results` is a `TimeFrame` with one row for each time step and one column for each state variable:

results2

# Plotting the results from `run_simulation` and `run_euler`, we can see that they are not very different.

plot(results.G, '-')
plot(results2.G, '-')
plot(data.glucose, 'bo')

# The differences in `G` are less than 1%.

# +
diff = results.G - results2.G
percent_diff = diff / results2.G * 100

max(abs(percent_diff.dropna()))
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

# When we call `odeint`, we need an array of timestamps where we want to compute the solution.
#
# I'll start with a duration of 10 seconds.

t_end = 10 * s

# Now we make a `System` object.

system = System(init=init, g=g, t_end=t_end)


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

# Now we're ready to call `run_euler`

system.set(dt=0.1*s)
results, details = run_euler(system, slope_func, max_step=0.5)
details.message

results


def crossings(series, value):
    """Find the labels where the series passes through value.

    The labels in series must be increasing numerical values.

    series: Series
    value: number

    returns: sequence of labels
    """
    units = get_units(series.values[0])
    values = magnitudes(series - value)
    interp = InterpolatedUnivariateSpline(series.index, values)
    return interp.roots()


t_crossings = crossings(results.y, 0)

system.set(dt=0.1*s)
results, details = run_ralston(system, slope_func, max_step=0.5)
details.message

t_crossings = crossings(results.y, 0)

# Here are the results:

results


# And here's position as a function of time:

# +
def plot_position(results):
    plot(results.y, label='y')
    decorate(xlabel='Time (s)',
             ylabel='Position (m)')

plot_position(results)
savefig('figs/chap09-fig01.pdf')


# -

# ### Onto the sidewalk
#
# To figure out when the penny hit the sidewalk, we can use `crossings`, which finds the times where a `Series` passes through a given value.

def crossings(series, value):
    """Find the labels where the series passes through value.

    The labels in series must be increasing numerical values.

    series: Series
    value: number

    returns: sequence of labels
    """
    units = get_units(series.values[0])
    values = magnitudes(series - value)
    interp = InterpolatedUnivariateSpline(series.index, values)
    return interp.roots()


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


# The estimate is accurate to about 10 decimal places.

# ## Events
#
# Instead of running the simulation until the penny goes through the sidewalk, it would be better to detect the point where the penny hits the sidewalk and stop.  `run_ralston` provides exactly the tool we need, **event functions**.
#
# Here's an event function that returns the height of the penny above the sidewalk:

def event_func(state, t, system):
    """Return the height of the penny above the sidewalk.
    """
    y, v = state
    return y


# And here's how we pass it to `run_ralston`.  The solver should run until the event function returns 0, and then terminate.

results, details = run_ralston(system, slope_func, events=event_func)
details

# The message from the solver indicates the solver stopped because the event we wanted to detect happened.
#
# Here are the results:

results

# With the `events` option, the solver returns the actual time steps it computed, which are not necessarily equally spaced. 
#
# The last time step is when the event occurred:

t_sidewalk = get_last_label(results) * s

# The result is accurate to about 15 decimal places.
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
