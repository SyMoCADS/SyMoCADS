[mmtb](../../../README.md)/[evaluation](../../evaluation.md)/Evaluation

## mmtb.evaluation.Evaluation

**class** $\color{purple}Evaluation$(tranmission_start_detec: TransmissonStartDetection,
sync_detec_tuples: tuple[SynchronizationBase, DetectionBase | Sequence[DetectionBase] | None] | Sequence[tuple[SynchronizationBase, DetectionBase | Sequence[DetectionBase] | None]])

This convenience class is able to group the transmission detection with multiple synchronization and corresponding detection blocks for ease of evaluation.

> Parameters:
+ `tranmission_start_detec: TransmissonStartDetection`

+ `sync_detec_tuples: tuple[SynchronizationBase, DetectionBase | Sequence[DetectionBase] | None] | Sequence[tuple[SynchronizationBase, DetectionBase | Sequence[DetectionBase] | None]]`

    This parameter specifies the evaluation chains, i.e., which synchronizer is used for which detector. Valid formats for this parameter include:

    | sync_detec_tuples |
    |-------------------|
    | (SynchronizationBase, DetectionBase)|
    | (SynchronizationBase, None)|
    | (SynchronizationBase, [DetectionBase, ..., DetectionBase])|
    | [(SynchronizationBase, DetectionBase), ..., (SynchronizationBase, DetectionBase)]
    | [(SynchronizationBase, [DetectionBase, ..., DetectionBase]), ..., (SynchronizationBase, [DetectionBase, ..., DetectionBase])]


> Methods

+ $\color{mediumpurple}\_ \_ call\_ \_$ (samples: DataPoint | DataPointList) -> `None`

    This is the `__call__` dunder method for this class, which receives data sequentially - either individual samples or multiple samples at once.