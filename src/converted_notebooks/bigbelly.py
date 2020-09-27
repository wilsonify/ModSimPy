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
# Copyright 2017 Allen Downey
#
# License: [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0)
#

# +
# Configure Jupyter so figures appear in the notebook
# %matplotlib inline

# Configure Jupyter to display the assigned value after an assignment
# %config InteractiveShell.ast_node_interactivity='last_expr_or_assign'

# import functions from the modsim library
from modsim import *
# -

# ## Bigbelly

# https://www.youtube.com/watch?v=frix_zTkPEs
#
# If the following import fails, open a terminal and run
#
# `conda install -c conda-forge pysolar`

from pysolar.solar import *

#

from datetime import datetime, timedelta

#

dt = datetime.now()

# +
from pytz import timezone

dt = pytz.timezone('EST').localize(dt)
# -

#

get_altitude(42.2931671, -71.263665, dt)

#

# +
latitude_deg = 42.3
longitude_deg = -71.3
altitude_deg = get_altitude(latitude_deg, longitude_deg, dt)
azimuth_deg = get_azimuth(latitude_deg, longitude_deg, dt)
radiation.get_radiation_direct(dt, altitude_deg)

# result is in Watts per square meter
# -

#

location = State(lat_deg=42.3, lon_deg=-71.3)

#

dt = datetime(year=2017, month=9, day=15, hour=12, minute=30)
dt = pytz.timezone('EST').localize(dt)


#

def compute_irradiance(location, dt):
    degree = UNITS.degree
    watt = UNITS.watt
    meter = UNITS.meter
    
    sun = State(
        altitude_deg = get_altitude(location.lat_deg, location.lon_deg, dt),
        azimuth_deg = get_azimuth(location.lat_deg, location.lon_deg, dt)
    )

    if sun.altitude_deg <= 0:
        irradiance = 0
    else:
        irradiance = radiation.get_radiation_direct(dt, sun.altitude_deg)

    sun.set(irradiance = irradiance * watt / meter**2)
    return sun


#

sun = compute_irradiance(location, dt)

#

# +
dt = datetime(year=2017, month=9, day=15)
dt = pytz.timezone('EST').localize(dt)

delta_t = timedelta(minutes=15)

result = TimeSeries()
for i in range(24 * 4):
    dt += delta_t
    sun = compute_irradiance(location, dt)
    result[dt] = sun.irradiance.magnitude

result
# -

#

result.plot()

cm = UNITS.centimeter
meter = UNITS.meter
watt = UNITS.watt
second = UNITS.second
joule = UNITS.joule

#

width = 45 * cm

#

area = width**2

#

power = sun.irradiance * area

#

area = area.to(meter**2)

#

power = sun.irradiance * area

#

delta_t = 1 * second
energy = power * delta_t

#

energy.to(joule)

#


















