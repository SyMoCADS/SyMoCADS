[mmtb](../../../README.md)/[evaluation](../../evaluation.md)/[filters](../filters.md)/blind_filter

## mmtb.evaluation.filters.blind_filter

**def** $\color{mediumpurple}blind\_ filter$ (t_sample: float, t_symbol: float, t_irradiation: float) &rarr; `np.array`

Returns the `np.array` containing the filter values for correlation synchronization scheme.

> Parameters

+ `t_sample: float` (&middot; &gt; 0)

    Sample interval.

+ `t_symbol: float` (&middot; &gt; 0)

    Symbol duration.

+ `t_irradiation: float` (&middot; &gt; 0)
    
    Irradiation duration.

> Returns

+ `np.array`