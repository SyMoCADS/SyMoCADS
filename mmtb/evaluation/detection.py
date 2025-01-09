from typing import Union, Optional, Sequence
from collections import deque
from abc import ABC, abstractmethod
import numpy as np

from ..dtypes import DetectionData, DataPoint


class DetectionBase(ABC):

    def __init__(self, detec_data: Optional[DetectionData], skip_n_symbols: int = 0) -> None:
        self._detec_data = detec_data
        self._skip_n_symbols = skip_n_symbols

    @abstractmethod
    def __call__(self, sample: Optional[DataPoint]) -> Optional[str]:
        pass


class ThresholdDetection(DetectionBase):

    def __init__(
        self,
        pilot_symbol_string: Sequence[str],
        symbol_map: dict[str, float],
        n_window: int,
        n_coherence: int,
        detec_data: Optional[DetectionData] = None,
        skip_n_symbols: int = 0,
    ) -> None:
        super().__init__(detec_data, skip_n_symbols)

        if n_coherence + len(pilot_symbol_string) - n_window < 0:
            raise ValueError(
                f"The detection parameters must fullfil the constraint:\n\tn_coherence + len(pilot_symbol_string) - n_window >= 0\ncurrently: {n_coherence} +  {len(pilot_symbol_string)} - {n_window} = {n_coherence+len(pilot_symbol_string)-n_window}"
            )

        if n_coherence == None:
            n_coherence = n_window

        self._n_pilots = len(pilot_symbol_string)
        self._n_window = n_window
        self._n_coherence = n_coherence

        self._symbol_map = symbol_map
        self._mod_order = len(symbol_map.keys())
        self._pilot_symbol_string = pilot_symbol_string

        self._threshold_vals = np.zeros(self._mod_order - 1)
        self._symbol_sample_map = {
            symbol: list()
            for symbol in self._symbol_map.keys()
        }
        self._sorted_symbol_map = sorted(self._symbol_map.keys(),
                                         key=lambda x: self._symbol_map[x])

        self._pilots_received = False
        self._sample_counter = 0

        for symbol in self._symbol_map.keys():
            if symbol not in self._pilot_symbol_string[skip_n_symbols:]:
                raise ValueError(
                    "No all possible symbols are included in the effective pilot sequence"
                )

        self._last_symbols = deque(maxlen=self._n_pilots -
                                   self._skip_n_symbols)
        self._last_samples = deque(maxlen=self._n_pilots -
                                   self._skip_n_symbols)
        self._last_detection_times = list()

    def _clear_symbol_sample_map(self) -> None:
        for symbol in self._symbol_sample_map.keys():
            self._symbol_sample_map[symbol].clear()

    def _build_symbol_sample_map(self) -> None:
        for i in range(len(self._last_symbols)):
            self._symbol_sample_map[self._last_symbols[i]].append(
                self._last_samples[i])

    def _determine_threshold_value(self) -> None:
        new_threshold_vals = np.full_like(self._threshold_vals, np.nan)

        index = 0
        while index < self._mod_order - 1:
            upper_sample_sequence = self._symbol_sample_map[
                self._sorted_symbol_map[index + 1]]
            lower_sample_sequence = self._symbol_sample_map[
                self._sorted_symbol_map[index]]

            if len(upper_sample_sequence) == 0 or len(
                    lower_sample_sequence) == 0:
                index += 1
                continue

            new_threshold_vals[index] = (np.mean(upper_sample_sequence) +
                                         np.mean(lower_sample_sequence)) / 2
            index += 1

        deltas = list()

        for index, threshold_val in enumerate(new_threshold_vals):
            if not np.isnan(threshold_val):
                deltas.append(new_threshold_vals[index] -
                              self._threshold_vals[index])

        if len(deltas) == 0:
            self._clear_symbol_sample_map()
            return

        delta = np.mean(deltas)

        for index, threshold_val in enumerate(new_threshold_vals):
            if np.isnan(threshold_val):
                new_threshold_vals[index] = self._threshold_vals[index] + delta

        self._threshold_vals = new_threshold_vals
        self._clear_symbol_sample_map()

    def __call__(self, detection_sample: Optional[DataPoint]) -> Optional[str]:
        if detection_sample == None:
            return None

        self._sample_counter += 1

        if not self._pilots_received:
            self._last_samples.append(detection_sample.value)
            self._last_symbols.append(
                self._pilot_symbol_string[self._sample_counter - 1])
            self._last_detection_times.append(detection_sample.time)

            if self._sample_counter >= self._n_pilots:
                self._pilots_received = True
                self._build_symbol_sample_map()
                self._determine_threshold_value()

                new_deque_1 = deque(maxlen=self._n_window)
                new_deque_2 = deque(maxlen=self._n_window)

                for i in range(self._n_pilots - self._skip_n_symbols):
                    new_deque_1.append(self._last_symbols[i])
                    new_deque_2.append(self._last_samples[i])

                self._last_symbols = new_deque_1
                self._last_samples = new_deque_2

                if self._detec_data != None:
                    for i in range(self._n_pilots):
                        self._detec_data.append(
                            self._pilot_symbol_string[i],
                            self._last_detection_times[i],
                            np.copy(self._threshold_vals),
                        )

                del self._last_detection_times
                self._sample_counter = 0

            return self._pilot_symbol_string[self._sample_counter - 1]

        else:
            threshold_index = np.where(
                detection_sample.value >= self._threshold_vals)[0]

            if len(threshold_index) > 0:
                symbol_decision = self._sorted_symbol_map[threshold_index[-1] +
                                                          1]
            else:
                symbol_decision = self._sorted_symbol_map[0]

            self._symbol_sample_map[symbol_decision].append(
                detection_sample.value)

            if self._detec_data != None:
                self._detec_data.append(
                    symbol_decision,
                    detection_sample.time,
                    np.copy(self._threshold_vals),
                )

            if self._n_coherence != None and self._sample_counter >= self._n_coherence:
                self._build_symbol_sample_map()
                self._determine_threshold_value()
                self._sample_counter = 0

            self._last_samples.append(detection_sample.value)
            self._last_symbols.append(symbol_decision)

            return symbol_decision
