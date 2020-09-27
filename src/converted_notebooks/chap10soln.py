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
# Chapter 10
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

from pandas import read_html
# -

# ### Under the hood
#
# To get a `DataFrame` and a `Series`, I'll read the world population data and select a column.
#
# `DataFrame` and `Series` contain a variable called `shape` that indicates the number of rows and columns.

filename = 'data/World_population_estimates.html'
tables = read_html(filename, header=0, index_col=0, decimal='M')
table2 = tables[2]
table2.columns = ['census', 'prb', 'un', 'maddison', 
                  'hyde', 'tanton', 'biraben', 'mj', 
                  'thomlinson', 'durand', 'clark']
table2.shape

census = table2.census / 1e9
census.shape

un = table2.un / 1e9
un.shape

# A `DataFrame` contains `index`, which labels the rows.  It is an `Int64Index`, which is similar to a NumPy array.

table2.index

# And `columns`, which labels the columns.

table2.columns

# And `values`, which is an array of values.

table2.values

# A `Series` does not have `columns`, but it does have `name`.

census.name

# It contains `values`, which is an array.

census.values

# And it contains `index`:

census.index

# If you ever wonder what kind of object a variable refers to, you can use the `type` function.  The result indicates what type the object is, and the module where that type is defined.
#
# `DataFrame`, `Int64Index`, `Index`, and `Series` are defined by Pandas.
#
# `ndarray` is defined by NumPy.

type(table2)

type(table2.index)

type(table2.columns)

type(table2.values)

type(census)

type(census.index)

type(census.values)

# ## Optional exercise
#
# The following exercise provides a chance to practice what you have learned so far, and maybe develop a different growth model.  If you feel comfortable with what we have done so far, you might want to give it a try.
#
# **Optional Exercise:** On the Wikipedia page about world population estimates, the first table contains estimates for prehistoric populations.  The following cells process this table and plot some of the results.

filename = 'data/World_population_estimates.html'
tables = read_html(filename, header=0, index_col=0, decimal='M')
len(tables)

# Select `tables[1]`, which is the second table on the page.

table1 = tables[1]
table1.head()

# Not all agencies and researchers provided estimates for the same dates.  Again `NaN` is the special value that indicates missing data.

table1.tail()

# Again, we'll replace the long column names with more convenient abbreviations.

table1.columns = ['PRB', 'UN', 'Maddison', 'HYDE', 'Tanton', 
                  'Biraben', 'McEvedy & Jones', 'Thomlinson', 'Durand', 'Clark']

# Some of the estimates are in a form Pandas doesn't recognize as numbers, but we can coerce them to be numeric.

for col in table1.columns:
    table1[col] = pd.to_numeric(table1[col], errors='coerce')

# Here are the results.  Notice that we are working in millions now, not billions.

table1.plot()
decorate(xlim=[-10000, 2000], xlabel='Year', 
         ylabel='World population (millions)',
         title='Prehistoric population estimates')
plt.legend(fontsize='small');

# We can use `xlim` to zoom in on everything after Year 0.

table1.plot()
decorate(xlim=[0, 2000], xlabel='Year', 
         ylabel='World population (millions)',
         title='CE population estimates')
plt.legend(fontsize='small');

# See if you can find a model that fits these data well from Year 0 to 1950.
#
# How well does your best model predict actual population growth from 1950 to the present?

# +
# Solution

# The function I found that best matches the data has the form
# a + b / (c - x)

# This function is hard to explain physically; that is, it doesn't
# correspond to a growth model that makes sense in terms of human behavior.

# And it implies that the population goes to infinity in 2040.

xs = linspace(100, 1950)
ys = 110 + 200000 / (2040 - xs)
table1.plot()
plot(xs, ys, color='gray', label='model')

decorate(xlim=[0, 2000], xlabel='Year', 
         ylabel='World population (millions)',
         title='CE population estimates')
plt.legend(fontsize='small');

# +
# Solution

# And it doesn't do a particularly good job of predicting
# actual growth from 1940 to the present.

plot(census, ':', label='US Census')
plot(un, '--', label='UN DESA')

xs = linspace(1940, 2020)
ys = 110 + 200000 / (2040 - xs)
plot(xs, ys/1000, color='gray', label='model')

decorate(xlim=[1950, 2016], xlabel='Year', 
         ylabel='World population (billions)',
         title='Prehistoric population estimates')
# -


