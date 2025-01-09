[mmtb](../../../README.md)/[evaluation](../..//evaluation.md)/[synchronization](../synchronization.md)/CorrelationSynchronization

## mmtb.types.synchronization.CorrelationSynchronization

**class** $\color{purple}CorrelationSynchronization$ (t_sample: float,
t_symbol: float, filter_vals: Sequence[float], search_radius: float, n_symbols: int sync_data: SynchronizationData | None = None, static_sync_n_avg: int | None = None)

`Note:` This is a subclass of [SynchronizationBase](./SynchronizationBase.md) that uses the default correlation as its synchronization metric.

> Parameters:
+ `t_sample: float` ( &middot; > 0)

    Sampling interval.

+ `t_symbol: float` ( &middot; > 0)

    Symbol duration.

+ `filter_vals: Sequence[float]`

    Sequence (array-like) containing the filter values.

+ `search_radius: float` (0 < &middot; < 1)

    Radius of the search interval.

+ `n_symbols: int` ( &middot; > 0)

    Total number of transmitted symbols.

+ `sync_data: SynchronizationData | None = None`

    SyncData class storing the data corresponding to the synchronization process.

+ `static_sync_n_avg: int | None = None`

    If not None, the synchronization differs from standard symbol synchronization, where the initial estimate is based on the final estimate of the previous symbol. Instead, this parameter specifies a set number of initial symbols for standard synchronization. It calculates the average synchronization time of these symbols and uses it as a fixed final estimate or center for the search interval going forward. This allows comparison with standard synchronisation by removing the dependence on the last synchronisation estimate of previous symbols

> Methods

+ $\color{mediumpurple}\_ \_ call\_ \_$ (new_sample: DataPoint) -> `DataPoint | None`

    This is the `__call__` dunder method for this class,  which receives data sequentially. Returns the data point when the synchronization process has settled on a sample, otherwise returns `None`.

+  $\color{mediumpurple}set\_ transmission\_ start$ (transmission_start_time: float) -> `None`

    Sets the transmission start time, after which the synchronization process will begin. No synchronization can take place before this method is called.