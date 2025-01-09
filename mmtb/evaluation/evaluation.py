from typing import Optional, Union, Sequence
import numpy as np

from .synchronization import TransmissonStartDetection, SynchronizationBase
from .detection import DetectionBase
from ..dtypes import DetectionData, SynchronizationData, DataPointList, DataPoint, TransmissionParameters


def calculate_symbol_error_rate(n_pilots, transmission_param: TransmissionParameters,
                                detec_data: DetectionData) -> float:
    symbolstring = [symbol for symbol in (int(transmission_param.n_reps) * transmission_param.symbol_string)]

    n_total = len(symbolstring) - n_pilots

    n_errors = np.sum(
        np.not_equal(symbolstring, detec_data.detection_symbols).astype(int))

    return n_errors / n_total


def calculate_bit_error_rate_gray_mapping(n_pilots, transmission_param: TransmissionParameters, detec_data: DetectionData) -> float:
    mod_order = transmission_param.mod_order
    n_bits = np.log2(mod_order)

    transmitted_symbols = [symbol for symbol in (int(transmission_param.n_reps) * transmission_param.symbol_string)]
    received_symbols = detec_data.detection_symbols

    # Construct Gray Code for Modulation Order M
    old_code_list = ['0', '1']
    new_code_list = list()

    while len(old_code_list[0]) != n_bits:
        new_code_list = ['1' + bits for bits in reversed(old_code_list)]
        old_code_list = ['0' + bits for bits in old_code_list]

        old_code_list.extend(new_code_list)

    gray_code = {
        symbol: bit_mapping
        for symbol, bit_mapping in zip(transmission_param.symbol_map.keys(),
                                       old_code_list)
    }

    # Mapping symbolstrings to Gray mapping
    transmitted_bits = ""
    received_bits = ""

    for index in range(len(transmission_param.symbol_string) - n_pilots):
        transmitted_bits = transmitted_bits + gray_code[transmitted_symbols[
            index + n_pilots]]
        received_bits = received_bits + gray_code[received_symbols[index +
                                                                   n_pilots]]

    transmitted_bits = [int(bit) for bit in transmitted_bits]
    received_bits = [int(bit) for bit in received_bits]

    n_errors = np.sum(
        np.not_equal(transmitted_bits, received_bits).astype(int))

    return n_errors / len(transmitted_bits)


def calculate_norm_rel_sync_error(t_symbol: float, sync_data: SynchronizationData) -> np.array:
    symbol_starts = sync_data.symbol_starts
    return np.diff(symbol_starts) / t_symbol - 1


def calculate_avg_norm_abs_rel_sync_error(t_symbol: float, sync_data: SynchronizationData) -> float:
    return np.mean(np.abs(calculate_norm_rel_sync_error(t_symbol, sync_data)))


class Evaluation:
    def __init__(
        self,
        transmission_start_detec: TransmissonStartDetection,
        sync_detec_tuples: Union[tuple[SynchronizationBase, Optional[Union[DetectionBase, Sequence[DetectionBase]]]], Sequence[tuple[SynchronizationBase, Optional[Union[DetectionBase, Sequence[DetectionBase]]]]]],
    ) -> None:
        self._transmission_start_detec = transmission_start_detec

        if isinstance(sync_detec_tuples, tuple):
            self._sync_detec_tuples = [sync_detec_tuples]

        elif isinstance(sync_detec_tuples, Sequence):
            self._sync_detec_tuples = sync_detec_tuples

        else:
            raise ValueError("The given sync_detec_tuples is not in the correct format.")

        for sync_detec_tuple in self._sync_detec_tuples:
            if not isinstance(sync_detec_tuple, tuple):
                raise ValueError("The given sync_detec_tuples is not in the correct format.")

            if not isinstance(sync_detec_tuple[0], SynchronizationBase):
                raise ValueError("The given sync_detec_tuples is not in the correct format.")

            if isinstance(sync_detec_tuple[1], Sequence):
                for detec in sync_detec_tuple[1]:
                    if not isinstance(detec, DetectionBase):
                        raise ValueError("The given sync_detec_tuples is not in the correct format.")

            elif not isinstance(sync_detec_tuple[1], DetectionBase):
                raise ValueError("The given sync_detec_tuples is not in the correct format.")

    def __call__(self, samples: Union[DataPoint, DataPointList]) -> None:

        if isinstance(samples, DataPointList):
            for sample in samples:
                self._eval(sample)

        if isinstance(samples, DataPoint):
            self._eval(samples)

    def _eval(self, sample: DataPoint) -> None:
        ret = self._transmission_start_detec(sample.value)

        for sync_detec_tuple in self._sync_detec_tuples:
            if ret:
                sync_detec_tuple[0].set_transmission_start(sample.time)

            detec_sample = sync_detec_tuple[0](sample)

            if detec_sample is not None and sync_detec_tuple[1] is not None:
                for idx, detec in enumerate(sync_detec_tuple):
                    if idx == 0 or detec is None:
                        continue

                    detec(detec_sample)