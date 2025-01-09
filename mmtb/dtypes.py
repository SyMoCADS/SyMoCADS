from datetime import datetime
from typing import Sequence, Union, Sequence
from pydantic import BaseModel, Field, ConfigDict, model_validator, NonNegativeInt, PositiveFloat, PositiveInt, NonNegativeFloat, validate_call, AliasPath

import matplotlib.pyplot as plt


class DataPoint(BaseModel):
    time: Union[float, datetime]
    value: float


class DataPointList(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)

    times: list[Union[float, datetime]]= Field(default=list())
    values: list[float]= Field(default=list())

    def __init__(self, *args, **kwargs) -> None:
        times = list()
        values = list()

        if len(kwargs) == 2:
            times = kwargs.get("times", None)
            values = kwargs.get("values", None)

        if len(args) == 1:
            if isinstance(args[0], DataPoint):
                times = [args[0].time]
                values = [args[0].value]

            if isinstance(args[0], Sequence):
                times = list()
                values = list()

                for list_elem in args[0]:
                    if not isinstance(list_elem, DataPoint):
                        raise TypeError

                    times.append(list_elem.time)
                    values.append(list_elem.value)

        super().__init__(times=times, values=values)

    @model_validator(mode='after')
    def check_input_list_lengths(self, values): 
        if len(self.times) != len(self.values):
            raise ValueError("times and values inputs must have the same length.")
        
        return self

    def __iter__(self) -> list[DataPoint]:
        return [DataPoint(time=time, value=value) for time, value in zip(self.times, self.values)].__iter__()

    def __getitem__(self, index: Union[int, slice]):
        if isinstance(index, slice):
            return DataPointList(times=self.times[index], values=self.values[index])
        else:
            return DataPoint(time=self.times[index], value=self.values[index])

    def __len__(self) -> int:
        return len(self.times)

    def append(self, data_point: DataPoint) -> None:
        self.times.append(data_point.time)
        self.values.append(data_point.value)

    def extend(self, other) -> None:
        self.times.extend(other.times)
        self.values.extend(other.values)

    def pop(self, index) -> None:
        self.times.pop(index)
        self.values.pop(index)

    def clear(self) -> None:
        self.times.clear()
        self.values.clear()


class SynchronizationData(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)

    metric_coeffs: DataPointList = Field(default=DataPointList())
    detection_metric_coeffs: DataPointList = Field(default=DataPointList())

    @property
    def symbol_starts(self) -> list[float]:
        return self.detection_metric_coeffs.times

    @validate_call
    def append_metric_coeff(self, metric_coeff: DataPoint) -> None:
        self.metric_coeffs.append(metric_coeff)

    @validate_call
    def append_detection_metric_coeff(self, detection_metric_coeff: DataPoint) -> None:
        self.detection_metric_coeffs.append(detection_metric_coeff)

    @validate_call
    def extend_metric_coeff(self, metric_coeffs: DataPointList) -> None:
        self.metric_coeffs.extend(metric_coeffs)

    @validate_call
    def extend_detection_metric_coeff(self, detection_metric_coeffs: DataPointList) -> None:
        self.detection_metric_coeffs.extend(detection_metric_coeffs)


class DetectionData(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)

    detection_symbols: list[str] = Field(default=list())
    detection_times: list[float] = Field(default=list())
    threshold_vals: dict[str, list[float]] = Field(default=dict())

    @validate_call
    def append(self, symbol: str, detection_time: float, threshold_vals: list[float]) -> None:
        self.detection_symbols.append(symbol)
        self.detection_times.append(detection_time)

        for i, threshold_val in enumerate(threshold_vals):
            try:
                self.threshold_vals[str(i)].append(threshold_val)
            except:
                self.threshold_vals[str(i)] = list()
                self.threshold_vals[str(i)].append(threshold_val)

    @validate_call
    def extend(self, symbols: Sequence[str], detection_times: list[float], threshold_vals: list[list[float]]) -> None:
        if len(symbols) != len(threshold_vals) or len(symbols) != len(detection_times):
            raise ValueError(f"All parameter lists must have the same length: {len(symbols)}, {len(detection_times)}, {len(threshold_vals)}")

        for index in range(len(symbols)):
            self.append(symbols[index], detection_times[index], threshold_vals[index])


class RxData(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)
    
    timestamps: list[datetime] = Field(validation_alias='timestamps')
    rel_times: list[float] = Field(validation_alias='rel_time')
    intensity_vals: list[float] = Field(validation_alias='intensity')
    fluorescence_vals: list[float] = Field(validation_alias='fluorescence')


class TxData(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)

    timestamps: list[datetime] = Field(validation_alias='timestamps')
    rel_times: list[float] = Field(validation_alias='rel_time')
    intensity_vals: list[float]  = Field(validation_alias='tx_intensity')
    event_symbols: list[str] = Field(validation_alias='symbols')

    def intensity_function(self) -> DataPointList:
        if len(self.rel_time) == 0:
            return DataPointList()

        tx_function = DataPointList()
        tx_function.append(DataPoint(time=self.rel_time[0], value=0.0))
        tx_function.append(DataPoint(time=self.rel_time[0], value=self.intensity_vals[0]))

        for data_point in [DataPoint(time=time, value=value) for time, value in zip(self.rel_time, self.intensity_vals)][1:]:
            if data_point.value != tx_function[-1].value:
                tx_function.append(DataPoint(time=data_point.time, value=tx_function[-1].value))
            tx_function.append(DataPoint(time=data_point.time, value=data_point.value))

        return tx_function
    

class TransmissionParameters(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)

    t_symbol: PositiveFloat = Field(validation_alias=AliasPath('tx', 't_symbol'))
    t_guard: PositiveFloat = Field(validation_alias=AliasPath('tx', 't_guard'))
    mod_type: str = Field(validation_alias=AliasPath('tx', 'mod_type'))
    mod_order: PositiveInt = Field(ge=2, validation_alias=AliasPath('tx', 'mod_order'))
    symbol_map: dict[str, NonNegativeFloat] = Field(validation_alias=AliasPath('tx', 'symbol_map'))
    symbol_string: str = Field(validation_alias=AliasPath('tx', 'symbolstring'))
    n_reps: NonNegativeInt = Field(validation_alias=AliasPath('tx', 'n_reps'))
    tx_leds: list[PositiveInt] = Field(validation_alias=AliasPath('tx', 'leds'))
  
    ex_intensity: NonNegativeFloat = Field(validation_alias=AliasPath('ex', 'intensity'))
    ex_leds: list[PositiveInt] = Field(validation_alias=AliasPath('ex', 'leds'))

    @property
    def t_irradiation(self) -> float:
        return self.t_symbol - self.t_guard
    
    @property
    def n_symbols(self) -> int:
        return len(self.symbol_string) * self.n_reps
    
    @property 
    def total_symbol_string(self) -> str:
        return self.n_reps * self.symbol_string

class SpectrometerSettings(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True) 

    t_sample: PositiveFloat = Field(validation_alias='sampling_interval')
    t_integration: PositiveFloat = Field(validation_alias='integration_time')
    eval_wavelengths: tuple[PositiveFloat, PositiveFloat] = Field(validation_alias='evaluation_wavelengths')

class ExperimentData(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)

    experiment_name: str
    dis_tx_rx: float
    rx_data: RxData
    tx_data: TxData
    trans_param: TransmissionParameters
    spec_settings: SpectrometerSettings

    def plot(self) -> None:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 8), height_ratios=[4, 1], sharex=True)

        ax1.plot(self.rx_data.rel_time, self.rx_data.fluorescence_vals, linewidth=2)
        ax1.set_xlabel("Time [s]")
        if len(self.spec_settings.eval_wavelengths) == 1:
            ax1.set_ylabel(f"Normalized Fluorescence at {self.spec_settings.eval_wavelengths[0]} nm")
        else:
            ax1.set_ylabel(f"Normalized Averaged Fluorescence from {self.spec_settings.eval_wavelengths[0]} nm to {self.spec_settings.eval_wavelengths[1]} nm")
        ax1.set_xlim(self.rx_data.rel_time[0], self.rx_data.rel_time[-1])
        ax1.set_ylim(0, 1.2)
        ax1.grid()

        tx_function = self.tx_data.intensity_function()

        ax2.plot(tx_function.times, tx_function.values, color="red", linewidth=2)
        ax2.set_xlabel("Time [s]")
        ax2.set_ylabel("TX Intensity [%]")
        ax2.set_ylim(0.0, 1.2)
        ax2.grid()

        plt.show()
