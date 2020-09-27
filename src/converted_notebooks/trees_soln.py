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

# +
# Configure Jupyter so figures appear in the notebook
# %matplotlib inline

# Configure Jupyter to display the assigned value after an assignment
# %config InteractiveShell.ast_node_interactivity='last_expr_or_assign'

# import functions from the modsim.py module
from modsim import *
# -

# ### Modeling tree growth
#
# This case study is based on "[Height-Age Curves for Planted Stands of Douglas Fir, with Adjustments for Density](http://www.cfr.washington.edu/research.smc/working_papers/smc_working_paper_1.pdf)", a working paper by Flewelling, Collier, Gonyea, Marshall, and Turnblom.
#
# It provides "site index curves", which are curves that show the expected height of the tallest tree in a stand of Douglas firs as a function of age, for a stand where the trees are the same age.
#
# Depending on the quality of the site, the trees might grow more quickly or slowing.  So each curve is identified by a "site index" that indicates the quality of the site.
#
# I'll start with some of the data from their Table 1.  Here's the sequence of ages.

years = [2, 3, 4, 5, 6, 8, 10, 15, 20, 25, 30,
         35, 40, 45, 50, 55, 60, 65, 70]

# And here's the series of heights for a site with index 45, indicating that height at 30 years is 45 feet.

site45 = TimeSeries([1.4, 1.49, 1.75, 2.18, 2.78, 4.45, 6.74,
                    14.86, 25.39, 35.60, 45.00, 53.65, 61.60,
                    68.92, 75.66, 81.85, 87.56, 92.8, 97.63],
                    index=years)

# Here's the series for site index 65.

site65 = TimeSeries([1.4, 1.56, 2.01, 2.76, 3.79, 6.64, 10.44, 
                    23.26, 37.65, 51.66, 65.00, 77.50, 89.07, 
                    99.66, 109.28, 117.96, 125.74, 132.68, 138.84],
                    index=years)

# And for site index 85.

site85 = Series([1.4, 1.8, 2.71, 4.09, 5.92, 10.73, 16.81, 
                 34.03, 51.26, 68.54, 85, 100.34, 114.33,
                 126.91, 138.06, 147.86, 156.39, 163.76, 170.10],
               index=years)

# Here's what the curves look like:

# +
plot(site85, label='SI 85')
plot(site65, label='SI 65')
plot(site45, label='SI 45')
decorate(xlabel='Time (years)',
         ylabel='Height (feet)')

savefig('figs/trees-fig01.pdf')
# -

# For my examples I'll work with the SI 65 data; as an exercise, you can run the notebook again with either of the other curves.

data = site65;

# ### Model 1
#
# As a starting place, let's assume that the ability of the tree to gain mass is limited by the area it exposes to sunlight, and that the growth rate (in mass) is proportional to that area.  In that case we can write:
#
# $ m_{n+1} = m_n + \alpha A$
#
# where $m_n$ is the mass of the at time step $n$, $A$ is the area exposed to sunlight, and $\alpha$ is an unknown growth parameter.
#
# To get from $m$ to $A$, I'll make the additional assumption that mass is proportional to height raised to an unknown power:
#
# $ m = \beta h^D $
#
# where $h$ is height, $\beta$ is an unknown constant of proportionality, and $D$ is the dimension that relates height and mass.  
#
# We'll start by assuming $D=3$, but we'll revisit that assumption.
#
# Finally, we'll assume that area is proportional to height squared:
#
# $ A = \gamma h^2$
#
# I'll specify height in feet, and choose units for mass and area so that $\beta=1$ and $\gamma=1$.
#
# Putting all that together, we can write a difference equation for height:
#
# $ h_{n+1}^D = h_n^D + \alpha h_n^2 $
#
# Now let's solve it.  Here's a system object with the parameters and initial conditions.

# +
alpha = 7
dim = 3

t_0 = get_first_label(data)
t_end = get_last_label(data)

h_0 = get_first_value(data)

system = System(alpha=alpha, dim=dim, 
                h_0=h_0, t_0=t_0, t_end=t_end)


# -

# And here's an update function that takes the current height as a parameter and returns the height during the next time step.

def update(height, t, system):
    """Update height based on geometric model.
    
    height: current height in feet
    t: what year it is
    system: system object with model parameters
    """
    area = height**2
    mass = height**system.dim
    mass += system.alpha * area
    return mass**(1/system.dim)


# Test the update function with the initial conditions.

update(h_0, t_0, system)


# Here's our usual version of `run_simulation`.

def run_simulation(system, update_func):
    """Simulate the system using any update function.
    
    system: System object
    update_func: function that computes the population next year
    
    returns: TimeSeries
    """
    results = TimeSeries()
    results[system.t_0] = system.h_0
    
    for t in linrange(system.t_0, system.t_end):
        results[t+1] = update_func(results[t], t, system)
        
    return results


# And here's how we run it.

results = run_simulation(system, update)
results.tail()


# Plot the results:

# +
def plot_results(results, data):
    plot(results, ':', label='model', color='gray')
    plot(data, label='data')
    decorate(xlabel='Time (years)',
             ylabel='Height (feet)')
    
plot_results(results, data)
# -

# The result converges to a straight line.
#
# I chose the value of `alpha` to fit the data as well as I could, but it is clear that the data have curvature that's not captured by the model.
#
# Here are the errors:

errors = results - data
errors.dropna()


# And here's the mean absolute error.

# +
def mean_abs_error(results, data):
    return np.mean(np.abs(results-data))

mean_abs_error(results, data)
# -

# This model might explain why the height of a tree grows roughly linearly:
#
# 1. If area is proportional to $h^2$ and mass is proportional to $h^3$, and
#
# 2. Change in mass is proportional to area, and
#
# 3. Height grows linearly, then
#
# 4. Area grows in proportion to $h^2$, and
#
# 5. Mass grows in proportion to $h^3$.
#
# If the goal is to explain (approximate) linear growth, we might stop there.  But this model does not fit the data particularly well, and it implies that trees could keep growing forever.
#
# So we might want to do better.

# ### Model 2

# As a second attempt, let's suppose that we don't know $D$.  In fact, we don't, because trees are not like simple solids; they are more like fractals, which have [fractal dimension](https://en.wikipedia.org/wiki/Fractal_dimension).
#
# I would expect the fractal dimension of a tree to be between 2 and 3, so I'll guess 2.5.

# +
alpha = 7
dim = 2.8

params = alpha, dim


# -

# I'll wrap the code from the previous section is a function that takes the parameters as inputs and makes a `System` object.

def make_system(params, data):
    """Makes a System object.
    
    params: sequence of alpha, dim
    data: Series
    
    returns: System object
    """
    alpha, dim = params
    
    t_0 = get_first_label(data)
    t_end = get_last_label(data)

    h_0 = get_first_value(data)

    return System(alpha=alpha, dim=dim, 
                  h_0=h_0, t_0=t_0, t_end=t_end)


# Here's how we use it.

system = make_system(params, data)


# With different values for the parameters, we get curves with different behavior.  Here are a few that I chose by hand.

def run_and_plot(alpha, dim, data):
    params = alpha, dim
    system = make_system(params, data)
    results = run_simulation(system, update)
    plot(results, ':', color='gray')


# +
run_and_plot(0.145, 2, data)
run_and_plot(0.58, 2.4, data)
run_and_plot(2.8, 2.8, data)
run_and_plot(6.6, 3, data)
run_and_plot(15.5, 3.2, data)
run_and_plot(38, 3.4, data)

plot(data, label='data')
decorate(xlabel='Time (years)',
             ylabel='Height (feet)')


# -

# To find the parameters that best fit the data, I'll use `leastsq`.
#
# We need an error function that takes parameters and returns errors:

def error_func(params, data, update_func):
    """Runs the model and returns errors.
    
    params: sequence of alpha, dim
    data: Series
    update_func: function object
    
    returns: Series of errors
    """
    print(params)
    system = make_system(params, data)
    results = run_simulation(system, update_func)
    return (results - data).dropna()


# Here's how we use it:

errors = error_func(params, data, update)

# Now we can pass `error_func` to `leastsq`, which finds the parameters that minimize the squares of the errors.

best_params, details = leastsq(error_func, params, data, update)
details

# Using the best parameters we found, we can run the model and plot the results.

# +
system = make_system(best_params, data)
results = run_simulation(system, update)

plot_results(results, data)
# -

# The mean absolute error is better than for Model 1, but that doesn't mean much.  The model still doesn't fit the data well.

mean_abs_error(results, data)

# And the estimated fractal dimension is 3.11, which doesn't seem likely.
#
# Let's try one more thing.

# ### Model 3

# Models 1 and 2 imply that trees can grow forever, but we know that's not true.  As trees get taller, it gets harder for them to move water and nutrients against the force of gravity, and their growth slows.
#
# We can model this effect by adding a term to the model similar to what we saw in the logistic model of population growth.  Instead of assuming:
#
# $ m_{n+1} = m_n + \alpha A $ 
#
# Let's assume
#
# $ m_{n+1} = m_n + \alpha A (1 - h / K) $
#
# where $K$ is similar to the carrying capacity of the logistic model.  As $h$ approaches $K$, the factor $(1 - h/K)$ goes to 0, causing growth to level off.
#
# Here's what the implementation of this model looks like:

# +
alpha = 2.0
dim = 2.5
K = 150

params = [alpha, dim, K]


# -

# Here's an updated version of `make_system`

def make_system(params, data):
    """Makes a System object.
    
    params: sequence of alpha, dim, K
    data: Series
    
    returns: System object
    """
    alpha, dim, K = params
    
    t_0 = get_first_label(data)
    t_end = get_last_label(data)

    h_0 = get_first_value(data)

    return System(alpha=alpha, dim=dim, K=K, 
                  h_0=h_0, t_0=t_0, t_end=t_end)


# Here's the new `System` object.

system = make_system(params, data)


# And here's the new update function.

def update3(height, t, system):
    """Update height based on geometric model with growth limiting term.
    
    height: current height in feet
    t: what year it is
    system: system object with model parameters
    """
    area = height**2
    mass = height**system.dim
    mass += system.alpha * area * (1 - height/system.K)
    return mass**(1/system.dim)


# As always, we'll test the update function with the initial conditions.

update3(h_0, t_0, system)

# Now we can test the error function with the new update function.

error_func(params, data, update3)

# And search for the best parameters.

best_params, details = leastsq(error_func, params, data, update3)
details

# With these parameters, we can fit the data much better.

# +
system = make_system(best_params, data)
results = run_simulation(system, update3)

plot_results(results, data)
# -

# And the mean absolute error is substantually smaller.

mean_abs_error(results, data)

# The estimated fractal dimension is about 2.6, which is plausible for a tree.
#
# Basically, it suggests that if you double the height of the tree, the mass grows by a factor of $2^{2.6}$

2**2.6

# In other words, the mass of the tree scales faster than area, but not as fast as it would for a solid 3-D object.
#
# What is this model good for?
#
# 1) It offers a possible explanation for the shape of tree growth curves.
#
# 2) It provides a way to estimate the fractal dimension of a tree based on a growth curve (probably with different values for different species).
#
# 3) It might provide a way to predict future growth of a tree, based on measurements of past growth.  As with the logistic population model, this would probably only work if we have observed the part of the curve where the growth rate starts to decline.

# ### Analysis
#
# With some help from my colleague, John Geddes, we can do some analysis.
#
# Starting with the difference equation in terms of mass:
#  
# $m_{n+1} = m_n + \alpha A (1 - h / K) $
#
# We can write the corresponding differential equation:
#
# (1) $ \frac{dm}{dt} = \alpha A (1 - h / K) $
#
# With
#
# (2) $A = h^2$
#
# and
#
# (3) $m = h^D$
#
# Taking the derivative of the last equation yields
#
# (4) $\frac{dm}{dt} = D h^{D-1} \frac{dh}{dt}$
#
# Combining (1), (2), and (4), we can write a differential equation for $h$:
#
# (5) $\frac{dh}{dt} = \frac{\alpha}{D} h^{3-D} (1 - h/K)$
#
# Now let's consider two cases:
#
# * With infinite $K$, the factor $(1 - h/K)$ approaches 1, so we have Model 2.
# * With finite $K$, we have Model 3.
#
# #### Model 2
#
# Within Model 2, we'll consider two special cases, with $D=2$ and $D=3$.
#
# With $D=2$, we have
#
# $\frac{dh}{dt} = \frac{\alpha}{2} h$
#
# which yields exponential growth with parameter $\alpha/2$.
#
# With $D=3$, we have Model 1, with this equation:
#
# $\frac{dh}{dt} = \frac{\alpha}{3}$
#
# which yields linear growth with parameter $\alpha/3$.
#
# This result explains why Model 1 is linear.
#
#
#
# #### Model 3
#
# Within Model 3, we'll consider two special cases, with $D=2$ and $D=3$.
#
# With $D=2$, we have
#
# $\frac{dh}{dt} = \frac{\alpha}{2} h (1 - h/K)$
#
# which yields logisitic growth with parameters $r = \alpha/2$ and $K$.
#
# With $D=3$, we have
#
# $\frac{dh}{dt} = \frac{\alpha}{3} (1 - h/K)$
#
# which yields a first order step response; that is, it converges to $K$ like a negative exponential:
#
# $ h(t) = c \exp(-\frac{\alpha}{3K} t) + K $
#
# where $c$ is a constant that depends on the initial conditions.

alpha = 10
D = 3
K = 200
params = alpha, D, K
system = make_system(params, data)
results = run_simulation(system, update3);

t = results.index
a = alpha/3
h = (-220) * exp(-a * t / K) + K
plot(t, h)
plot(results)
decorate(xlabel='Time (years)',
         ylabel='Height (feet)')

# Additional resources:
#
# Garcia, [A stochastic differential equation model for the
# height growth of forest stands](http://citeseerx.ist.psu.edu/viewdoc/download;jsessionid=664FED1E46ABCBF6E16741C294B79976?doi=10.1.1.608.81&rep=rep1&type=pdf)
#
# [EasySDE software and data](http://forestgrowth.unbc.ca/)


