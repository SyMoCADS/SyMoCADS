import inspect
import json
import os
from pathlib import Path
from typing import Union, Sequence, Optional

from ._interface import ExperimentSelectionWindow
from ..dtypes import ExperimentData
from ._database import ExperimentDatabase


def get_selected_experiments(*, use_prev_selected_files: bool=False, select_files: Optional[Union[str, Sequence[str]]]=None) -> list[ExperimentData]:
    if use_prev_selected_files and select_files is not None:
        raise ValueError("Either use previously selected files or specify to be selected files; not both.")

    ret_list = list()
    
    if select_files is not None:

        if len(select_files) == 0:
            raise ValueError("The select_files parameter cannot be an empty list.")
        
        for file_specifier in select_files:
            if not isinstance(file_specifier, str):
                raise TypeError("The entries of select_files must be of type 'str'")
            
        selected_files = select_files
    else:
        file_name = inspect.stack()[1].filename

        json_path = os.path.abspath(os.path.join(Path(__file__).parent, "SelectedExperiments.json"))

        if not os.path.exists(json_path):
            with open(json_path, 'w') as f:
                json.dump({}, f, indent=4)
        
        with open(json_path, 'r') as f:
            selected_files_dict = json.load(f)
            selected_files = selected_files_dict.get(file_name)

        if use_prev_selected_files and selected_files is None:
            raise RuntimeError("Could not find any previously selected experiments for this file.")
        
    if not use_prev_selected_files and select_files is None:
        ew = ExperimentSelectionWindow(selected_files)

        try:
            ret_list = ew.get_selected_exp_data()
            selected_files = list(ew.get_selected_exp())
        except:
            pass

        if len(ret_list) > 0:
            with open(json_path, 'w') as f:
                selected_files_dict[file_name] = ew.get_selected_exp()

                if len(selected_files_dict) > 50:
                    selected_files_dict.pop(next(iter(selected_files_dict)))

                json.dump(selected_files_dict, f, indent=4)

        ew.close()
    else:

        database = ExperimentDatabase()

        for date_exp_str in selected_files:
            date_exp_str = date_exp_str.split(')')
            date = date_exp_str[0].replace('(', '')
            exp_name = date_exp_str[1][1:]
            exp_list =  database.get_data(date=date, experiment_name=exp_name)

            if len(exp_list) == 0:
                raise ValueError(f"'{date_exp_str}' could not be found.")
            
            ret_list.extend(exp_list)
            

    print(f"Selected experiments: {selected_files}")

    return ret_list