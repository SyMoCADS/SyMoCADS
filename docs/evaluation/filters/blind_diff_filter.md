[mmtb](../../../README.md)/[evaluation](../../evaluation.md)/[filters](../filters.md)/blind_diff_filter

# mmtb.evaluation.filters.blind_diff_filter

**def** $\color{mediumpurple}blind\_ diff\_ filter$ (t_sample: float, t_symbol: float, t_irradiation: float) &rarr; `np.array`

Returns the `np.array` containing the filter values for differential correlation synchronization scheme.

> Parameters

+ `t_sample: float` (. &gt; 0)

    Sample interval.

+ `t_symbol: float` (. &gt; 0)

    Symbol duration.

+ `t_irradiation: float` (. &gt; 0)
    
    Irradiation duration.

> Returns

+ `np.array`