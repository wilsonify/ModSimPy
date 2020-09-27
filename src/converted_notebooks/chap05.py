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
# Chapter 5
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

# ## Reading data
#
# Pandas is a library that provides tools for reading and processing data.  `read_html` reads a web page from a file or the Internet and creates one `DataFrame` for each table on the page.

from pandas import read_html

# The data directory contains a downloaded copy of https://en.wikipedia.org/wiki/World_population_estimates
#
# The arguments of `read_html` specify the file to read and how to interpret the tables in the file.  The result, `tables`, is a sequence of `DataFrame` objects; `len(tables)` reports the length of the sequence.

filename = 'data/World_population_estimates.html'
tables = read_html(filename, header=0, index_col=0, decimal='M')
len(tables)

# We can select the `DataFrame` we want using the bracket operator.  The tables are numbered from 0, so `tables[2]` is actually the third table on the page.
#
# `head` selects the header and the first five rows.

table2 = tables[2]
table2.head()

# `tail` selects the last five rows.

table2.tail()

# Long column names are awkard to work with, but we can replace them with abbreviated names.

table2.columns = ['census', 'prb', 'un', 'maddison', 
                  'hyde', 'tanton', 'biraben', 'mj', 
                  'thomlinson', 'durand', 'clark']

# Here's what the DataFrame looks like now.  

table2.head()

# The first column, which is labeled `Year`, is special.  It is the **index** for this `DataFrame`, which means it contains the labels for the rows.
#
# Some of the values use scientific notation; for example, `2.544000e+09` is shorthand for $2.544 \cdot 10^9$ or 2.544 billion.
#
# `NaN` is a special value that indicates missing data.

# ### Series
#
# We can use dot notation to select a column from a `DataFrame`.  The result is a `Series`, which is like a `DataFrame` with a single column.

census = table2.census
census.head()

census.tail()

# Like a `DataFrame`, a `Series` contains an index, which labels the rows.
#
# `1e9` is scientific notation for $1 \cdot 10^9$ or 1 billion.

# From here on, we will work in units of billions.

un = table2.un / 1e9
un.head()

census = table2.census / 1e9
census.head()

# Here's what these estimates look like.

# +
plot(census, ':', label='US Census')
plot(un, '--', label='UN DESA')
    
decorate(xlabel='Year',
         ylabel='World population (billion)')

savefig('figs/chap05-fig01.pdf')
# -

# The following expression computes the elementwise differences between the two series, then divides through by the UN value to produce [relative errors](https://en.wikipedia.org/wiki/Approximation_error), then finds the largest element.
#
# So the largest relative error between the estimates is about 1.3%.

max(abs(census - un) / un) * 100

# **Exercise:** Break down that expression into smaller steps and display the intermediate results, to make sure you understand how it works.
#
# 1.  Compute the elementwise differences, `census - un`
# 2.  Compute the absolute differences, `abs(census - un)`
# 3.  Compute the relative differences, `abs(census - un) / un`
# 4.  Compute the percent differences, `abs(census - un) / un * 100`
#

# +
# Solution goes here

# +
# Solution goes here

# +
# Solution goes here

# +
# Solution goes here
# -

# `max` and `abs` are built-in functions provided by Python, but NumPy also provides version that are a little more general.  When you import `modsim`, you get the NumPy versions of these functions.

# ### Constant growth

# We can select a value from a `Series` using bracket notation.  Here's the first element:

census[1950]

# And the last value.

census[2016]

# But rather than "hard code" those dates, we can get the first and last labels from the `Series`:

t_0 = get_first_label(census)

t_end = get_last_label(census)

elapsed_time = t_end - t_0

# And we can get the first and last values:

p_0 = get_first_value(census)

p_end = get_last_value(census)

# Then we can compute the average annual growth in billions of people per year.

total_growth = p_end - p_0

annual_growth = total_growth / elapsed_time

# ### TimeSeries

# Now let's create a `TimeSeries` to contain values generated by a linear growth model.

results = TimeSeries()

# Initially the `TimeSeries` is empty, but we can initialize it so the starting value, in 1950, is the 1950 population estimated by the US Census.

results[t_0] = census[t_0]
results

# After that, the population in the model grows by a constant amount each year.

for t in linrange(t_0, t_end):
    results[t+1] = results[t] + annual_growth

# Here's what the results looks like, compared to the actual data.

# +
plot(census, ':', label='US Census')
plot(un, '--', label='UN DESA')
plot(results, color='gray', label='model')

decorate(xlabel='Year', 
         ylabel='World population (billion)',
         title='Constant growth')

savefig('figs/chap05-fig02.pdf')
# -

# The model fits the data pretty well after 1990, but not so well before.

# ### Exercises
#
# **Optional Exercise:**  Try fitting the model using data from 1970 to the present, and see if that does a better job.
#
# Hint: 
#
# 1. Copy the code from above and make a few changes.  Test your code after each small change.
#
# 2. Make sure your `TimeSeries` starts in 1950, even though the estimated annual growth is based on later data.
#
# 3. You might want to add a constant to the starting value to match the data better.

# +
# Solution goes here
# -

census.loc[1960:1970]


