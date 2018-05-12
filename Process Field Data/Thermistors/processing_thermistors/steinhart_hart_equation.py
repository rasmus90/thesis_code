"""
Title: 	Steinhart Hart Equation
Author: Rasmus Nes Tjoerstad
Info:	Compute coefficients for the equation.
"""

import numpy as np


def steinhart_hart_coefficients(t0, t1, t2, r0, r1, r2):
    a = np.array([[1, np.log(r0), (np.log(r0))**3], [1, np.log(r1), (np.log(r1))**3],[1, np.log(r2), (np.log(r2))**3]])
    b = np.array([[t0**-1], [t1**-1], [t2**-1]])
    x = np.linalg.solve(a, b)
    return x


def steinhart_hart_temperature(A, B, C, r):
    return (1/(A + B*np.log(r) + C*(np.log(r))**3))-273.15


k = 273.15
t0 = -10+k
r0 = 47428
t1 = k
r1 = 29278.
t2 = 5+k
r2 = 23311.
x = steinhart_hart_coefficients(t0, t1, t2, r0, r1, r2)
a = x[0]
b = x[1]
c = x[2]
