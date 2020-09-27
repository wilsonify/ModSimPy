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
import numpy as np

from sympy import *

init_printing()
# -

# This notebook uses SymPy to derive the equations of motion for a springy pendulum and a rigid pendulum.
#
# Here are the symbols we need:

x, y, vx, vy, ax, ay = symbols('x, y, vx, vy, ax, ay')
length0, k, m, g, R, t = symbols('length0, k, m, g, R, t')

# We'll use vectors P, V, and A to represent position, velocity and acceleration.  The Vector class in modsim.py doesn't play nicely with SymPy, so I'll use NumPy arrays instead:

P = np.array([x, y])
P

V = np.array([vx, vy])
V

A = np.array([ax, ay])
A


# The only vector operations we need are `mag` and `hat`:

def mag(P):
    return sqrt(P[0]**2 + P[1]**2)


#

mag(P)


def hat(P):
    return P / mag(P)


hat(P)

# For convenience, I'll define intermediate variables like length:

length = mag(P)
length

# `f_spring` is the force on the particle due to the spring

f_spring = -k * (length - length0) * hat(P)
f_spring

# xhat and yhat are unit vectors along the x and y axes: 

xhat = np.array([1, 0])
yhat = np.array([0, 1])

# Now I can write force due to gravity as a Vector

f_grav = -m * g * yhat
f_grav

# To write $\sum F = ma$, I'll define the left-hand side and right-hand sides of the equations separately.

lhs = f_spring + f_grav

rhs = m * A

# Now I can make two equations, one for each component of F and A:

eq1 = Eq(lhs[0], rhs[0])
eq1

eq2 = Eq(lhs[1], rhs[1])
eq2

# Now I want equations that are explicit in ax and ay.  In this case I can get them easily by dividing through by m.  But for the rigid pendulum we will need to use solve, so I want to demonstrate that here.

soln = solve([eq1, eq2], [ax, ay])

# Now we can extract the expressions for ax and ay

soln[ax]

soln[ay]

# And we can get SymPy to format the result for LaTeX:

print(latex(soln[ax]))

print(latex(soln[ay]))

# Or generate Python code we can paste into a slope function:

print(python(soln[ax]))

print(python(soln[ay]))

# To see these equations run, see pendulum.ipynb

# ### Rigid pendulum

# Solving the rigid pendulum is almost the same, except we need a third equation to represent the geometric constraint.  The simplest form of the constraint is:
#
# $ x^2 + y ^2 = length$
#
# But this equation doesn't involve vx, vy, ax, and ay, so it's not much help.  However, if we take the time derivative of both sides, we get
#
# $ 2 x vx + 2 y vy = 0 $
#
# And if we take the time derivative one more time (and divide through by 2), we get
#
# $ x ax + y ay + vx^2 + vy^2 = 0 $
#
# And that's just what we need.

eq3 = Eq(x*ax + y*ay + vx**2 + vy**2, 0)
eq3

# Now we can represent the force due to tension as a vector with unknown magnitude, R, and direction opposite P. 

f_tension = -R * hat(P)

# Again, we can write $\sum F = ma$

lhs = f_grav + f_tension

rhs = m * A

# And make one equation for each dimension:

eq4 = Eq(lhs[0], rhs[0])
eq4

#

eq5 = Eq(lhs[1], rhs[1])
eq5

# Now we have three equations in three unknowns:

soln = solve([eq3, eq4, eq5], [ax, ay, R])

# And we can get explicit expressions for ax and ay

soln[ax]

#

soln[ay]

# Again, we can get the results in LaTeX or Python.

print(latex(soln[ax]))

print(latex(soln[ay]))

# To see these equations run, see pendulum2.ipynb

print(python(soln[ax]))

print(python(soln[ay]))


