[mmtb](../../README.md)/[dtypes](../dtypes.md)/DetectionData

# mmtb.dtypes.DetectionData

**class** $\color{purple}DetectionData$ (detection_symbols: list[str] | None, detection_times: list[float] | None, threshold_vals: list[list[float]] | None)

> Parameters

+ `detection_symbols: list[str] | None`
+ `detection_times: list[float] | None`
+ `threshold_vals: list[list[float]] | None`

> Attributes

+ `detection_symbols: list[str]`
+ `detection_times: list[float]`
+ `threshold_vals: list[list[float]]`

> Methods

+ $\color{mediumpurple}append$ (symbol: str, detection_time: float, threshold_vals: list[float]) -> `None`

    Appends the new symbol, detect time and corresponding threshold values to DetectionData.

+ $\color{mediumpurple}extend$ (symbols: Sequence[str], detection_times: list[float], threshold_vals: list[list[float]]) -> `None`

    Extends DetectionData with a list of symbols, a list of detection times, and a list of corresponding threshold values.