[mmtb](../../../README.md)/[evaluation](../..//evaluation.md)/[detection](../detection.md)/ThresholdDetection

## mmtb.types

**class** $\color{purple}ThresholdDetection$ (pilot_symbolstring: Sequence[str], symbol_map: dict[str, float], n_window: int, n_coherence: int, detec_data: DetectionData | None, skip_n_symbols: int = 0)

This class inherits from [DetectionBase](./DetectionBase.md) in order to implement a threshold detection.

> Parameters:
+ `pilot_symbolstring: Sequence[str]`

    String containing the pilot symbol sequence.

+ `symbol_map: dict[str, float]` (dict[str(&middot; &ge; 0), 0 &le; &middot; &le; 1])

    Dictionary with symbol (`str`) to normalized TX intensity (`float`) mapping.

+ `n_window: int` ( &middot; > 0)

    Number of preceeding detection samples used for the readjustment of the threshold values.

+ `n_coherence: int` ( &middot; > 0)

    Number of detection samples for which the current thresholds are valid, after which the thresholds are re-evaluated.

+ `detec_data: DetectionData | None`

    Dataclass to store the detection data for later analysis.

+ `skip_n_symbols: int = 0` ( &middot; &ge; 0)

    Number of initially transmitted symbols ignored/skipped (usually due to rapidly changing fluorescence at the start of a transmission).

> Methods

+ $\color{mediumpurple}\_ \_ call\_ \_$(sample_val: float | None) -> `str | None`

    This is the `__call__` dunder method for this class, which receives data sequentially. Returns the detect symbol character in form of a `str` upon succesful detection; otherwise returns `False`.