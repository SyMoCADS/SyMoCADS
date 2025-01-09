[mmtb](../README.md)/experiments

## mmtb.experiments.get_selected_experiments

**def** $\color{mediumpurple}get\_ selected\_ experiments$ (*, use_prev_selected_files: bool = False, select_files: Sequence[str] | None = None)

Calling this function without any parameters opens a window where the user can select all the desired experiments. After confirmation, the information associated with the selected experiments is returned in the form of a dictionary. If either one of the input parameters is (exclusively) specified, the window selection is skipped and the experiment  data is returned directly.

`Note`: The function uses a file-specific memory system. This means that it keeps track of previous selections or choices made while working with a particular file (for window selections only). It can remember selections for up to 50 different files.

>Parameters

+ `use_prev_selected_files: bool = False`
+ `select_files: Sequence[str] | None = None`

>Returns

+ `List[ExperimentData]`

    Returns a `list` of `ExperimentData` of the selected experiments in order of selection.