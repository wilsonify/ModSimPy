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

# # Hey friends. #
#
# Variables r weird. Shift+Enter if you agree.
#
# by Jane Sieving

from modsim import System
# If this doesn't work, move this file into your /code folder.
# It needs to be in the same folder as modsim.py.

# Let's write a function, like they do in ModSim notebooks all the time. We'll give it some parameters just to make it feel important.

def func1(input1, input2):
    print("Input 1 = ", input1)
    print("Input 2 = ", input2)
    output = input1 + input2
    print("Output = ", output)


func1(1, 2.5)

# All it does is add two numbers and print a lot of stuff. Printing is fun, let's do it some more.

print(output)

# Well, shucks. That didn't work. `output` isn't defined? But we defined it in that super technical function!
# You can try printing `input1` or `input2` as well, and you'll probably see the same error.

output = 5
print(output)

# So, output was defined in the function, but doesn't exist outside of the function executing. What happens if you run the function again and print output?

func1(1, 2.5) # will print input1, input2, and output
print("Output also =", output)


# What? There are 2 versions of `output`? Well ya see, this is where we come to **global** and **local** variables. Local variables only exist within a function or class* that is using them (they are temporary for a function/specific to a class). Global variables can be accessed by any function or class.
#
# When you create `output` in `func1` (and when you pass in values for `input1` and `input2`) those are local variables that only `func1` "knows" about. When you assign a value to output outside of `func1`, that is a global variable that you can access any time.
#
# \**Classes are pre-defined or user-defined objects that have different methods and parmeters. TimeSeries, Series, State and System are all classes defined in the modsim.py library.*

def func2(input1, input2):
    print("Input 1 = ", input1)
    print("Input 2 = ", input2)
    print("Output = ", output) # this will be the global value from earlier, since it's not locally computed


func1(1, 2.5)
func2(1, 2.5)


# Here we're running two similar functions one after another, and they print their results one after another.
# The only difference between the functions is that one computes a value for `output` locally, and the other just prints `output`.
#
# `func2` accesses the global version of `output` because it has no other option.* `func1` accesses the local variable `output` because local variables override global values with the same name.
#
# \**This isn't universally true, in some languages/cases you have to declare a variable as global for it to be accessed anywhere.*
#
# Let's look at another example:

# +
def forgetful_func(input1, input2):
    print(input1, input2)
    
forgetful_func(1, 6)

print("Now we try to print those:")
print(input1, input2)


# -

# Why isn't the second `print` command (outside of the function) working? Because `input1` and `input2` still aren't global. We getting this? Good.
#
# Now let's do what the book does all the time:

def useful_func(input1, input2):
    print(input1 + input2)


useful_func(2, 3) # This should make sense. You pass in these parameters, they get used, they aren't stored after printing.

input1 = 1.5
input2 = 4
useful_func(input1, input2)

# Now, I dare you to do something w_i_l_d: change those variable names in the cell above. Change them to be all different. Change them to be all the same. How does the function care about your variable names?

cat = 5
dog = 10
useful_func(cat, dog)
useful_func(dog, dog)
useful_func(input2, dog)


# Cool, so that's inputs (mostly). What about outputs? That poor little small-town `output` variable wants to be a global star.
# This, friends, is why `return` is so gosh darn important.

def will_you_remember_me(thing1, thing2):
    new_thing = thing1 + thing2
    return new_thing


will_you_remember_me(3, 8)
print(new_thing)

# Foiled again! But we used `return` and everything! Well guess what, a return value that doesn't get assigned to anything is like a letter without an address (cue joke about The Twitter and snail mail implying that I'm old or something).
# To store a return value, you HAVE TO assign it to a variable OUTSIDE of the function.

I_will_remember_you = will_you_remember_me(6, 7)
print(I_will_remember_you)
# Please, never name things like this. Please.

# If you're lazy you can do this, but your variable will not be saved so be careful.
# It just feeds the output (return value) of your function to the input of print().

print(will_you_remember_me(5, 6))

# You can do the above as a shortcut, but remember that your return value will be LOST FOREVER after that.
#
# Like Jack at the end of *Titanic*.
#
# Think about the choices that you make.

# ## Keyword arguments ##
# Okay, I guess I should talk about keyword arguments and that whole `System(this=this, that=that)` nonsense you're seeing.
#
# So basically, a class (object) has a bunch of properties (attributes). Usually a given class will have specific attributes, but classes like `State` and `System` are set up to pretty much take any parameters you give them and accept them as attributes.

# +
solar_system = System(planets=8, central_mass="Sun")

print(solar_system.planets, solar_system.central_mass)

# +
other_system = System(planets=5, central_mass="Me")

print(other_system.planets, other_system.central_mass)

# +
friends = 1000
center_of_universe = " " # Type your name here?

personal_universe = System(friends=friends, 
                           center_of_universe=center_of_universe)

print(personal_universe.friends, 
      personal_universe.center_of_universe)
# -

# So, you've created two systems by directly setting parameters, and one by passing in premade variables. In the book those variables usually have the same name as their target, which obscures what's actually happening.

# +
apples = 1
bananas = 1
cherries = 7
grapes = 13

fruit_salad = System(a=apples, b=bananas, c=cherries, d=grapes)

print(fruit_salad.a, fruit_salad.b, fruit_salad.c, fruit_salad.d)
# -

print(fruit_salad.apples)

# Oh dear, did that last one fail? Of course it did, apples isn't an attribute of fruit_salad. You *can* print plain old apples, because it's global:

print(apples)

# You *can't* print plain old a, because that's an attribute of fruit_salad and isn't defined outside of that.

print(a)

# You can, however, do this:

global_a = fruit_salad.a # This is a name I chose, it doesn't 'make' the variable global.
print(global_a)

# And you could just as well call `global_a` something else, like `a`, and there would be a global variable `a` as well as a property `a`, and if you changed one the other would not be affected.

b = fruit_salad.b
b += 10
fruit_salad.b += 100
print(b, fruit_salad.b)

# So, when you type `bikeshare = System(this=this, that=that)`,
# the *left* parts are specific attributes of the System object, *local* to the system.
# The *right* parts are values you are *passing in*, which happen to already be defined as global variables with the same names.
#
# You're just telling a function or class to use the global value on the right, calling it by the name on the left.


