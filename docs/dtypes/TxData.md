[mmtb](../../README.md)/[dtypes](../dtypes.md)/TxData

# mmtb.dtypes.TxData

**class** $\color{purple}TxData$ (timestamps: list[datetime] | None, rel_times: list[float] | None, intensity_vals: list[float] | None, event_symbols: list[str] | None)

> Parameters

+ `timestamps: list[datetime] | None`
+ `rel_times: list[float] | None`
+ `intensity_vals: list[float] | None`
+ `event_symbols: list[str] | None`

> Attributes

+ `timestamps: list[datetime]`
+ `rel_times: list[float]`
+ `intensity_vals: list[float]`
+ `event_symbols: list[str]`

> Methods

+ $\color{mediumpurple}intensity\_ function$ (None) -> `DataPointList`

    Returns a DataPointList characterizing the variation in TX intensity over time as a rectangular function for ease of plotting.