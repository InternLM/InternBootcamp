import numpy as np


def cost_analysis(thickness, D, B1, bolt_count_edit, L, Density, price):
    return np.pi * thickness * ((D**2 - B1**2) - bolt_count_edit * L**2) * 1e-9 * Density * price
    