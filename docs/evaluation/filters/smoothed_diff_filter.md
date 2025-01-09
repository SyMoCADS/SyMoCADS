[mmtb](../../../README.md)/[evaluation](../../evaluation.md)/[filters](../filters.md)/smoothed_diff_filter

## mmtb.evaluation.filters.smoothed_diff_filter

**def** $\color{mediumpurple}smoothed\_ diff\_ filter$ (t_sample: float, t_symbol: float, t_irradiation: float, dis_tx_rx: float, fraction_used_data: float = 0.2) &rarr; `np.array`

Returns a `np.array` containing the filter values for differential correlation synchronization scheme.

`Note`: The smoothed filter is based on data extracted from prior experiments. This means that if no data can be found that matches the given parameters, the function will return an error.

> Parameters

+ `t_sample: float` ( &middot; &gt; 0)

    Sample interval.

+ `t_symbol: float` ( &middot; &gt; 0)

    Symbol duration.

+ `t_irradiation: float` ( &middot; &gt; 0)
    
    Irradiation duration.

+ `dis_tx_rx: float` ( &middot; &ge; 0)

    Distance between TX and RX in centimeters.

+ `fraction_used_data: float = 0.2` (0 &lt; &middot; &le; 1)

    Fraction of data used for the locally weighted scatterplot smoothing.

> Returns

+ `np.array`