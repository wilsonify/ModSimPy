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
#
# Copyright 2018 Allen Downey
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

# ## Inferring thermal resistance and thermal mass of a wall
#
# This case study is based on Gori, Marincioni, Biddulph, Elwell, "Inferring the thermal resistance and effective thermal mass distribution of a wall from in situ measurements to characterise heat transfer at both the interior and exterior surfaces", *Energy and Buildings*, Volume 135, 15 January 2017, Pages 398-409, [which I downloaded here](https://www.sciencedirect.com/science/article/pii/S0378778816313056).
#     
# The authors put their paper under a Creative Commons license, and [make their data available here](http://discovery.ucl.ac.uk/1526521).  I thank them for their commitment to open, reproducible science, which made this case study possible.
#
# The goal of their paper is to model the thermal behavior of a wall as a step toward understanding the "performance gap between the expected energy use of buildings and their measured energy use".  The wall they study is identified as the exterior wall of an office building in central London, [not unlike this one](https://www.google.com/maps/@51.5269375,-0.1303666,3a,75y,90h,88.17t/data=!3m6!1e1!3m4!1sAoAXzN0mbGF9acaVEgUdDA!2e0!7i13312!8i6656).
#
# The following figure shows the scenario and their model:
#
# ![Figure 2](https://ars.els-cdn.com/content/image/1-s2.0-S0378778816313056-gr2.jpg)
#
# On the interior and exterior surfaces of the wall, they measure temperature and heat flux over a period of three days.  They model the wall using two thermal masses connected to the surfaces, and to each other, by thermal resistors.
#
# The primary methodology of the paper is a Bayesian method for inferring the parameters of the system (two thermal masses and three thermal resistances).
#
# The primary result is a comparison of two models: the one shown here with two thermal masses, and a simpler model with only one thermal mass.  They find that the two-mass model is able to reproduce the measured fluxes substantially better.
#
# Tempting as it is, I will not replicate their method for estimating the parameters.  Rather, I will
#
# 1. Implement their model and run it with their estimated parameters, to replicate the results, and 
#
# 2. Use SciPy's `leastsq` to see if I can find parameters that yield lower errors (root mean square).
#
# `leastsq` is a wrapper for some venerable FORTRAN code that runs ["a modification of the Levenberg-Marquardt algorithm"](https://www.math.utah.edu/software/minpack/minpack/lmdif.html), which is one of my favorites ([really](http://allendowney.com/research/model)).
#
# Implementing their model in the ModSimPy framework turns out to be straightforward.  The simulations run fast enough even when we carry units through the computation.  And the results are visually similar to the ones in the original paper.
#
# I find that `leastsq` is not able to find parameters that yield substantially better results, which suggest that the estimates in the paper are at least locally optimal.
#

# ### Loading the data
#
# First I'll load the units we need from Pint.

m = UNITS.meter
K = UNITS.kelvin
W = UNITS.watt
J = UNITS.joule
degC = UNITS.celsius
s = UNITS.second

# Read the data.

data = pd.read_csv('data/DataOWall.csv', parse_dates=[0], index_col=0, header=0, skiprows=[1,2])
data.head()

# The index contains Pandas `Timestamp` objects, which is good for dealing with real-world dates and times, but not as good for running the simulations, so I'm going to convert to seconds.

timestamp_0 = get_first_label(data)

# Subtracting the first `Timestamp` yields `Timedelta` objects:

time_deltas = data.index - timestamp_0

# Then we can convert to seconds and replace the index.

data.index = time_deltas.days * 86400 + time_deltas.seconds
data.head()

# The timesteps are all 5 minutes:

np.all(np.diff(data.index) == 300)

# Mark the columns of the `Dataframe` with units.

data.Q_in.units = W / m**2
data.Q_out.units = W / m**2
data.T_int.units = degC
data.T_ext.units = degC

# Plot the measured fluxes.

plot(data.Q_in, color='C2')
plot(data.Q_out, color='C0')
decorate(xlabel='Time (s)',
         ylabel='Heat flux (W/$m^2$)')

# Plot the measured temperatures.

plot(data.T_int, color='C2')
plot(data.T_ext, color='C0')
decorate(xlabel='Time (s)',
         ylabel='Temperature (degC)')

# ### Params and System objects
#
# Here's a `Params` object with the [estimated parameters from the paper](https://www.sciencedirect.com/science/article/pii/S0378778816313056#tbl0005).

params = Params(
    R1 = 0.076 * m**2 * K / W,
    R2 = 0.272 * m**2 * K / W,
    R3 = 0.078 * m**2 * K / W,
    C1 = 212900 * J / m**2 / K,
    C2 = 113100 * J / m**2 / K)


# I'll pass the `Params` object `make_system`, which computes `init`, packs the parameters into `Series` objects, and computes the interpolation functions.

def make_system(params, data):
    """Makes a System object for the given conditions.
    
    params: Params object
    
    returns: System object
    """
    R1, R2, R3, C1, C2 = params
    
    init = State(T_C1 = Quantity(16.11, degC),
                 T_C2 = Quantity(15.27, degC))
    
    ts = data.index
    t_end = ts[-1] * s
    
    return System(init=init,
                  R=Series([R1, R2, R3]),
                  C=Series([C1, C2]),
                  T_int_func=interpolate(data.T_int),
                  T_ext_func=interpolate(data.T_ext),
                  unit_temp=degC,
                  t_end=t_end, ts=ts)


# Make a `System` object

system = make_system(params, data)

# Test the interpolation function:

system.T_ext_func(0), system.T_ext_func(150), system.T_ext_func(300)


# ### Implementing the model
#
# Next we need a slope function that takes instantaneous values of the two internal temperatures and computes their time rates of change.
#
# The slope function gets called two ways.
#
# * When we call it directly, `state` is a `State` object and the values it contains have units.
#
# * When `run_ode_solver` calls it, `state` is an array and the values it contains don't have units.
#
# In the second case, we have to apply the units before attempting the computation.  `require_units` applies units if necessary:

# The following function computes the fluxes between the four zones.

def compute_flux(state, t, system):
    """Compute the fluxes between the walls surfaces and the internal masses.
    
    state: State with T_C1 and T_C2
    t: time in seconds
    system: System with interpolated measurements and the R Series
    
    returns: Series of fluxes
    """    
    # unpack the temperatures
    T_C1, T_C2 = state
        
    # compute a series of temperatures from inside out
    T_int = system.T_int_func(t)
    T_ext = system.T_ext_func(t)
    
    T = [require_units(T_int, system.unit_temp),
         require_units(T_C1, system.unit_temp),
         require_units(T_C2, system.unit_temp),
         require_units(T_ext, system.unit_temp)]
    
    # compute differences of adjacent temperatures
    T_diff = np.diff(T)

    # compute fluxes between adjacent compartments
    Q = T_diff / system.R
    return Q


# We can test it like this.

compute_flux(system.init, 0, system)


# Here's a slope function that computes derivatives of `T_C1` and `T_C2`

def slope_func(state, t, system):
    """Compute derivatives of the state.
    
    state: position, velocity
    t: time
    system: System object
    
    returns: derivatives of y and v
    """
    Q = compute_flux(state, t, system)

    # compute the net flux in each node
    Q_diff = np.diff(Q)
        
    # compute the rate of change of temperature
    dQdt = Q_diff / system.C
    return dQdt


# Test the slope function with the initial conditions.

slopes = slope_func(system.init, system.ts[1], system)

for y, slope in zip(system.init, slopes):
    print(y, slope*s)

# Now let's run the simulation, generating estimates for the time steps in the data.

results, details = run_ode_solver(system, slope_func)
details

# Here's what the results look like.

results.head()


# +
def plot_results(results, data):
    plot(data.T_int, color='C2')
    plot(results.T_C1, color='C3')
    plot(results.T_C2, color='C1')
    plot(data.T_ext, color='C0')
    decorate(xlabel='Time (s)',
             ylabel='Temperature (degC)')
    
plot_results(results, data)


# -

# These results are similar to what's in the paper:
#
# ![Figure 5](https://ars.els-cdn.com/content/image/1-s2.0-S0378778816313056-gr5.jpg).  
#
# To get the estimated fluxes, we have to go through the results and basically do the flux calculation again.

# +
def recompute_fluxes(results, system):
    """Compute fluxes between wall surfaces and internal masses.
    
    results: Timeframe with T_C1 and T_C2
    system: System object
    
    returns: Timeframe with Q_in and Q_out
    """
    Q_frame = TimeFrame(index=results.index, columns=['Q_in', 'Q_out'])
    
    for t, row in results.iterrows():
        Q = compute_flux(row, t, system)
        
        Q_frame.row[t] = (-Q[0].magnitude, 
                          -Q[2].magnitude)
        
    return Q_frame
            
Q_frame = recompute_fluxes(results, system)
Q_frame.head()


# -

# Let's see how the estimates compare to the data.

# +
def plot_Q_in(frame, data):
    plot(frame.Q_in, color='gray')
    plot(data.Q_in, color='C2')
    decorate(xlabel='Time (s)',
             ylabel='Heat flux (W/$m^2$)')
    
plot_Q_in(Q_frame, data)


# +
def plot_Q_out(frame, data):
    plot(frame.Q_out, color='gray')
    plot(data.Q_out, color='C0')
    decorate(xlabel='Time (s)',
             ylabel='Heat flux (W/$m^2$)')
    
plot_Q_out(Q_frame, data)


# -

# These results are also similar to what's in the paper (the bottom row):
#
# ![Figure 3](https://ars.els-cdn.com/content/image/1-s2.0-S0378778816313056-gr3.jpg)
#
#

def compute_error(frame, data):
    model_Q_in = interpolate(Q_frame.Q_in)(data.index)
    error_Q_in = model_Q_in - data.Q_in
    
    model_Q_out = interpolate(Q_frame.Q_out)(data.index)
    error_Q_out = model_Q_out - data.Q_out
    
    return np.hstack([error_Q_in, error_Q_out])


errors = compute_error(Q_frame, data)

# Here's the root mean squared error.

print(np.sqrt(np.mean(errors**2)))

# ### Estimating parameters

# Now let's see if we can do any better than the parameters in the paper.
#
# In order to work with `leastsq`, we need a version of `params` with no units.

params = [0.076, 0.272, 0.078, 212900, 113100]


# Here's an error function that takes a hypothetical set of parameters, runs the simulation, and returns an array of errors.

def error_func(params, data):
    """Run a simulation and return an array of errors.
    
    params: Params object or array
    data: DataFrame
    
    returns: array of float
    """
    print(params)
    system = make_system(params, data)
    system = remove_units(system)
    
    results, details = run_ode_solver(system, slope_func)
    Q_frame = recompute_fluxes(results, system)
    errors = compute_error(Q_frame, data)
    print('RMSE', np.sqrt(np.mean(errors**2)))
    return errors


# Testing `error_func`.

errors = error_func(params, data)

# Pass `error_func` to `leastsq` to see if it can do any better.

best_params, details = leastsq(error_func, params, data)

details

details.mesg

# The best params are only slightly different from the starting place. 

best_params

# Here's what the results look like with the `best_params`.

# +
system = make_system(best_params, data)
system = remove_units(system)

results, details = run_ode_solver(system, slope_func, t_eval=system.ts)
Q_frame = recompute_fluxes(results, system)
errors = compute_error(Q_frame, data)
print(np.sqrt(np.mean(errors**2)))
# -

# The RMS error is only slightly smaller.
#
# And the results are visually similar.

plot_Q_in(Q_frame, data)

plot_Q_out(Q_frame, data)

# **Exercise:** Try starting the model with a different set of parameters and see if it moves toward the parameters in the paper.
#
# I found that no matter where I start, `leastsq` doesn't move far, which suggests that it is not able to optimize the parameters effectively.

# ### Notes
#
# Notes on working with degC.
#
# Usually I construct a `Quantity` object by multiplying a number and a unit.  With degC, that doesn't work; you get
#
# ```
# OffsetUnitCalculusError: Ambiguous operation with offset unit (degC).
# ```

# +
#16.11 * C 
# -

# The problem is that it doesn't know whether you want a temperature measurement or a temperature difference.
#
# You can create a temperature measurement like this.

T = Quantity(16.11, degC)

# If you convert to Kelvin, it does the right thing.

T.to(K)

# When you subtract temperatures, the results is a temperature difference, indicated by the units.

diff = T - 273.15 * K

# If you convert a temperature difference to Kelvin, it does the right thing.

diff.to(K)


