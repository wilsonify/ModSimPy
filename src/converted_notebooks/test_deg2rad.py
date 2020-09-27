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

import numpy as np
from pint import UnitRegistry
ureg = UnitRegistry()
Q_ = ureg.Quantity

angle = 45
np.deg2rad(angle)

angle = 45 * ureg.degree
np.deg2rad(angle)

angle = 0.785 * ureg.radian
np.deg2rad(angle)

angle = 45 * ureg.dimensionless
np.deg2rad(angle)


