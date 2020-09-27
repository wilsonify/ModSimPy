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


results = run_simulation(system, update_func);


# ### Numerical solution
#
# In the previous chapter, we approximated the differential equations with difference equations, and solved them using `run_simulation`.
#
# In this chapter, we solve the differential equation numerically using `run_ode_solver`, which is a wrapper for the SciPy ODE solver.
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

results2, details = run_ode_solver(system, slope_func, t_eval=data.index);

# `details` is a `ModSimSeries` object with information about how the solver worked.

details

# `results` is a `TimeFrame` with one row for each time step and one column for each state variable:

results2

# Plotting the results from `run_simulation` and `run_ode_solver`, we can see that they are not very different.

plot(results.G, '-')
plot(results2.G, '-')
plot(data.glucose, 'bo')

# The differences in `G` are less than 1%.

diff = results.G - results2.G
percent_diff = diff / results2.G * 100
percent_diff.dropna()

# ### Optimization

# Now let's find the parameters that yield the best fit for the data.  

# We'll use these values as an initial estimate and iteratively improve them.

params = Params(G0 = 290,
                k1 = 0.03,
                k2 = 0.02,
                k3 = 1e-05)


# `make_system` takes the parameters and actual data and returns a `System` object.

def make_system(params, data):
    """Makes a System object with the given parameters.
    
    params: sequence of G0, k1, k2, k3
    data: DataFrame with `glucose` and `insulin`
    
    returns: System object
    """
    # params might be a Params object or an array,
    # so we have to unpack it like this
    G0, k1, k2, k3 = params
    
    Gb = data.glucose[0]
    Ib = data.insulin[0]
    I = interpolate(data.insulin)
    
    t_0 = get_first_label(data)
    t_end = get_last_label(data)

    init = State(G=G0, X=0)
    
    return System(G0=G0, k1=k1, k2=k2, k3=k3,
                  init=init, Gb=Gb, Ib=Ib, I=I,
                  t_0=t_0, t_end=t_end, dt=2)


system = make_system(params, data)

# `error_func` takes the parameters and actual data, makes a `System` object, and runs `odeint`, then compares the results to the data.  It returns an array of errors.

system = make_system(params, data)
results, details = run_ode_solver(system, slope_func, t_eval=data.index)
details


def error_func(params, data):
    """Computes an array of errors to be minimized.
    
    params: sequence of parameters
    data: DataFrame of values to be matched
    
    returns: array of errors
    """
    print(params)
    
    # make a System with the given parameters
    system = make_system(params, data)
    
    # solve the ODE
    results, details = run_ode_solver(system, slope_func, t_eval=data.index)
    
    # compute the difference between the model
    # results and actual data
    errors = results.G - data.glucose
    return errors


# When we call `error_func`, we provide a sequence of parameters as a single object.

# Here's how that works:

error_func(params, data)

# `leastsq` is a wrapper for `scipy.optimize.leastsq`

# Here's how we call it.

best_params, fit_details = leastsq(error_func, params, data)

# The first return value is a `Params` object with the best parameters:

best_params

# The second return value is a `ModSimSeries` object with information about the results.

fit_details

# Now that we have `best_params`, we can use it to make a `System` object and run it.

system = make_system(best_params, data)
results, details = run_ode_solver(system, slope_func, t_eval=data.index)
details.message

# Here are the results, along with the data.  The first few points of the model don't fit the data, but we don't expect them to.

# +
plot(results.G, label='simulation')
plot(data.glucose, 'bo', label='glucose data')

decorate(xlabel='Time (min)',
         ylabel='Concentration (mg/dL)')

savefig('figs/chap08-fig04.pdf')


# -

# ### Interpreting parameters
#
# Based on the parameters of the model, we can estimate glucose effectiveness and insulin sensitivity.

def indices(params):
    """Compute glucose effectiveness and insulin sensitivity.
    
    params: sequence of G0, k1, k2, k3
    data: DataFrame with `glucose` and `insulin`
    
    returns: State object containing S_G and S_I
    """
    G0, k1, k2, k3 = params
    return State(S_G=k1, S_I=k3/k2)


# Here are the results.

indices(best_params)

# ### Under the hood
#
# Here's the source code for `run_ode_solver` and `leastsq`, if you'd like to know how they work.

source_code(run_ode_solver)

source_code(leastsq)

# ## Exercises
#
# **Exercise:** Since we don't expect the first few points to agree, it's probably better not to make them part of the optimization process.  We can ignore them by leaving them out of the `Series` returned by `error_func`.  Modify the last line of `error_func` to return `errors.loc[8:]`, which includes only the elements of the `Series` from `t=8` and up.
#
# Does that improve the quality of the fit?  Does it change the best parameters by much?
#
# Note: You can read more about this use of `loc` [in the Pandas documentation](https://pandas.pydata.org/pandas-docs/stable/indexing.html#indexing-integer).

# **Exercise:** How sensitive are the results to the starting guess for the parameters?  If you try different values for the starting guess, do we get the same values for the best parameters?

# **Related reading:** You might be interested in this article about [people making a DIY artificial pancreas](https://www.bloomberg.com/news/features/2018-08-08/the-250-biohack-that-s-revolutionizing-life-with-diabetes).


