[mmtb](../../../README.md)/[evaluation](../..//evaluation.md)/[synchronization](../synchronization.md)/TransmissonStartDetection

## mmtb.types

**class** $\color{purple}TransmissonStartDetection$ (training_data_length: int, false_alarm_probaility: float)

> Parameters:

+ `training_data_length: int` ( &middot; > 0)

    Number of consecutive samples used for determining the threshold for the transmission start detection.

+ `false_alarm_probaility: float` (0 < &middot; < 1)

    Specifies the false alarm probaiblity (left tail probaility) of the transmission start detection.

> Methods

+ $\color{mediumpurple}\_ \_ call\_ \_$ (sample_val: float) -> `bool`

    This is the `__call__` dunder method for this class, which receives data sequentially. Retruns `True` only if a transmission has been detected, i.e., a sample fell below the previously computed threshold; otherwise returns `False`.


+ <span style="color: mediumpurple;">enough_training_samples</span> (None) -> `bool`

    Returns `True` if enough samples have been collected to from the first training data set.