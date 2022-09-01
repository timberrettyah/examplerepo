import random
from typing import Any, List

import numpy as np
import pandas as pd
from statsmodels.tsa.arima_process import arma_generate_sample


def simulate_seasonal_flow(timerange: int, frequencies: List, amplitudes: List) -> List:
    """
    This function simulates a seasonal flow using a summation of fourier terms.

    Parameters:

    Timerange: total timespan for which the timeseries needs to be created
    Frequencies: Frequencies for the different foerier terms.
    Amplitudes: Amplitudes for the different foerier terms.
    """

    # Create a timerange for the simulated data
    ts = 1 / timerange
    time = np.arange(0, 1, ts)

    # Create the first foerier term
    seasonality = amplitudes[0] * np.sin(2 * np.pi * frequencies[0] * time)

    # Create and summate rest of the Fourier terms
    if len(frequencies) > 1:
        for i in range(1, len(frequencies)):
            print(i)
            print("frequency: ", frequencies[i])
            seasonality += amplitudes[i] * np.sin(2 * np.pi * frequencies[i] * time)
            seasonality = seasonality.round(4)

    # Adjust minimum level of seasonality to 0 and round value to 4 digits
    level = seasonality.min()
    seasonality = seasonality - level
    seasonality = [round(value, 4) for value in seasonality]

    return seasonality


def random_integer(frequency: float) -> float:
    """
    This function creates a random integer with either the value 0 or 1.
    With the frequency parameter you can set can control the occurrence of the 1 value.

    Parameters:

    frequency: the occurrence of the 1 value.

    """

    probability = random.uniform(0, 1)

    integer = 0

    if probability <= frequency:
        integer = 1

    return float(integer)


def simulate_promotion(
    timerange: int, fullyear: int, sales_total: List, promotion_uplift_perc: float, promotion_frequency: int
) -> tuple:
    """
    This function simulates a promotion dummy. This dummy has either the value or 1
    for each of the time units in the simulated dataset.

    Parameters:


    timerange: Number of time units in the entire dataset.
    fullyear: Number of time units in a single year.
    y_total: value of the normal sales for each time unit.
    promotion_uplift: uplift for the time units in which there is a promotion
    promotion_frequency: the frequency at which there is a promotion
    """

    # Simulate list with indication for occurence of promotion
    promotion_timing = [random_integer(promotion_frequency / fullyear) for i in range(0, timerange)]

    # Create list with promotion uplift when a promotion takes place
    promotion_uplift_abs = [value * promotion_uplift_perc + 1 for value in promotion_timing]

    # Create list with sales including the promotion uplift
    sales_total_series = pd.Series(sales_total) * pd.Series(promotion_uplift_abs)
    sales_total = sales_total_series.to_list()

    return (sales_total, promotion_timing)


def simulate_arma(
    timerange: int, arparams: np.array, maparams: np.array, scale: float, seed: Any = None
) -> List:
    """
    This function simulates an arma effects within the simulated timeseries.

    Parameters:

    timerange: Number of time units in the entire dataset.
    arparams: parameters for the autocorrelations.
    maparams: parameters for the moving averages.
    scale: standard deviation of the white nois error term.
    """

    # Set seed
    if seed is not None:
        np.random.seed(seed)
        print("Seed: ", seed)

    # Simulate ARMA process
    ar = np.r_[1, -arparams]  # add zero-lag and negate
    ma = np.r_[1, maparams]  # add zero-lag
    z_arma = arma_generate_sample(ar, ma, timerange, scale=scale)

    # Round values arma process to 4 digits
    z_arma = [round(datapoint, 4) for datapoint in z_arma]

    return z_arma


def simulate_timeseries(
    timerange: int,
    fullyear: int,
    frequencies: List,
    amplitudes: List,
    arparams: np.array,
    maparams: np.array,
    scale: float,
    promotion: bool = False,
    promotion_uplift: Any = None,
    promotion_frequency: Any = None,
    seed: Any = None,
) -> pd.DataFrame:
    """
    This function simulates a sales timeseries with the possibility of
    seasonality and arma effects.

    Parameters:


    timerange: total timespan for which the timeseries needs to be created
    fullyear: Number of time units in a single year.
    frequencies: Frequencies for the different foerier terms.
    amplitudes: Amplitudes for the different foerier terms.
    arparams: parameters for the autocorrelations.
    maparams: parameters for the moving averages.
    scale: standard deviation of the white nois error term.
    promotion: boolean that indictes whether promotion effects need to be modeled as well.
    promotion_uplift: size of the promotional uplift.
    promotion_frequency: frequency at which the promotions occur.
    seed: fixed seed for the random sampling elements.
    Helps ensuring the simulation gives the same outcome for each run.
    """

    # Take two full years as a period for thinning the sampled data.
    thinning = fullyear * 2
    simulationrange = timerange + thinning

    # Simulated the arma effects
    sales_arma = simulate_arma(
        timerange=simulationrange, arparams=arparams, maparams=maparams, scale=scale, seed=seed
    )

    # Simulated the seasonal flow
    seasonality = simulate_seasonal_flow(timerange=fullyear, frequencies=frequencies, amplitudes=amplitudes)
    y = seasonality

    # Create the sales timeseries
    for i in range(fullyear, simulationrange):
        y.append(y[i - fullyear] + sales_arma[i])

    # Add the promotional effect
    if promotion is True:
        (sales_total, promotion_timing) = simulate_promotion(
            timerange=simulationrange,
            fullyear=fullyear,
            sales_total=y,
            promotion_uplift_perc=promotion_uplift,
            promotion_frequency=promotion_frequency,
        )

    # Add placeholders for the promotional effects
    if promotion is False:
        sales_total = y
        promotion_timing = [0 for day in range(0, simulationrange)]

    # Use the thinning for the dataset
    sales_total = sales_total[thinning:simulationrange]
    promotion_timing = promotion_timing[thinning:simulationrange]
    sales_arma = sales_arma[thinning:simulationrange]
    time = [day for day in range(1, timerange + 1)]

    print(len(sales_total), len(sales_arma), len(time))

    # Combine data in dataframe
    timeseries_dataset = pd.DataFrame(
        {
            "time": time,
            "sales_total": sales_total,
            "sales_arma": sales_arma,
            "promotion_timing": promotion_timing,
        }
    )

    # Downcast the timeseries to float32
    timeseries_dataset["sales_total"] = pd.to_numeric(timeseries_dataset["sales_total"], downcast="float")
    timeseries_dataset["sales_arma"] = pd.to_numeric(timeseries_dataset["sales_arma"], downcast="float")
    timeseries_dataset["promotion_timing"] = pd.to_numeric(
        timeseries_dataset["promotion_timing"], downcast="float"
    )

    timeseries_dataset = timeseries_dataset.set_index("time")

    return timeseries_dataset
