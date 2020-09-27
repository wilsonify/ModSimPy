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
# Chapter 9
#
# Copyright 2017 Allen Downey
#
# License: [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0)
#

# +
# import everything from SymPy.
from sympy import *

# Set up Jupyter notebook to display math.
init_printing() 
# -

# The following displays SymPy expressions and provides the option of showing results in LaTeX format.

# +
from sympy.printing import latex

def show(expr, show_latex=False):
    """Display a SymPy expression.
    
    expr: SymPy expression
    show_latex: boolean
    """
    if show_latex:
        print(latex(expr))
    return expr


# -

# ### Analysis with SymPy

# Create a symbol for time.

t = symbols('t')
t

# If you combine symbols and numbers, you get symbolic expressions.

expr = t + 1
expr

# The result is an `Add` object, which just represents the sum without trying to compute it.

type(expr)

# `subs` can be used to replace a symbol with a number, which allows the addition to proceed.

expr.subs(t, 2)

# `f` is a special class of symbol that represents a function.

f = Function('f')
f

# The type of `f` is `UndefinedFunction`

type(f)

# SymPy understands that `f(t)` means `f` evaluated at `t`, but it doesn't try to evaluate it yet.

f(t)

# `diff` returns a `Derivative` object that represents the time derivative of `f`

dfdt = diff(f(t), t)
dfdt

type(dfdt)

# We need a symbol for `alpha`

alpha = symbols('alpha')
alpha

# Now we can write the differential equation for proportional growth.

eq1 = Eq(dfdt, alpha*f(t))
eq1

# And use `dsolve` to solve it.  The result is the general solution.

solution_eq = dsolve(eq1)
solution_eq

# We can tell it's a general solution because it contains an unspecified constant, `C1`.
#
# In this example, finding the particular solution is easy: we just replace `C1` with `p_0`

C1, p_0 = symbols('C1 p_0')

particular = solution_eq.subs(C1, p_0)
particular

# In the next example, we have to work a little harder to find the particular solution.

# ### Solving the quadratic growth equation 
#
# We'll use the (r, K) parameterization, so we'll need two more symbols:

r, K = symbols('r K')

# Now we can write the differential equation.

eq2 = Eq(diff(f(t), t), r * f(t) * (1 - f(t)/K))
eq2

# And solve it.

solution_eq = dsolve(eq2)
solution_eq

# The result, `solution_eq`, contains `rhs`, which is the right-hand side of the solution.

general = solution_eq.rhs
general

# We can evaluate the right-hand side at $t=0$

at_0 = general.subs(t, 0)
at_0

# Now we want to find the value of `C1` that makes `f(0) = p_0`.
#
# So we'll create the equation `at_0 = p_0` and solve for `C1`.  Because this is just an algebraic identity, not a differential equation, we use `solve`, not `dsolve`.
#
# The result from `solve` is a list of solutions.  In this case, [we have reason to expect only one solution](https://en.wikipedia.org/wiki/Picard%E2%80%93Lindel%C3%B6f_theorem), but we still get a list, so we have to use the bracket operator, `[0]`, to select the first one.

solutions = solve(Eq(at_0, p_0), C1)
type(solutions), len(solutions)

value_of_C1 = solutions[0]
value_of_C1

# Now in the general solution, we want to replace `C1` with the value of `C1` we just figured out.

particular = general.subs(C1, value_of_C1)
particular

# The result is complicated, but SymPy provides a method that tries to simplify it.

particular = simplify(particular)
particular

# Often simplicity is in the eye of the beholder, but that's about as simple as this expression gets.
#
# Just to double-check, we can evaluate it at `t=0` and confirm that we get `p_0`

particular.subs(t, 0)

# This solution is called the [logistic function](https://en.wikipedia.org/wiki/Population_growth#Logistic_equation).
#
# In some places you'll see it written in a different form:
#
# $f(t) = \frac{K}{1 + A e^{-rt}}$
#
# where $A = (K - p_0) / p_0$.
#
# We can use SymPy to confirm that these two forms are equivalent.  First we represent the alternative version of the logistic function:

A = (K - p_0) / p_0
A

logistic = K / (1 + A * exp(-r*t))
logistic

# To see whether two expressions are equivalent, we can check whether their difference simplifies to 0.

simplify(particular - logistic)

# This test only works one way: if SymPy says the difference reduces to 0, the expressions are definitely equivalent (and not just numerically close).
#
# But if SymPy can't find a way to simplify the result to 0, that doesn't necessarily mean there isn't one.  Testing whether two expressions are equivalent is a surprisingly hard problem; in fact, there is no algorithm that can solve it in general.

# ### Exercises
#
# **Exercise:** Solve the quadratic growth equation using the alternative parameterization
#
# $\frac{df(t)}{dt} = \alpha f(t) + \beta f^2(t) $

# +
# Solution

alpha, beta = symbols('alpha beta')

# +
# Solution

eq3 = Eq(diff(f(t), t), alpha*f(t) + beta*f(t)**2)
eq3

# +
# Solution

solution_eq = dsolve(eq3)
solution_eq

# +
# Solution

general = solution_eq.rhs
general

# +
# Solution

at_0 = general.subs(t, 0)

# +
# Solution

solutions = solve(Eq(at_0, p_0), C1)
value_of_C1 = solutions[0]
value_of_C1

# +
# Solution

particular = general.subs(C1, value_of_C1)
particular.simplify()
# -

# **Exercise:**  Use [WolframAlpha](https://www.wolframalpha.com/) to solve the quadratic growth model, using either or both forms of parameterization:
#
#     df(t) / dt = alpha f(t) + beta f(t)^2
#
# or
#
#     df(t) / dt = r f(t) (1 - f(t)/K)
#
# Find the general solution and also the particular solution where `f(0) = p_0`.


