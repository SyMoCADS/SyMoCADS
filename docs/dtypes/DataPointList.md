[mmtb](../../README.md)/[dtypes](../dtypes.md)/DataPointList

#mmtb.dtypes.DataPointList

**class** $\color{purple}DataPointList$ (time: Sequence[float | datetime], value: Sequence[float])

> Parameters

+ `times: Sequence[float | datetime]`
+ `values: Sequence[float]`

> Attributes

+ `times: list[float | datetime]`
+ `values: list[float]`

> Methods

+ $\color{mediumpurple}\_ \_ len\_ \_$ (None) -> `int`
    
    Dunder method that returns the length of the DataPointList.

+ $\color{mediumpurple}\_ \_ iter\_ \_$ (None) -> `Iterator`
    
    Dunder method that returns an Iterator for DataPointList, which upon calling `__next__()` return a DataPoint.

+ $\color{mediumpurple}\_ \_ getitem\_ \_$ (index: int | slice) -> `DataPoint | DataPointList`
    
    This dunder method returns either the specified entry from the DataPointList as a DataPoint if the index is of type `int`, or returns the specified section of the DataPointList as a separate DataPointList if the index is of type `slice`.

+ $\color{mediumpurple}append$ (data_point: DataPoint) -> `None`

    Appends a DataPoint to the DataPointList.

+ $\color{mediumpurple}extend$ (other: DataPointList) -> `None`

    Extends the DataPointList by the other given DataPointList.

+ $\color{mediumpurple}pop$ (index: int) -> `None`

    Removes an entry from the DataPointList at the specified index.

+ $\color{mediumpurple}clear$ (None) -> `None`

    Clears the entire DataPointList, removing all entries.