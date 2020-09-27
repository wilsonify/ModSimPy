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
# Rabbit example
#
# Copyright 2017 Allen Downey
#
# License: [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0)
#

# +
# %matplotlib inline

from modsim import *
# -

# ## Rabbit Redux
#
# This notebook starts with a version of the rabbit population growth model and walks through some steps for extending it.
#
# In the original model, we treat all rabbits as adults; that is, we assume that a rabbit is able to breed in the season after it is born.  In this notebook, we extend the model to include both juvenile and adult rabbits.
#
# As an example, let's assume that rabbits take 3 seasons to mature.  We could model that process explicitly by counting the number of rabbits that are 1, 2, or 3 seasons old.  As an alternative, we can model just two stages, juvenile and adult.  In the simpler model, the maturation rate is 1/3 of the juveniles per season.
#
# To implement this model, make these changes in the System object:
#
# 1.  Replace `p0` with two initial populations: `juvenile_pop0` and `adult_pop0`, with values `0` and `10`.
#
# 2.  Add an additional variable, `mature_rate`, with the value `0.33`.

# +
system = System(t0 = 0, 
                t_end = 30,
                juvenile_pop0 = 0,
                adult_pop0 = 10,
                birth_rate = 0.9,
                mature_rate = 0.33,
                death_rate = 0.5)

system


# -

# Now update `run_simulation` with the following changes:
#
# 1.  Add a second TimeSeries, named `juveniles`, to keep track of the juvenile population, and initialize it with `juvenile_pop0`.
#
# 2.  Inside the for loop, compute the number of juveniles that mature during each time step.
#
# 3.  Also inside the for loop, add a line that stores the number of juveniles in the new `TimeSeries`.  For simplicity, let's assume that only adult rabbits die.
#
# 4.  During each time step, subtract the number of maturations from the juvenile population and add it to the adult population.
#

def run_simulation(system):
    """Runs a proportional growth model.
    
    Adds TimeSeries to `system` as `results`.
    
    system: System object with t0, t_end, p0,
            birth_rate and death_rate
    """
    juveniles = TimeSeries()
    juveniles[system.t0] = system.juvenile_pop0
    
    adults = TimeSeries()
    adults[system.t0] = system.adult_pop0
    
    for t in linrange(system.t0, system.t_end):
        maturations = system.mature_rate * juveniles[t]
        births = system.birth_rate * adults[t]
        deaths = system.death_rate * adults[t]
        
        if adults[t] > 30:
            market = adults[t] - 30
        else:
            market = 0
            
        juveniles[t+1] = juveniles[t] + births - maturations
        adults[t+1] = adults[t] + maturations - deaths - market
        
    system.adults = adults
    system.juveniles = juveniles


# Test your changes in `run_simulation`:

run_simulation(system)
system.adults


# Next, update `plot_results` to plot both the adult and juvenile `TimeSeries`.

def plot_results(system, title=None):
    """Plot the estimates and the model.
    
    system: System object with `results`
    """
    newfig()
    plot(system.adults, 'bo-', label='adults')
    plot(system.juveniles, 'gs-', label='juveniles')
    decorate(xlabel='Season', 
             ylabel='Rabbit population',
             title=title)


# And test your updated version of `plot_results`.

plot_results(system, title='Proportional growth model')

# This notebook demonstrates the steps we recommend for starting your project:
#
# 1.  Start with one of the examples from the book, either by copying a notebook or pasting code into a new notebook.  Get the code working before you make any changes.
#
# 2.  Make one small change, and run the code again.
#
# 3.  Repeat step 2 until you have a basic implementation of your model.
#
# If you start with working code that you understand and make small changes, you can avoid spending a lot of time debugging.
#
# One you have a basic model working, you can think about what metrics to measure, what parameters to sweep, and how to use the model to predict, explain, or design.

# ### Bonus question
#
# Suppose you only have room for 30 adult rabbits.  Whenever the adult population exceeds 30, you take any excess rabbits to market (as pets for kind children, of course).  Modify `run_simulation` to model this strategy.  What effect does it have on the behavior of the system?

# What happens if rabbits only take one season to mature?  Change `mature_rate` to 1.0 and run the simulation again.


