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
# Case study
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

# ### Exponential, geometric, and polynomial growth

# **Exercise:**  Suppose there are two banks across the street from each other, The First Geometric Bank (FGB) and Exponential Savings and Loan (ESL).  They offer the same interest rate on checking accounts, 3%, but at FGB, they compute and pay interest at the end of each year, and at ESL they compound interest continuously.
#
# If you deposit $p_0$ dollars at FGB at the beginning of Year 0, the balanace of your account at the end of Year $n$ is
#
# $ x_n = p_0 (1 + \alpha)^n $
#
# where $\alpha = 0.03$.  At ESL, your balance at any time $t$ would be
#
# $ x(t) = p_0 \exp(\alpha t) $
#
# If you deposit \$1000 at each back at the beginning of Year 0, how much would you have in each account after 10 years?
#
# Is there an interest rate FGB could pay so that your balance at the end of each year would be the same at both banks?  What is it?
#
# Hint: `modsim` provides a function called `exp`, which is a wrapper for the NumPy function `exp`.

# +
# Solution

p_0 = 1000
alpha = 0.03

# +
# Solution

ts = linrange(11)

# +
# Solution

geometric = p_0 * (1 + alpha) ** ts

# +
# Solution

exponential = p_0 * exp(alpha * ts)

# +
# Solution

alpha2 = exp(alpha) - 1

# +
# Solution

geometric = p_0 * (1 + alpha2) ** ts

# +
# Solution

plot(ts, exponential, '-', label='Exponential')
plot(ts, geometric, 's', label='Geometric')

decorate(xlabel='Time (years)',
         ylabel='Value (dollars)')
# -

# **Exercise:** Suppose a new bank opens called the Polynomial Credit Union (PCU).  In order to compete with First Geometric Bank and Exponential Savings and Loan, PCU offers a parabolic savings account where the balance is a polynomial function of time:
#
# $ x(t) = p_0 + \beta_1 t + \beta_2 t^2 $
#
# As a special deal, they offer an account with $\beta_1 = 30$ and $\beta_2 = 0.5$, with those parameters guaranteed for life.
#
# Suppose you deposit \$1000 at all three banks at the beginning of Year 0.  How much would you have in each account at the end of Year 10?  How about Year 20?  And Year 100?

# +
# Solution

number_of_years = 100
ts = linrange(number_of_years+1)
geometric = p_0 * (1 + alpha2) ** ts
exponential = p_0 * exp(alpha * ts)
None

# +
# Solution

beta1 = 30
beta2 = 0.5
parabolic = p_0 + beta1 * ts + beta2 * ts**2
None


# +
# Solution

def plot_results():
    plot(ts, exponential, '-', label='Exponential')
    plot(ts, geometric, 's', label='Geometric')
    plot(ts, parabolic, 'o', label='Parabolic')
    
    decorate(xlabel='Time (years)',
             ylabel='Value (dollars)')


# +
# Solution

plot_results()

# +
# Solution

plot_results()
plt.yscale('log')
# -




