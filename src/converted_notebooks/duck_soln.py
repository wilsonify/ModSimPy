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

# ## The duck problem
#
#

g = UNITS.g
cm = UNITS.cm

system = System (
    density_duck = 0.3 * g/cm**3,
    density_water = 1  * g/cm**3,
    r = 5 * cm,
)


def error_func(d, system):
    # in order to work with root_scale, we have
    # to accept input that does not have units
    d = d * cm
    r = system.r
    
    volume_duck = 4 / 3 * pi * r**3
    mass_duck = volume_duck * system.density_duck

    volume_water = pi / 3 * (3 * r * d**2 - d**3)
    mass_water = volume_water * system.density_water

    # and return an error that does not have units
    error = mass_duck - mass_water
    return magnitude(error)


error_func(3, system)

error_func(4, system)

res = root_scalar(error_func, [3., 4.], system)

res.root * cm
