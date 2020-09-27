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
# Case Study: Predicting salmon returns
#
# This case study is based on a ModSim student project by Josh Deng and Erika Lu.
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

# ### Can we predict salmon populations?
#
# Each year the [U.S. Atlantic Salmon Assessment Committee](https://www.nefsc.noaa.gov/USASAC/Reports/USASAC2018-Report-30-2017-Activities.pdf) reports estimates of salmon populations in oceans and rivers in the northeastern United States.  The reports are useful for monitoring changes in these populations, but they generally do not include predictions.
#
# The goal of this case study is to model year-to-year changes in population, evaluate how predictable these changes are, and estimate the probability that a particular population will increase or decrease in the next 10 years.
#
# As an example, I'll use data from page 18 of the 2017 report, which provides population estimates for the Narraguagus and Sheepscot Rivers in Maine.
#
# ![USASAC_Report_2017_Page18](data/USASAC_Report_2017_Page18.png)
#
# At the end of this notebook, I make some suggestions for extracting data from a PDF document automatically, but for this example I will keep it simple and type it in.
#
# Here are the population estimates for the Narraguagus River:

pops = [2749, 2845, 4247, 1843, 2562, 1774, 1201, 1284, 1287, 2339, 1177, 962, 1176, 2149, 1404, 969, 1237, 1615, 1201];

# To get this data into a Pandas Series, I'll also make a range of years to use as an index.

years = range(1997, 2016)

# And here's the series.

pop_series = TimeSeries(pops, index=years, dtype=np.float64)


# Here's what it looks like:

# +
def plot_population(series):
    plot(series, label='Estimated population')
    decorate(xlabel='Year', 
             ylabel='Population estimate', 
             title='Narraguacus River',
             ylim=[0, 5000])
    
plot_population(pop_series)
# -

# ## Modeling changes
#
# To see how the population changes from year-to-year, I'll use `ediff1d` to compute the absolute difference between each year and the next.
#

abs_diffs = np.ediff1d(pop_series, to_end=0)

# We can compute relative differences by dividing by the original series elementwise.

rel_diffs = abs_diffs / pop_series

# Or we can use the `modsim` function `compute_rel_diff`:

rel_diffs = compute_rel_diff(pop_series)

# These relative differences are observed annual net growth rates.  So let's drop the `0` and save them.

rates = rel_diffs.drop(2015)

# A simple way to model this system is to draw a random value from this series of observed rates each year.  We can use the NumPy function `choice` to make a random choice from a series.

np.random.choice(rates)

# ## Simulation
#
# Now we can simulate the system by drawing random growth rates from the series of observed rates.
#
# I'll start the simulation in 2015.

t_0 = 2015
p_0 = pop_series[t_0]

# Create a `System` object with variables `t_0`, `p_0`, `rates`, and `duration=10` years. 
#
# The series of observed rates is one big parameter of the model.

system = System(t_0=t_0,
                p_0=p_0,
                duration=10,
                rates=rates)


# Write an update functon that takes as parameters `pop`, `t`, and `system`.
# It should choose a random growth rate, compute the change in population, and return the new population.

# +
# Solution

def update_func1(pop, t, system):
    """Simulate one time step.
    
    pop: population
    t: time step
    system: System object
    """
    rate = np.random.choice(system.rates)
    pop += rate * pop
    return pop


# -

# Test your update function and run it a few times

update_func1(p_0, t_0, system)


# Here's a version of `run_simulation` that stores the results in a `TimeSeries` and returns it.

def run_simulation(system, update_func):
    """Simulate a queueing system.
    
    system: System object
    update_func: function object
    """
    t_0 = system.t_0
    t_end = t_0 + system.duration
    
    results = TimeSeries()
    results[t_0] = system.p_0
    
    for t in linrange(t_0, t_end):
        results[t+1] = update_func(results[t], t, system)

    return results


# Use `run_simulation` to run generate a prediction for the next 10 years.
#
# The plot your prediction along with the original data.  Your prediction should pick up where the data leave off.

# +
# Solution

results = run_simulation(system, update_func1)
plot(results, label='Simulation')
plot_population(pop_series)


# -

# To get a sense of how much the results vary, we can run the model several times and plot all of the results.

def plot_many_simulations(system, update_func, iters):
    """Runs simulations and plots the results.
    
    system: System object
    update_func: function object
    iters: number of simulations to run
    """
    for i in range(iters):
        results = run_simulation(system, update_func)
        plot(results, color='gray', linewidth=5, alpha=0.1)


# The plot option `alpha=0.1` makes the lines semi-transparent, so they are darker where they overlap.
#
# Run `plot_many_simulations` with your update function and `iters=30`.  Also plot the original data.

# +
# Solution

plot_many_simulations(system, update_func1, 30)
plot_population(pop_series)


# -

# The results are highly variable: according to this model, the population might continue to decline over the next 10 years, or it might recover and grow rapidly!
#
# It's hard to say how seriously we should take this model.  There are many factors that influence salmon populations that are not included in the model.  For example, if the population starts to grow quickly, it might be limited by resource limits, predators, or fishing.  If the population starts to fall, humans might restrict fishing and stock the river with farmed fish.
#
# So these results should probably not be considered useful predictions.  However, there might be something useful we can do, which is to estimate the probability that the population will increase or decrease in the next 10 years.  

# ## Distribution of net changes
#
# To describe the distribution of net changes, write a function called `run_many_simulations` that runs many simulations, saves the final populations in a `ModSimSeries`, and returns the `ModSimSeries`.
#

def run_many_simulations(system, update_func, iters):
    """Runs simulations and report final populations.
    
    system: System object
    update_func: function object
    iters: number of simulations to run
    
    returns: series of final populations
    """
    # FILL THIS IN


# +
# Solution

def run_many_simulations(system, update_func, iters):
    """Runs simulations and report final populations.
    
    system: System object
    update_func: function object
    iters: number of simulations to run
    
    returns: series of final populations
    """
    last_pops = ModSimSeries()
    
    for i in range(iters):
        results = run_simulation(system, update_func)
        last_pops[i] = get_last_value(results)
        
    return last_pops


# -

# Test your function by running it with `iters=5`.

run_many_simulations(system, update_func1, 5)

# Now we can run 1000 simulations and describe the distribution of the results.

last_pops = run_many_simulations(system, update_func1, 1000)
last_pops.describe()

# If we substract off the initial population, we get the distribution of changes.

net_changes = last_pops - p_0
net_changes.describe()

# The median is negative, which indicates that the population decreases more often than it increases.
#
# We can be more specific by counting the number of runs where `net_changes` is positive.

np.sum(net_changes > 0)

# Or we can use `mean` to compute the fraction of runs where `net_changes` is positive.

np.mean(net_changes > 0)

# And here's the fraction where it's negative.

np.mean(net_changes < 0)

# So, based on observed past changes, this model predicts that the population is more likely to decrease than increase over the next 10 years, by about 2:1.

# ## A refined model
#
# There are a few ways we could improve the model.
#
# 1.  It looks like there might be cyclic behavior in the past data, with a period of 4-5 years.  We could extend the model to include this effect.
#
# 2.  Older data might not be as relevant for prediction as newer data, so we could give more weight to newer data.
#
# The second option is easier to implement, so let's try it.
#
# I'll use `linspace` to create an array of "weights" for the observed rates.  The probability that I choose each rate will be proportional to these weights.
#
# The weights have to add up to 1, so I divide through by the total.

weights = linspace(0, 1, len(rates))
weights /= sum(weights)
plot(weights)
decorate(xlabel='Index into the rates array',
         ylabel='Weight')

# I'll add the weights to the `System` object, since they are parameters of the model.

system.weights = weights

# We can pass these weights as a parameter to `np.random.choice` (see the [documentation](https://docs.scipy.org/doc/numpy/reference/generated/numpy.random.choice.html))

np.random.choice(system.rates, p=system.weights)


# Write an update function that takes the weights into account.

# +
# Solution

def update_func2(pop, t, system):
    """Simulate one time step.
    
    pop: population
    t: time step
    system: System object
    """
    rate = np.random.choice(system.rates, p=system.weights)
    pop += rate * pop
    return pop


# -

# Use `plot_many_simulations` to plot the results.

# +
# Solution

plot_many_simulations(system, update_func2, 30)
plot_population(pop_series)
# -

# Use `run_many_simulations` to collect the results and `describe` to summarize the distribution of net changes.

# +
# Solution

last_pops = run_many_simulations(system, update_func2, 1000)
net_changes = last_pops - p_0
net_changes.describe()
# -

# Does the refined model have much effect on the probability of population decline?

# +
# Solution

np.mean(net_changes < 0)
# -

# ## Extracting data from a PDF document
#
# The following section uses `tabula-py` to get data from a PDF document.
#
# If you don't already have it installed, and you are using Anaconda, you can install it by running the following command in a Terminal or Git Bash:
#
# ```
# conda install -c conda-forge tabula-py
# ```

from tabula import read_pdf

df = read_pdf('data/USASAC2018-Report-30-2017-Activities-Page11.pdf')
