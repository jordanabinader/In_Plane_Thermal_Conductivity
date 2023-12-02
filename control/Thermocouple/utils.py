import numpy as np
import pandas as pd
from scipy.optimize import curve_fit


# Define the model function
def sinusoidal_model(x, b0, b1, b2, TempFrequency):
    return b0 + b1 * np.sin(2 * np.pi * TempFrequency * (x + b2))


# Non-linear fitting
def fit_data(temps, times, TempFrequency):
    x_data = times

    y_data = temps

    if len(x_data) != len(y_data) or len(x_data) == 0 or len(y_data) == 0:
        raise ValueError("x_data and y_data must have the same length")
    if len(x_data) == 0:
        raise ValueError("x_data cannot have 0 length")
    if len(y_data) == 0:
        raise ValueError("y_data cannot have 0 length")

    # initial guess
    p0 = [np.mean(y_data), np.max(y_data) - np.mean(y_data), np.pi]

    if len(p0) != 3:  # Assuming your model has 3 parameters
        raise ValueError("Initial parameter vector p0 must have length 3")

    # Define a lambda function to pass TempFrequency as an additional parameter
    model_func = lambda x, a, b, phi: sinusoidal_model(x, a, b, phi, TempFrequency)

    try:
        popt, _ = curve_fit(model_func, x_data, y_data, p0=p0)  # fit the model
    except Exception as e:
        raise RuntimeError(f"Curve fitting failed with error: {str(e)}")

    # Predicted y_data
    y_pred = model_func(x_data, *popt)

    # Calculate R squared
    residuals = y_data - y_pred
    ss_res = np.sum(residuals ** 2)
    ss_tot = np.sum((y_data - np.mean(y_data)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)

    # Calculate the adjusted R-squared
    n = len(x_data)
    p = len(p0)
    adjusted_r_squared = 1 - (1 - r_squared) * ((n - 1) / (n - p - 1))

    return popt, adjusted_r_squared


def process_data(lst, sampling_rate, temp_frequency):
    if temp_frequency != 0:
        window_size = int(min((sampling_rate // temp_frequency)*2, len(lst)))  # TODO is this better/fine as 2x period?
    else:
        window_size = int(len(lst))

    # print(sampling_rate // temp_frequency)
    # print(len(lst)/2)
    # print(window_size)
    if (len(lst) > 5):
        column_series = pd.Series(lst)
        moving_avg = column_series.rolling(window=window_size, min_periods=1, center=True).mean()
        lst = list(column_series - moving_avg)

    return lst


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # Trim white spaces from column names
    df.columns = df.columns.str.strip()

    # Drop rows with any NaN values
    df_cleaned = df.dropna()

    return df_cleaned
