import os
import sqlite3
import json
import tomllib
import polars as pls
from pathlib import Path
from datetime import datetime

from ..dtypes import *

class ExperimentDatabaseMeta(type):
    _instance = None
    _n_references = 0
    _conn = None
    _cursor = None

    def __call__(cls):
        if cls._instance is None:
            cwd_path = os.getcwd()
            database_path = None

            for root, _, files in os.walk(cwd_path, topdown=True):
                if "mmtb.db" in files:
                    database_path = os.path.join(root, "mmtb.db") 

            if database_path is None:
                database_path = os.path.abspath(os.path.join(Path(__file__).parent, "mmtb.db"))

            try:
                cls._conn = sqlite3.connect(database_path)
                cls._cursor = cls._conn.cursor()

                cls._cursor.execute(
                    '''CREATE TABLE IF NOT EXISTS message_data (
                        experiment_name TEXT,
                        t_symbol REAL,
                        t_guard REAL,
                        mod_order INTEGER,
                        use_ex BOOLEAN,
                        n_symbols INTEGER,
                        date DATE,
                        dis_tx_rx REAL,
                        experiment_param TEXT,
                        system_param TEXT,
                        spec_feather BLOB,
                        serial_feather BLOB
                    )''')

                cls._conn.commit()

            except sqlite3.Error as e:
                cls._conn = None
                cls._cursor = None
                raise e

            cls._instance = super(ExperimentDatabaseMeta,
                                  cls).__call__(cls._cursor)
            cls._n_references += 1

        return cls._instance

    @classmethod
    def _remove_reference(cls) -> None:
        cls._n_references -= 1
        if cls._n_references <= 0 and cls._conn is not None:
            cls._conn.close()
            cls._conn = None
            cls._cursor = None
            cls._n_references = 0
            cls._instance = None


class ExperimentDatabase(metaclass=ExperimentDatabaseMeta):
    def __init__(self, cursor: sqlite3.Cursor) -> None:
        self._cursor = cursor

    def __del__(self):
        ExperimentDatabaseMeta._remove_reference()

    def get_info(self,
                 *,
                 experiment_name: str = None,
                 t_symbol: float = None,
                 t_guard: float = None,
                 mod_order: int = None,
                 use_ex: bool = None,
                 n_symbols: int = None,
                 date: datetime = None,
                 dis_tx_rx: float = None) -> list[dict]:

        params = {
            param_name: param_val
            for param_name, param_val in locals().items()
            if param_name != 'self' and param_val is not None
        }
        query = "SELECT experiment_name, date, dis_tx_rx, experiment_param, system_param FROM message_data"

        if params:
            query += " WHERE " + " AND ".join(f"{param_name} = ?"
                                              for param_name in params)

        self._cursor.execute(query, tuple(params.values()))

        return_list = list()

        for experiment_name, date, dis_tx_rx, experiment_param, system_param in self._cursor.fetchall(
        ):
            if system_param is None:
                return_list.append({
                    "experiment_name": experiment_name,
                    "date": date,
                    "dis_tx_rx": dis_tx_rx,
                    "transmission_param": json.loads(str(experiment_param)),
                    "system_param": None
                })

            else:
                return_list.append({
                    "experiment_name": experiment_name,
                    "date": date,
                    "dis_tx_rx": dis_tx_rx,
                    "transmission_param": json.loads(experiment_param),
                    "system_param": tomllib.loads(system_param)
                })

        return return_list

    def get_data(
            self,
            *,
            experiment_name: str = None,
            t_symbol: float = None,
            t_guard: float = None,
            mod_order: int = None,
            use_ex: bool = None,
            n_symbols: int = None,
            date: str = None,
            dis_tx_rx: float = None) -> list[ExperimentData]:

        params = {
            param_name: param_val
            for param_name, param_val in locals().items()
            if param_name != 'self' and param_val is not None
        }
        query = "SELECT experiment_name, dis_tx_rx, experiment_param, system_param, spec_feather, serial_feather FROM message_data"

        if params:
            query += " WHERE " + " AND ".join(f"{param_name} = ?" for param_name in params)

        return_list = list()

        self._cursor.execute(query, tuple(params.values()))

        for experiment_name, dis_tx_rx, experiment_param, system_param, spec_feather, serial_feather in self._cursor.fetchall():
            exp_data = ExperimentData(experiment_name=experiment_name,
                                      dis_tx_rx=dis_tx_rx,
                                      rx_data=RxData(**pls.read_ipc(spec_feather).to_dict(as_series=False)),
                                      tx_data=TxData(**pls.read_ipc(serial_feather).to_dict(as_series=False)), 
                                      trans_param=TransmissionParameters(**json.loads(str(experiment_param))),
                                      spec_settings=SpectrometerSettings(**(tomllib.loads(system_param)["spectrometer"])))
            
            return_list.append(exp_data)

        return return_list
    
