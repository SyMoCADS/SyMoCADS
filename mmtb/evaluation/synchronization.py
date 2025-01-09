import numpy as np
from abc import ABC, abstractmethod
from scipy.stats import norm
from typing import Sequence, Optional
from math import floor
from collections import deque

from ..dtypes import *

class TransmissonStartDetection:

    def __init__(self, training_data_length: float,
                 false_alarm_probaility: float):

        self._training_data_length = training_data_length
        self._false_alarm_probaility = false_alarm_probaility
        self._training_sample_vals = np.zeros(training_data_length)

        self._threshold = None
        self._sample_counter = 0
        self._detected_transmission_start = False

    def __call__(self, sample_val: float) -> bool:
        if self._detected_transmission_start:
            return True

        self._training_sample_vals[self._sample_counter] = sample_val
        self._sample_counter += 1

        if self._threshold is not None and sample_val <= self._threshold:
            self._detected_transmission_start = True
            return True

        if self._sample_counter == self._training_data_length:
            mean = np.mean(self._training_sample_vals)
            std = np.std(self._training_sample_vals)
            self._threshold = norm.ppf(self._false_alarm_probaility,
                                       loc=mean,
                                       scale=std)
            self._sample_counter = 0

        return False

    def enough_training_samples(self) -> bool:
        if self._threshold is None:
            return False
        else:
            return True


class SynchronizationBase(ABC):

    def __init__(
        self,
        t_sample: float,
        t_symbol: float,
        filter_vals: Sequence[float],
        search_radius: float,
        n_symbols: int,
        sync_data: Optional[SynchronizationData] = None,
        static_sync_n_avg: Optional[int] = None,
    ) -> None:

        self._static_sync_n_avg = static_sync_n_avg
        self._metric_buffer = None

        if self._static_sync_n_avg is not None:
            if self._static_sync_n_avg <= 0:
                raise ValueError()
            else:
                self._sync_time_buffer = list()
                self._metric_buffer = DataPointList(times=[], values=[])
                self._detec_metric_buffer = list()
                self._first_avg_sync_time = None

        self._search_radius = search_radius
        self._sync_data = sync_data
        self._n_symbols = n_symbols
        self._t_symbol = t_symbol

        self._filter_vals = filter_vals
        self._filter_len = len(filter_vals)
        self._lower_search_distance = (1 - self._search_radius) * t_symbol
        self._upper_search_distance = (1 + self._search_radius) * t_symbol
        self._half_symbol_len = floor(t_symbol / (2 * t_sample))
        self._observation_interval_length = floor(
            (2 * search_radius * t_symbol) / t_sample)

        self._metric_coeffs = deque(maxlen=2 * self._half_symbol_len)
        self._metric_times = deque(maxlen=2 * self._half_symbol_len)
        self._detection_sample = deque(maxlen=2 * self._half_symbol_len)

        self._sample_vals = deque(maxlen=self._filter_len)
        self._sample_times = deque(maxlen=self._filter_len)

        self._symbol_counter = 0

        self._enough_samples = False
        self._first_symbol = True

        self._counter = 0
        self._threshold = None
        self._transmission_start_time = None

    @abstractmethod
    def _eval_func(self, sample_values: float) -> float:
        pass

    @abstractmethod
    def _aggregation_func(self, samples: Sequence[float]) -> int:
        pass

    def set_transmission_start(self, transmission_start_time: float) -> None:
        if self._transmission_start_time is not None:
            return

        self._transmission_start_time = transmission_start_time

    def _symbol_by_symbol_sync(self) -> Optional[DataPoint]:
        if self._symbol_counter == 0:

            if self._metric_times[
                    -1] < self._transmission_start_time + self._t_symbol / 2:
                return

            max_index = self._aggregation_func(self._metric_coeffs)
            self._symbol_counter += 1
            self._last_symbol_start = self._metric_times[max_index]
            ret = DataPoint(time=self._metric_times[max_index],
                            value=self._metric_coeffs[max_index])

            self._metric_coeffs = deque(
                maxlen=self._observation_interval_length)
            self._metric_times = deque(
                maxlen=self._observation_interval_length)
            self._detection_sample = deque(
                maxlen=self._observation_interval_length)

            return ret
        else:
            if (self._metric_times[0] - self._last_symbol_start
                    < self._lower_search_distance):
                return None

            try:
                idx = np.where(
                    np.array(self._metric_times) > self._last_symbol_start +
                    self._upper_search_distance)[0][0]
                metric_times_array = np.array(self._metric_coeffs)
                max_index = self._aggregation_func(metric_times_array[:idx])
            except IndexError:
                max_index = self._aggregation_func(self._metric_coeffs)

            self._symbol_counter += 1
            self._last_symbol_start = self._metric_times[max_index]

            return DataPoint(time=self._metric_times[max_index],
                             value=self._metric_coeffs[max_index])

    def _static_sync(self) -> Optional[DataPoint]:
        if self._symbol_counter < self._static_sync_n_avg:
            ret = self._symbol_by_symbol_sync()

            if ret is not None:
                self._sync_time_buffer.append(ret.time)

            return None

        if self._first_avg_sync_time is None:
            self._first_avg_sync_time = np.mean(
                np.array(self._sync_time_buffer) -
                (np.arange(self._static_sync_n_avg) * self._t_symbol))
            del self._sync_time_buffer

        if self._metric_buffer is not None:
            if self._metric_buffer[-1].time < (
                    self._symbol_counter - 1
            ) * self._t_symbol + self._first_avg_sync_time + self._upper_search_distance:
                return None
            else:
                for symbol_index in range(self._static_sync_n_avg):
                    print(symbol_index)
                    lower_index = np.where(
                        self._metric_buffer.times >= symbol_index *
                        self._t_symbol + self._first_avg_sync_time -
                        self._lower_search_distance)[0][0]
                    upper_index = np.where(
                        self._metric_buffer.times > symbol_index *
                        self._t_symbol + self._first_avg_sync_time +
                        self._upper_search_distance)[0][0]
                    max_index = self._aggregation_func(
                        self._metric_buffer.values[lower_index:upper_index])
                    self._detec_metric_buffer.append(
                        self._metric_buffer[max_index + lower_index])

                self._metric_buffer = None
        else:
            self._last_symbol_start = (
                self._symbol_counter -
                1) * self._t_symbol + self._first_avg_sync_time
            detection_sample = self._symbol_by_symbol_sync()
            self._detec_metric_buffer.append(detection_sample)

        if len(self._detec_metric_buffer) > 0:
            ret = self._detec_metric_buffer[0]
            self._detec_metric_buffer.pop(0)
            return ret
        else:
            return None

    def __call__(self, new_sample: DataPoint) -> Optional[DataPoint]:
        if self._symbol_counter >= self._n_symbols:
            return None

        self._sample_vals.append(new_sample.value)
        self._sample_times.append(new_sample.time)

        if not self._enough_samples:
            if len(self._sample_vals) < self._filter_len:
                return None
            self._enough_samples = True

        corr_coeff = self._eval_func(self._sample_vals)
        self._metric_coeffs.append(corr_coeff)
        self._metric_times.append(self._sample_times[0])

        if self._sync_data is not None:
            self._sync_data.append_metric_coeff(
                DataPoint(time=self._sample_times[0],
                          value=self._metric_coeffs[-1]))

        if self._metric_buffer is not None:
            self._metric_buffer.append(
                DataPoint(time=self._sample_times[0],
                          value=self._metric_coeffs[-1]))

        if self._transmission_start_time is None:
            return None

        if self._static_sync_n_avg is None:
            ret = self._symbol_by_symbol_sync()
        else:
            ret = self._static_sync()

        if ret is not None and self._sync_data is not None:
            self._sync_data.append_detection_metric_coeff(ret)

        return ret

    def get_sync_data(self) -> Optional[SynchronizationData]:
        return self._sync_data


class CorrelationSynchronization(SynchronizationBase):

    def __init__(
        self,
        t_sample: float,
        t_symbol: float,
        filter_vals: Sequence[float],
        search_radius: float,
        n_symbols: int,
        sync_data: SynchronizationData = None,
        static_sync_n_avg: Optional[int] = None,
    ) -> None:

        super().__init__(t_sample, t_symbol, filter_vals, search_radius,
                         n_symbols, sync_data, static_sync_n_avg)

    def _eval_func(self, sample_values: Sequence[float]) -> float:
        return np.correlate(self._filter_vals,
                            1 - np.array(sample_values),
                            mode="valid")[0]

    def _aggregation_func(self, samples: Sequence[float]) -> int:
        return np.argmax(samples)


class DifferentialCorrelationSynchronization(SynchronizationBase):

    def __init__(
        self,
        t_sample: float,
        t_symbol: float,
        filter_vals: Sequence[float],
        search_radius: float,
        n_symbols: int,
        sync_data: SynchronizationData = None,
        static_sync_n_avg: Optional[int] = None,
    ) -> None:

        super().__init__(t_sample, t_symbol, filter_vals, search_radius,
                         n_symbols, sync_data, static_sync_n_avg)

        self._filter_len += 1
        self._sample_vals = deque(maxlen=self._filter_len)
        self._sample_times = deque(maxlen=self._filter_len)

    def _eval_func(self, sample_values: Sequence[float]) -> float:
        return np.correlate(self._filter_vals,
                            np.diff(sample_values),
                            mode="valid")[0]

    def _aggregation_func(self, samples: Sequence[float]) -> int:
        return np.argmax(samples)
