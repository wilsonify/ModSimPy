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

import pint
UNITS = pint.UnitRegistry()
Quantity = UNITS.Quantity

import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
# -

plt.plot(1, 1, None)

meter = UNITS.meter
minute = UNITS.minute
newton = UNITS.newton

# And a few more parameters in the `Params` object.

max_torque = 240 * newton * meter

max_rpm = 5500 / minute


def available_torque(rpm):
    if rpm > max_rpm:
        return 0 * newton * meter
    return max_torque * (1 - rpm/max_rpm)


available_torque(0 / minute)

rpms = np.linspace(0, max_rpm*1.1, 21) / minute

taus = [available_torque(rpm) for rpm in rpms]

series = pd.Series(taus, index=rpms.magnitude)

plt.plot(series)
plt.xlabel('Motor speed (rad/s)')
plt.ylabel('Available torque (N m)')


