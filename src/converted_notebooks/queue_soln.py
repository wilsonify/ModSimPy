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
# Case Study: Queueing theory
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

# set the random number generator
np.random.seed(7)


# -

# ## One queue or two?
#
# This notebook presents a solution to an exercise from *Modeling and Simulation in Python*.  It uses features from the first four chapters to answer a question related to queueing theory, which is the study of systems that involve waiting in lines, also known as "queues".
#
# Suppose you are designing the checkout area for a new store.  There is room for two checkout counters and a waiting area for customers.  You can make two lines, one for each counter, or one line that serves both counters.
#
# In theory, you might expect a single line to be better, but it has some practical drawbacks: in order to maintain a single line, you would have to install rope barriers, and customers might be put off by what seems to be a longer line, even if it moves faster.
#
# So you'd like to check whether the single line is really better and by how much.  Simulation can help answer this question.
#
# As we did in the bikeshare model, we'll assume that a customer is equally likely to arrive during any timestep.  I'll denote this probability using the Greek letter lambda, $\lambda$, or the variable name `lam`.  The value of $\lambda$ probably varies from day to day, so we'll have to consider a range of possibilities.
#
# Based on data from other stores, you know that it takes 5 minutes for a customer to check out, on average.  But checkout times are highly variable: most customers take less than 5 minutes, but some take substantially more.  A simple way to model this variability is to assume that when a customer is checking out, they have the same probability of finishing up during each time step.  I'll denote this probability using the Greek letter mu, $\mu$, or the variable name `mu`.
#
# If we choose $\mu=1/5$, the average number of time steps for each checkout will be 5 minutes, which is consistent with the data.

# ### One server, one queue
#
# Write a function called `make_system` that takes `lam` and `mu` as parameters and returns a `System` object with variables `lam`, `mu`, and `duration`.  Set `duration`, which is the number of time steps to simulate, to 10 hours, expressed in minutes. 

# +
# Solution

def make_system(lam, mu):
    """Make a System object.
    
    lam: arrival rate, per minute
    mu: service completion rate, per minute
    
    returns: System object
    """
    # duration is 10 hours, expressed in minutes
    return System(lam=lam, mu=mu, duration=10*60)


# -

# Test this function by creating a `System` object with `lam=1/8` and `mu=1/5`.

# +
# Solution

interarrival_time = 8
service_time = 5

lam = 1 / interarrival_time
mu = 1 / service_time

system = make_system(lam, mu)


# -

# Write an update function that takes as parameters `x`, which is the total number of customer in the store, including the one checking out; `t`, which is the number of minutes that have elapsed in the simulation, and `system`, which is a `System` object.
#
# If there's a customer checking out, it should use `flip` to decide whether they are done.  And it should use `flip` to decide if a new customer has arrived.
#
# It should return the total number of customers at the end of the time step.
#

# +
# Solution

def update_func1(x, t, system):
    """Simulate one time step.
    
    x: number of people in the shop
    t: time step
    system: System object
    """
    # if there's a customer in service, check if they're done
    if x > 0:
        if flip(system.mu):
            x -= 1
            
    # check for an arrival
    if flip(system.lam):
        x += 1
        
    return x


# -

# Test your function by calling it with `x=1`, `t=0`, and the `System` object you created.  If you run it a few times, you should see different results.

# +
# Solution

update_func1(1, 0, system)


# -

# Now we can run the simulation.  Here's a version of `run_simulation` that creates a `TimeSeries` with the total number of customers in the store, including the one checking out.

def run_simulation(system, update_func):
    """Simulate a queueing system.
    
    system: System object
    update_func: function object
    """
    x = 0
    results = TimeSeries()
    results[0] = x
    
    for t in linrange(0, system.duration):
        x = update_func(x, t, system)
        results[t+1] = x

    return results


# Call `run_simulation` with your update function and plot the results.

# +
# Solution

results = run_simulation(system, update_func1)
plot(results)
decorate(xlabel='Time (min)', ylabel='Customers')


# -

# After the simulation, we can compute `L`, which is the average number of customers in the system, and `W`, which is the average time customers spend in the store.  `L` and `W` are related by Little's Law:
#
# $L = \lambda W$
#
# Where $\lambda$ is the arrival rate.  Here's a function that computes them.

def compute_metrics(results, system):
    """Compute average number of customers and wait time.
    
    results: TimeSeries of queue lengths
    system: System object
    
    returns: L, W
    """
    L = results.mean()
    W = L / system.lam
    return L, W


# Call `compute_metrics` with the results from your simulation.

# +
# Solution

compute_metrics(results, system)
# -

# ### Parameter sweep
#
# Since we don't know the actual value of $\lambda$, we can sweep through a range of possibilities, from 10% to 80% of the completion rate, $\mu$.  (If customers arrive faster than the completion rate, the queue grows without bound.  In that case the metrics `L` and `W` just depend on how long the store is open.)
#
# Create an array of values for `lam`.

# +
# Solution

num_vals = 101
lam_array = linspace(0.1*mu, 0.8*mu, num_vals)
lam_array


# -

# Write a function that takes an array of values for `lam`, a single value for `mu`, and an update function.
#
# For each value of `lam`, it should run a simulation, compute `L` and `W`, and store the value of `W` in a `SweepSeries`.
#
# It should return the `SweepSeries`.

# +
# Solution

def sweep_lam(lam_array, mu, update_func):
    """Run simulations with a range of values for `lam`
    
    lam_array: array of values for `lam`
    mu: probability of finishing a checkout
    update_func: passed along to run_simulation
    
    returns: SweepSeries of average wait time vs lam
    """
    sweep = SweepSeries()
    
    for lam in lam_array:
        system = make_system(lam, mu)
        results = run_simulation(system, update_func)
        L, W = compute_metrics(results, system)
        sweep[lam] = W
        
    return sweep


# -

# Call your function to generate a `SweepSeries`, and plot it.

# +
# Solution

sweep = sweep_lam(lam_array, mu, update_func1)

# +
# Solution

plot(sweep, 'bo')

decorate(xlabel='Arrival late, lambda (per min)',
         ylabel='Average time in system',
         title='Single server, single queue')


# -

# If we imagine that this range of values represents arrival rates on different days, we can use the average value of `W`, for a range of values of `lam`, to compare different queueing strategies.

# +
# W_avg = sweep.mean()
# -

# ### Analysis
#
# The model I chose for this system is a common model in queueing theory, in part because many of its properties can be derived analytically.
#
# In particular, we can derive the average time in the store as a function of $\mu$ and $\lambda$:
#
# $W = 1 / (\mu - \lambda)$
#
# The following function plots the theoretical value of $W$ as a function of $\lambda$.

def plot_W(lam_array, mu):
    """Plot the theoretical mean wait time.
    
    lam_array: array of values for `lam`
    mu: probability of finishing a checkout
    """
    W = 1 / (mu - lam_array)
    plot(lam_array, W, 'g-')


# Use this function to plot the theoretical results, then plot your simulation results again on the same graph.  How do they compare?

# +
# Solution

plot_W(lam_array, mu)
plot(sweep, 'bo')

decorate(xlabel='Arrival late, lambda (per min)',
         ylabel='Average time in system',
         title='Single server, single queue')


# -

# ### Multiple servers
#
# Now let's try the other two queueing strategies:
#
# 1.  One queue with two checkout counters.
# 2.  Two queues, one for each counter.
#
# The following figure shows the three scenarios:
#
# ![](diagrams/queue.png)
#
# Write an update function for one queue with two servers.

# +
# Solution

def update_func2(x, t, system):
    """Simulate a single queue with two servers.
    
    system: System object
    """
    # if both servers are busy, check whether the
    # second is complete
    if x > 1 and flip(system.mu):
        x -= 1
            
    # check whether the first is complete
    if x > 0 and flip(system.mu):
        x -= 1
    
    # check for an arrival
    if flip(system.lam):
        x += 1
        
    return x


# -

# Use this update function to simulate the system, plot the results, and print the metrics.

# +
# Solution

system = make_system(lam, mu)
run_simulation(system, update_func2)
plot(results)
decorate(xlabel='Time (min)', ylabel='Customers')
compute_metrics(results, system)
# -

# Since we have two checkout counters now, we can consider values for $\lambda$ that exceed $\mu$.
#
# Create a new array of values for `lam` from 10% to 160% of `mu`.

# +
# Solution

lam_array = linspace(0.1*mu, 1.6*mu, num_vals)
# -

# Use your sweep function to simulate the two server, one queue scenario with a range of values for `lam`.
#
# Plot the results and print the average value of `W` across all values of `lam`.

# +
# Solution

sweep = sweep_lam(lam_array, mu, update_func2)
W_avg = sweep.mean()
print('Average of averages = ', W_avg, 'minutes')

# +
# Solution

plot(sweep, 'bo')
decorate(xlabel='Arrival late, lambda (per min)',
         ylabel='Average time in system',
         title='Multiple server, single queue')


# -

# ### Multiple queues
#
# To simulate the scenario with two separate queues, we need two state variables to keep track of customers in each queue.
#
# Write an update function that takes `x1`, `x2`, `t`, and `system` as parameters and returns `x1` and `x2` as return values.  f you are not sure how to return more than one return value, see `compute_metrics`.
#
# When a customer arrives, which queue do they join?

# +
# Solution

def update_func3(x1, x2, t, system):
    """Simulate two queues with one server each.
    
    x1: number of customers in queue 1
    x2: number of customers in queue 2
    t: time step
    system: System object
    """
    # if the first servers is busy, check it it's done
    if x1 > 0 and flip(system.mu):
        x1 -= 1
            
    # if the second queue is busy, check if it's done
    if x2 > 0 and flip(system.mu):
        x2 -= 1
            
    # check for an arrival
    if flip(system.lam):
        # join whichever queue is shorter
        if x1 < x2:
            x1 += 1
        else:
            x2 += 1
            
    return x1, x2


# -

# Write a version of `run_simulation` that works with this update function.

# +
# Solution

def run_simulation(system, update_func):
    """Simulate a queueing system.
    
    system: System object
    update_func: function object
    """
    x1, x2 = 0, 0
    results = TimeSeries()
    results[0] = x1 + x2
    
    for t in linrange(0, system.duration):
        x1, x2 = update_func(x1, x2, t, system)
        results[t+1] = x1 + x2

    return results


# -

# Test your functions by running a simulation with a single value of `lam`.

# +
# Solution

system = make_system(lam, mu)
run_simulation(system, update_func3)
plot(results)
decorate(xlabel='Time (min)', ylabel='Customers')
compute_metrics(results, system)
# -

# Sweep a range of values for `lam`, plot the results, and print the average wait time across all values of `lam`.
#
# How do the results compare to the scenario with two servers and one queue.

# +
# Solution

sweep = sweep_lam(lam_array, mu, update_func3)
W_avg = sweep.mean()
print('Average of averages = ', W_avg, 'minutes')

# +
# Solution

plot(sweep, 'bo')
decorate(xlabel='Arrival late, lambda (per min)',
         ylabel='Average time in system',
         title='Multiple server, multiple queue')

# +
# Solution

"""
With two queues, the average of averages is slightly higher, most of the time.  But the difference is small.

The two configurations are equally good as long as both servers are busy; the only time two lines is worse is if one queue is empty and the other contains more than one customer.  In real life, if we allow customers to change lanes, that disadvantage can be eliminated.

From a theoretical point of view, one line is better.  From a practical point of view, the difference is small and can be mitigated.  So the best choice depends on practical considerations.

On the other hand, you can do substantially better with an express line for customers with short service times.  But that's a topic for another notebook.
""";
# -


