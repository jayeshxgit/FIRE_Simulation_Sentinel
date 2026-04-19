import numpy as np


def evolve(grid, wind, slope, fuel, weights, firebreaks=None):
    """
    Evolve the fire grid by one time step using cellular automata rules.

    States:
        0 = Unburned
        1 = Burning
        2 = Burned

    Args:
        weights: dict with keys 'base', 'wind', 'slope', 'fuel'
        firebreaks: optional boolean mask (True = firebreak cell, blocks spread)
    """
    new_grid = grid.copy()
    rows, cols = grid.shape

    for i in range(1, rows - 1):
        for j in range(1, cols - 1):
            if grid[i, j] == 1:  # currently burning
                new_grid[i, j] = 2  # becomes burned
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        ni, nj = i + di, j + dj
                        if firebreaks is not None and firebreaks[ni, nj]:
                            continue
                        if grid[ni, nj] == 0:
                            prob = fire_probability(
                                wind[ni, nj], slope[ni, nj], fuel[ni, nj], weights
                            )
                            if np.random.rand() < prob:
                                new_grid[ni, nj] = 1
    return new_grid


def fire_probability(wind_val, slope_val, fuel_val, weights):
    """Calculate the probability of fire spreading to a cell."""
    prob = (
        weights["base"]
        + weights["wind"]  * wind_val
        + weights["slope"] * slope_val
        + weights["fuel"]  * fuel_val
    )
    return np.clip(prob, 0.0, 1.0)


def run_simulation(initial_grid, wind, slope, fuel, iterations, weights, firebreaks=None):
    """Run the simulation for a given number of iterations, returning all frames."""
    frames = [initial_grid.copy()]
    current_grid = initial_grid.copy()
    for _ in range(iterations):
        current_grid = evolve(current_grid, wind, slope, fuel, weights, firebreaks)
        frames.append(current_grid.copy())
    return frames
