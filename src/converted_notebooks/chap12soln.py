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
# Chapter 12
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

# ### Code
#
# Here's the code from the previous notebook that we'll need.

def make_system(beta, gamma):
    """Make a system object for the SIR model.
    
    beta: contact rate in days
    gamma: recovery rate in days
    
    returns: System object
    """
    init = State(S=89, I=1, R=0)
    init /= sum(init)

    t0 = 0
    t_end = 7 * 14

    return System(init=init, t0=t0, t_end=t_end,
                  beta=beta, gamma=gamma)


def update_func(state, t, system):
    """Update the SIR model.
    
    state: State with variables S, I, R
    t: time step
    system: System with beta and gamma
    
    returns: State object
    """
    s, i, r = state

    infected = system.beta * i * s    
    recovered = system.gamma * i
    
    s -= infected
    i += infected - recovered
    r += recovered
    
    return State(S=s, I=i, R=r)


def run_simulation(system, update_func):
    """Runs a simulation of the system.
        
    system: System object
    update_func: function that updates state
    
    returns: TimeFrame
    """
    frame = TimeFrame(columns=system.init.index)
    frame.row[system.t0] = system.init
    
    for t in linrange(system.t0, system.t_end):
        frame.row[t+1] = update_func(frame.row[t], t, system)
    
    return frame


# ### Metrics

# Given the results, we can compute metrics that quantify whatever we are interested in, like the total number of sick students, for example.

def calc_total_infected(results):
    """Fraction of population infected during the simulation.
    
    results: DataFrame with columns S, I, R
    
    returns: fraction of population
    """
    return get_first_value(results.S) - get_last_value(results.S)


# Here's an example.|

# +
beta = 0.333
gamma = 0.25
system = make_system(beta, gamma)

results = run_simulation(system, update_func)
print(beta, gamma, calc_total_infected(results))


# -

# **Exercise:** Write functions that take a `TimeFrame` object as a parameter and compute the other metrics mentioned in the book:
#
# 1.  The fraction of students who are sick at the peak of the outbreak.
#
# 2.  The day the outbreak peaks.
#
# 3.  The fraction of students who are sick at the end of the semester.
#
# Note: Not all of these functions require the `System` object, but when you write a set of related functons, it is often convenient if they all take the same parameters.
#
# Hint:  If you have a `TimeSeries` called `I`, you can compute the largest value of the series like this:
#
#     I.max()
#
# And the index of the largest value like this:
#
#     I.idxmax()
#
# You can read about these functions in the `Series` [documentation](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.html).

# +
# Solution

def fraction_sick_at_peak(results):
    return results.I.max()

fraction_sick_at_peak(results)


# +
# Solution

def time_of_peak(results):
    return results.I.idxmax()

time_of_peak(results)


# +
# Solution

def sick_at_end(results):
    return get_last_value(results.I)

sick_at_end(results)


# -

# ### What if?

# We can use this model to evaluate "what if" scenarios.  For example, this function models the effect of immunization by moving some fraction of the population from S to R before the simulation starts.

def add_immunization(system, fraction):
    """Immunize a fraction of the population.
    
    Moves the given fraction from S to R.
    
    system: System object
    fraction: number from 0 to 1
    """
    system.init.S -= fraction
    system.init.R += fraction


# Let's start again with the system we used in the previous sections.

# +
tc = 3      # time between contacts in days 
tr = 4      # recovery time in days

beta = 1 / tc      # contact rate in per day
gamma = 1 / tr     # recovery rate in per day

system = make_system(beta, gamma)
# -

# And run the model without immunization.

results = run_simulation(system, update_func)
calc_total_infected(results)

# Now with 10% immunization.

system2 = make_system(beta, gamma)
add_immunization(system2, 0.1)
results2 = run_simulation(system2, update_func)
calc_total_infected(results2)

# 10% immunization leads to a drop in infections of 16 percentage points.
#
# Here's what the time series looks like for S, with and without immunization.

# +
plot(results.S, '-', label='No immunization')
plot(results2.S, '--', label='10% immunization')

decorate(xlabel='Time (days)',
         ylabel='Fraction susceptible')

savefig('figs/chap12-fig01.pdf')
# -

# Now we can sweep through a range of values for the fraction of the population who are immunized.

immunize_array = linspace(0, 1, 11)
for fraction in immunize_array:
    system = make_system(beta, gamma)
    add_immunization(system, fraction)
    results = run_simulation(system, update_func)
    print(fraction, calc_total_infected(results))


# This function does the same thing and stores the results in a `Sweep` object.

def sweep_immunity(immunize_array):
    """Sweeps a range of values for immunity.
    
    immunize_array: array of fraction immunized
    
    returns: Sweep object
    """
    sweep = SweepSeries()
    
    for fraction in immunize_array:
        system = make_system(beta, gamma)
        add_immunization(system, fraction)
        results = run_simulation(system, update_func)
        sweep[fraction] = calc_total_infected(results)
        
    return sweep


# Here's how we run it.

immunize_array = linspace(0, 1, 21)
infected_sweep = sweep_immunity(immunize_array)

# And here's what the results look like.

# +
plot(infected_sweep)

decorate(xlabel='Fraction immunized',
         ylabel='Total fraction infected',
         title='Fraction infected vs. immunization rate',
         legend=False)

savefig('figs/chap12-fig02.pdf')


# -

# If 40% of the population is immunized, less than 4% of the population gets sick.

# ### Logistic function

# To model the effect of a hand-washing campaign, I'll use a [generalized logistic function](https://en.wikipedia.org/wiki/Generalised_logistic_function) (GLF), which is a convenient function for modeling curves that have a generally sigmoid shape.  The parameters of the GLF correspond to various features of the curve in a way that makes it easy to find a function that has the shape you want, based on data or background information about the scenario.

def logistic(x, A=0, B=1, C=1, M=0, K=1, Q=1, nu=1):
    """Computes the generalize logistic function.
    
    A: controls the lower bound
    B: controls the steepness of the transition 
    C: not all that useful, AFAIK
    M: controls the location of the transition
    K: controls the upper bound
    Q: shift the transition left or right
    nu: affects the symmetry of the transition
    
    returns: float or array
    """
    exponent = -B * (x - M)
    denom = C + Q * exp(exponent)
    return A + (K-A) / denom ** (1/nu)


# The following array represents the range of possible spending.

spending = linspace(0, 1200, 21)


# `compute_factor` computes the reduction in `beta` for a given level of campaign spending.
#
# `M` is chosen so the transition happens around \$500.
#
# `K` is the maximum reduction in `beta`, 20%.
#
# `B` is chosen by trial and error to yield a curve that seems feasible.

def compute_factor(spending):
    """Reduction factor as a function of spending.
    
    spending: dollars from 0 to 1200
    
    returns: fractional reduction in beta
    """
    return logistic(spending, M=500, K=0.2, B=0.01)


# Here's what it looks like.

# +
percent_reduction = compute_factor(spending) * 100

plot(spending, percent_reduction)

decorate(xlabel='Hand-washing campaign spending (USD)',
         ylabel='Percent reduction in infection rate',
         title='Effect of hand washing on infection rate',
         legend=False)


# -

# **Exercise:** Modify the parameters `M`, `K`, and `B`, and see what effect they have on the shape of the curve.  Read about the [generalized logistic function on Wikipedia](https://en.wikipedia.org/wiki/Generalised_logistic_function).  Modify the other parameters and see what effect they have.

# ### Hand washing

# Now we can model the effect of a hand-washing campaign by modifying `beta`

def add_hand_washing(system, spending):
    """Modifies system to model the effect of hand washing.
    
    system: System object
    spending: campaign spending in USD
    """
    factor = compute_factor(spending)
    system.beta *= (1 - factor)


# Let's start with the same values of `beta` and `gamma` we've been using.

# +
tc = 3      # time between contacts in days 
tr = 4      # recovery time in days

beta = 1 / tc      # contact rate in per day
gamma = 1 / tr     # recovery rate in per day

beta, gamma
# -

# Now we can sweep different levels of campaign spending.

# +
spending_array = linspace(0, 1200, 13)

for spending in spending_array:
    system = make_system(beta, gamma)
    add_hand_washing(system, spending)
    results = run_simulation(system, update_func)
    print(spending, system.beta, calc_total_infected(results))


# -

# Here's a function that sweeps a range of spending and stores the results in a `SweepSeries`.

def sweep_hand_washing(spending_array):
    """Run simulations with a range of spending.
    
    spending_array: array of dollars from 0 to 1200
    
    returns: Sweep object
    """
    sweep = SweepSeries()
    
    for spending in spending_array:
        system = make_system(beta, gamma)
        add_hand_washing(system, spending)
        results = run_simulation(system, update_func)
        sweep[spending] = calc_total_infected(results)
        
    return sweep


# Here's how we run it.

spending_array = linspace(0, 1200, 20)
infected_sweep = sweep_hand_washing(spending_array)

# And here's what it looks like.

# +
plot(infected_sweep)

decorate(xlabel='Hand-washing campaign spending (USD)',
         ylabel='Total fraction infected',
         title='Effect of hand washing on total infections',
         legend=False)

savefig('figs/chap12-fig03.pdf')
# -

# Now let's put it all together to make some public health spending decisions.

# ### Optimization

# Suppose we have \$1200 to spend on any combination of vaccines and a hand-washing campaign.

num_students = 90
budget = 1200
price_per_dose = 100
max_doses = int(budget / price_per_dose)
dose_array = linrange(max_doses, endpoint=True)
max_doses

# We can sweep through a range of doses from, 0 to `max_doses`, model the effects of immunization and the hand-washing campaign, and run simulations.
#
# For each scenario, we compute the fraction of students who get sick.

for doses in dose_array:
    fraction = doses / num_students
    spending = budget - doses * price_per_dose
    
    system = make_system(beta, gamma)
    add_immunization(system, fraction)
    add_hand_washing(system, spending)
    
    results = run_simulation(system, update_func)
    print(doses, system.init.S, system.beta, calc_total_infected(results))


# The following function wraps that loop and stores the results in a `Sweep` object.

def sweep_doses(dose_array):
    """Runs simulations with different doses and campaign spending.
    
    dose_array: range of values for number of vaccinations
    
    return: Sweep object with total number of infections 
    """
    sweep = SweepSeries()
    
    for doses in dose_array:
        fraction = doses / num_students
        spending = budget - doses * price_per_dose
        
        system = make_system(beta, gamma)
        add_immunization(system, fraction)
        add_hand_washing(system, spending)
        
        results = run_simulation(system, update_func)
        sweep[doses] = calc_total_infected(results)

    return sweep


# Now we can compute the number of infected students for each possible allocation of the budget.

infected_sweep = sweep_doses(dose_array)

# And plot the results.

# +
plot(infected_sweep)

decorate(xlabel='Doses of vaccine',
         ylabel='Total fraction infected',
         title='Total infections vs. doses',
         legend=False)

savefig('figs/chap12-fig04.pdf')
# -

# ### Exercises
#
# **Exercise:** Suppose the price of the vaccine drops to $50 per dose.  How does that affect the optimal allocation of the spending?

# **Exercise:** Suppose we have the option to quarantine infected students.  For example, a student who feels ill might be moved to an infirmary, or a private dorm room, until they are no longer infectious.
#
# How might you incorporate the effect of quarantine in the SIR model?

# +
# Solution

"""There is no unique best answer to this question,
but one simple option is to model quarantine as an
effective reduction in gamma, on the assumption that
quarantine reduces the number of infectious contacts
per infected student.

Another option would be to add a fourth compartment
to the model to track the fraction of the population
in quarantine at each point in time.  This approach
would be more complex, and it is not obvious that it
is substantially better.

The following function could be used, like 
add_immunization and add_hand_washing, to adjust the
parameters in order to model various interventions.

In this example, `high` is the highest duration of
the infection period, with no quarantine.  `low` is
the lowest duration, on the assumption that it takes
some time to identify infectious students.

`fraction` is the fraction of infected students who 
are quarantined as soon as they are identified.
"""

def add_quarantine(system, fraction):
    """Model the effect of quarantine by adjusting gamma.
    
    system: System object
    fraction: fraction of students quarantined
    """
    # `low` represents the number of days a student 
    # is infectious if quarantined.
    # `high` is the number of days they are infectious
    # if not quarantined
    low = 1
    high = 4
    tr = high - fraction * (high-low)
    system.gamma = 1 / tr
