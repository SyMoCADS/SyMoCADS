[mmtb](../../README.md)/[dtypes](../dtypes.md)/SynchronizationData

# mmtb.dtypes.SynchronizationData

**class** $\color{purple}SynchronizationData$ (metric_coeffs: DataPointList | None, detection_metric_coeffs: DataPointList | None)

> Parameters

+ `metric_coeffs: DataPointList | None`
+ `detection_metric_coeffs: DataPointList | None`

> Attributes

+ `metric_coeffs: DataPointList`
+ `detection_metric_coeffs: DataPointList`
+ `symbol_starts: list`

> Methods

+ $\color{mediumpurple}append\_ metric\_ coeff$ (metric_coeff: DataPoint) -> `None`

    Appends the DataPoint to metric_coeffs.

+ $\color{mediumpurple}append\_ detection\_ metric\_ coeff$ (detection_metric_coeff: DataPoint) -> `None`

    Appends the DataPoint to detection_metric_coeffs.

+ $\color{mediumpurple}extend\_ metric\_ coeff$ (metric_coeffs: DataPointList) -> `None`

    Extends metric_coeffs by the DataPointList.

+ $\color{mediumpurple}extend\_ detection\_ metric\_ coeff$ (detection_metric_coeffs: DataPointList) -> `None`

    Extends detection_metric_coeffs by the DataPointList.