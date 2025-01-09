import os
import json
import numpy as np
from pathlib import Path
import statsmodels.api as sm

from ..dtypes import *

def blind_filter(t_sample: float, t_symbol: float, t_irradiation: float):
    def filter_func(t):
        if t < 0 or t > t_symbol:
            return 0
        elif t <= t_irradiation:
            return t - t**2 / (2 * t_irradiation)
        else:
            return (
                0.5
                * t_irradiation
                * (t**2 - 2 * t * t_symbol + t_symbol**2)
                / (t_symbol - t_irradiation) ** 2
            )

    ret = np.vectorize(filter_func)(np.arange(0, t_symbol, t_sample))
    return ret


def blind_diff_filter(t_sample: float, t_symbol: float, t_irradiation: float) -> np.array:
    def filter_func(t):
        if t < 0 or t > t_symbol:
            return 0
        elif t <= t_irradiation:
            return t / t_irradiation - 1
        else:
            return (t_symbol - t) / (t_symbol - t_irradiation)

    ret = np.vectorize(filter_func)(np.arange(0, t_symbol, t_sample))
    return ret

def smoothed_filter(t_sample: float, t_symbol: float, t_irradiation: float, dis_tx_rx: float, fraction_used_data: float = 0.2) -> np.array:
    dis_key = "distance = " + str(float(dis_tx_rx)) + "cm"
    t_sample_key = "t_sample = " + str(float(t_sample)) + "s"
    t_impulse_key = "t_impulse = " + str(float(t_irradiation)) + "s"

    with open(os.path.join(Path(__file__).parent,"filters.json"), 'r') as f:
        json_dict = json.load(f)

    try:
        filter_vals = json_dict[dis_key][t_sample_key][t_impulse_key]
    except KeyError:
        raise KeyError("Filter values corresponding to the input parameter couldn't be found.")

    start_idx = np.argmax(np.correlate(-np.diff(filter_vals), np.ones(int(np.ceil( t_irradiation / t_sample)))))
    filter_vals = np.array(filter_vals[start_idx : start_idx + int(np.ceil( t_symbol / t_sample))])
    filter_vals = filter_vals - np.max(filter_vals) + 1

    filter_vals = sm.nonparametric.lowess(
            exog=t_sample * np.arange(0, len(filter_vals)),
            endog=filter_vals,
            is_sorted=True,
            return_sorted=False,
            frac=fraction_used_data,
        )
    
    return np.array(filter_vals)

def smoothed_diff_filter(t_sample: float, t_symbol: float, t_irradiation: float, dis_tx_rx: float, fraction_used_data: float = 0.2) -> np.array:
    dis_key = "distance = " + str(float(dis_tx_rx)) + "cm"
    t_sample_key = "t_sample = " + str(float(t_sample)) + "s"
    t_impulse_key = "t_impulse = " + str(float(t_irradiation)) + "s"

    with open(os.path.join(os.path.join(Path(__file__).parent,"filters.json"),"filters.json"), 'r') as f:
        json_dict = json.load(f)

    try:
        filter_vals = json_dict[dis_key][t_sample_key][t_impulse_key]
    except KeyError:
        raise KeyError("Filter values corresponding to the input parameter couldn't be found.")
    
    filter_vals = np.diff(filter_vals)
    
    start_idx = np.argmax(np.correlate(-filter_vals, np.ones(int(np.ceil( t_irradiation / t_sample)))))
    filter_vals = np.array(filter_vals[start_idx : start_idx + int(np.ceil( t_symbol / t_sample))])

    filter_vals = sm.nonparametric.lowess(
            exog=t_sample * np.arange(0, len(filter_vals)),
            endog=filter_vals,
            is_sorted=True,
            return_sorted=False,
            frac=fraction_used_data,
    )
    
    return np.array(filter_vals)
