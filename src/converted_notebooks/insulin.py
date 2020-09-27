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
# Insulin minimal model
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

# ### Data
#
# We have data from Pacini and Bergman (1986), "MINMOD: a computer program to calculate insulin sensitivity and pancreatic responsivity from the frequently sampled intravenous glucose tolerance test", *Computer Methods and Programs in Biomedicine*, 23: 113-122..

data = pd.read_csv('data/glucose_insulin.csv', index_col='time');

# ### The insulin minimal model
#
# In addition to the glucose minimal mode, Pacini and Bergman present an insulin minimal model, in which the concentration of insulin, $I$, is governed by this differential equation:
#
# $ \frac{dI}{dt} = -k I(t) + \gamma (G(t) - G_T) t $

# **Exercise:**  Write a version of `make_system` that takes the parameters of this model, `I0`, `k`, `gamma`, and `G_T` as parameters, along with a `DataFrame` containing the measurements, and returns a `System` object suitable for use with `run_simulation` or `run_odeint`.
#
# Use it to make a `System` object with the following parameters:

params = Params(I0 = 360,
                k = 0.25,
                gamma = 0.004,
                G_T = 80)

# +
# Solution goes here

# +
# Solution goes here
# -

# **Exercise:** Write a slope function that takes state, t, system as parameters and returns the derivative of `I` with respect to time.  Test your function with the initial condition $I(0)=360$.

# +
# Solution goes here

# +
# Solution goes here
# -

# **Exercise:** Run `run_ode_solver` with your `System` object and slope function, and plot the results, along with the measured insulin levels.

# +
# Solution goes here

# +
# Solution goes here

# +
# Solution goes here
# -

# **Exercise:**  Write an error function that takes a sequence of parameters as an argument, along with the `DataFrame` containing the measurements.  It should make a `System` object with the given parameters, run it, and compute the difference between the results of the simulation and the measured values.  Test your error function by calling it with the parameters from the previous exercise.
#
# Hint: As we did in a previous exercise, you might want to drop the errors for times prior to `t=8`.

# +
# Solution goes here

# +
# Solution goes here
# -

# **Exercise:** Use `leastsq` to find the parameters that best fit the data.  Make a `System` object with those parameters, run it, and plot the results along with the measurements.

# +
# Solution goes here

# +
# Solution goes here

# +
# Solution goes here

# +
# Solution goes here
# -

# **Exercise:** Using the best parameters, estimate the sensitivity to glucose of the first and second phase pancreatic responsivity:
#
# $ \phi_1 = \frac{I_{max} - I_b}{k (G_0 - G_b)} $
#
# $ \phi_2 = \gamma \times 10^4 $
#
# For $G_0$, use the best estimate from the glucose model, 290.  For $G_b$ and $I_b$, use the inital measurements from the data.
#

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


