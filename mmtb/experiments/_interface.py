import os
import tkinter as tk
from tkinter import scrolledtext
from functools import partial
from typing import Optional

from ..dtypes import *
from ._database import ExperimentDatabase

class ExperimentSelectionWindow:
    def __init__(self, prev_selected_exp: Optional[list[str]] = None):
        self._database = ExperimentDatabase()
        self._curr_selection = None

        self._root_win = tk.Tk()
        self._root_win.title("Media Modulation Testbed: Experiments")
        self._logo = tk.PhotoImage(file = os.path.abspath(os.path.join(__file__, "..", "idc_logo.png")))
        self._root_win.wm_iconphoto(False, self._logo)
        self._root_win.resizable(False, False)

        ################### 
        # Class variables #
        ###################

        self._dis_bool = tk.BooleanVar(value=False) 
        self._t_symbol_bool = tk.BooleanVar(value=False)
        self._t_guard_bool = tk.BooleanVar(value=False)
        self._mod_order_bool = tk.BooleanVar(value=False)
        self._use_ex_bool = tk.BooleanVar(value=False)

        self._dis_tx_rx = tk.DoubleVar(value=0)
        self._t_symbol = tk.DoubleVar(value=0)
        self._t_guard = tk.DoubleVar(value=0)
        self._mod_order = tk.IntVar(value=0)
        self._use_ex = tk.StringVar(value="True")

        ########### 
        # Widgets #
        ###########

        self._exp_label = tk.Label(master=self._root_win, text="Found Experiments: (0)")
        self._exp_label.grid(column=0, row=0, sticky="w", padx=5)

        self._exp_list = tk.Listbox(master=self._root_win, width=50, height=8)
        self._exp_list.grid(column=0, row=1, sticky="n", padx=5)
        self._exp_list.bind('<<ListboxSelect>>', partial(self._show_exp_info, id="search_list"))
        self._exp_list.bind('<Double-1>', self._add_exp_to_selection)

        self._search_scrollbar = tk.Scrollbar(master=self._root_win)
        self._search_scrollbar.grid(column=2, row=1, sticky='ns')

        self._exp_list.config(yscrollcommand=self._search_scrollbar.set)
        self._search_scrollbar.config(command=self._exp_list.yview)

        self._exp_info_label = tk.Label(master=self._root_win, text="Detailed Information:")
        self._exp_info_label.grid(column=3, row=0, sticky="w", padx=5)

        self._exp_info = scrolledtext.ScrolledText(master=self._root_win, width=55, height=20)
        self._exp_info.configure(state=tk.DISABLED)
        self._exp_info.grid(column=3, row=1, rowspan=5, sticky="ns", padx=5)
        
        self._set_list_entries()

        self._filter_exp_button = tk.Button(master=self._root_win, text="Filter", command=self._filter_exp)
        self._filter_exp_button.grid(column=0, row=2, sticky="e", padx=5)

        self._add_exp_button = tk.Button(master=self._root_win, text="Add", command=partial(self._add_exp_to_selection, 0))
        self._add_exp_button.grid(column=0, row=2, sticky="w", padx=5)

        self._selected_label = tk.Label(master=self._root_win, text="Selected Experiments: (0)")
        self._selected_label.grid(row=3, column=0, sticky='w', padx=5)

        self._selected_list = tk.Listbox(master=self._root_win, width=50, height=8)
        self._selected_list.grid(column=0, row=4, sticky="nw", padx=5)
        self._selected_list.bind('<<ListboxSelect>>', partial(self._show_exp_info,  id="selected_list"))
        self._selected_list.bind('<Double-1>', self._remove_selected_exp)
        self._selected_list.bind('<B1-Motion>', self._drag_selected_entry)

        self._selected_scrollbar = tk.Scrollbar(master=self._root_win)
        self._selected_scrollbar.grid(column=2, row=4, sticky='ns')

        self._selected_list.config(yscrollcommand=self._selected_scrollbar.set)
        self._selected_scrollbar.config(command=self._selected_list.yview)

        self._remove_exp_button = tk.Button(master=self._root_win, text="Remove", command=partial(self._remove_selected_exp, 0))
        self._remove_exp_button.grid(column=0, row=5, sticky="w", padx=5)

        self._confirm_button = tk.Button(master=self._root_win, text="Confirm", command=self._confirm_event)
        self._confirm_button.grid(column=0, row=6, columnspan=4, pady=10)

        if prev_selected_exp is not None and len(prev_selected_exp) > 0:
            self._selected_label.config(text=f"Selected Experiments: ({len(prev_selected_exp)})")

            for row, exp in enumerate(prev_selected_exp):
                self._selected_list.insert(row, exp)

        self._root_win.mainloop()
    
    def _show_exp_info(self, event, id: str):
        if id == "search_list":
            selected_entry = self._exp_list.curselection()
        else:
            selected_entry = self._selected_list.curselection()

        if not selected_entry:
            return

        self._exp_info.configure(state=tk.NORMAL)
        self._exp_info.delete(0.0, "end")

        if id == "search_list":
            selection = self._exp_list.curselection()   
        else:
            selection = self._selected_list.curselection()
            self._curr_selection = self._selected_list.nearest(event.y)

        if selection:
            if id == "search_list":
                selected_entry = self._exp_list.get(selection[0]).split(')')
            else:
                selected_entry = self._selected_list.get(selection[0]).split(')')

            date = selected_entry[0].replace('(', '')
            experiment_name = str(selected_entry[1][1:])

            experiment_info = self._database.get_info(experiment_name=experiment_name, date=date)[0]

            if experiment_info["system_param"] is not None:
                self._exp_info.insert("end", "------------------SYSTEM PARAMETERS-------------------\n")

                self._exp_info.insert("end", f"distance_TX_RX = {experiment_info["dis_tx_rx"]} [cm]\n\n")
                for key, d in experiment_info["system_param"].items():
                    self._exp_info.insert("end", f"{key.upper()}:\n\n")
        
                    for param, val in d.items():
                        if "interval" in param or "time" in param:
                            self._exp_info.insert("end", f"{str(param)} = {val} [s]\n")
                        elif "wavelength" in param:
                            self._exp_info.insert("end", f"{str(param)} = {val} [nm]\n")

                self._exp_info.insert("end", "\n\n")

            self._exp_info.insert("end", "-----------------TRANSMISSION PARAMETERS---------------\n")

            try:
                experiment_info["transmission_param"]["tx"]
                for key, d in experiment_info["transmission_param"].items():
                        self._exp_info.insert("end", f"{key.upper()}:\n\n")
                        for param, val in d.items():
                            if 't_' in param:
                                self._exp_info.insert("end", f"{str(param)} = {val} [s]\n")
                            else:
                                self._exp_info.insert("end", f"{str(param)} = {val}\n")

                        self._exp_info.insert("end", "\n")
            except KeyError:
                for param, val in experiment_info["transmission_param"].items():
                    if 't_' in param:
                        self._exp_info.insert("end", f"{str(param)} = {val} [s]\n")
                    else:
                        self._exp_info.insert("end", f"{str(param)} = {val}\n")
                
                self._exp_info.insert("end", "\n")

        self._exp_info.configure(state=tk.DISABLED)
                        
    def _add_exp_to_selection(self, event) -> None:
        self._show_exp_info(event, "search_list")
        selection = self._exp_list.curselection()
        
        if len(selection) == 0:
            return
        
        value = self._exp_list.get(selection[0])

        if value not in self._selected_list.get(0, "end"):
            self._selected_list.insert("end", value)
            updated_elem_num = len(self._selected_list.get(0, "end"))
            self._selected_label.config(text=f"Selected Experiments: ({updated_elem_num})")

    def _remove_selected_exp(self, event) -> None:
        selection = self._selected_list.curselection()

        if selection:
            self._selected_list.delete(selection[0])
            selected_exps = [exp for exp in self._selected_list.get(0, "end") if exp != '']
            self._selected_list.delete(0, "end")

            updated_elem_num = len(selected_exps)
            self._selected_label.config(text=f"Selected Experiments: ({updated_elem_num})")

            for row, exp in enumerate(selected_exps):
                self._selected_list.insert(row, exp)

    def _set_list_entries(self, **kwargs) -> None:
        self._exp_list.delete(0, "end")

        row = 0

        for entry in self._database.get_info(**kwargs):
            self._exp_list.insert(row, f"({entry["date"]}) {entry["experiment_name"]}")
            row += 1

        self._exp_label.config(text=f"Found Experiments: ({row})")

    def _drag_selected_entry(self, event) -> None:
        index = self._selected_list.nearest(event.y)
        curr_select = self._selected_list.curselection()

        if index != self._curr_selection and curr_select:
            selected_exp = list(self._selected_list.get(0, "end"))
            
            self._selected_list.delete(0, "end")
            self._selected_list.selection_clear(0, tk.END)

            selected_exp[curr_select[0]], selected_exp[index] = selected_exp[index], selected_exp[curr_select[0]]
            
            for row, exp in enumerate(selected_exp):
                self._selected_list.insert(row, exp)
            
            self._curr_selection = index
            self._selected_list.selection_set(index)

    def _filter_exp(self) -> None:
        top = tk.Toplevel(master=self._root_win)
        top.wm_iconphoto(False, self._logo)
        top.title("Filter by")

        database_entries = self._database.get_info()

        t_symbols = set()
        t_guards = set()
        mod_orders = set()
        dis_tx_rx = set()

        for entry in database_entries:
            try:
                t_symbols.add(entry["transmission_param"]["tx"]["t_symbol"])
                t_guards.add(entry["transmission_param"]["tx"]["t_guard"])
                mod_orders.add(entry["transmission_param"]["tx"]["mod_order"])
                dis_tx_rx.add(entry["dis_tx_rx"])
            except KeyError:
                t_symbols.add(entry["transmission_param"]["t_symbol"])
                t_guards.add(entry["transmission_param"]["t_guard"])
                mod_orders.add(entry["transmission_param"]["mod_order"])
                dis_tx_rx.add(entry["dis_tx_rx"])

        t_symbols = sorted(list(t_symbols))
        t_guards = sorted(list(t_guards))
        mod_orders = sorted(list(mod_orders))
        dis_tx_rx = sorted(list(dis_tx_rx))

        if self._t_symbol.get() == 0:
            self._t_symbol.set(t_symbols[0])

        if self._t_guard.get() == 0:
            self._t_guard.set(t_guards[0])

        if self._mod_order.get() == 0:
            self._mod_order.set(mod_orders[0])

        if self._dis_tx_rx.get() == 0:
            self._dis_tx_rx.set(dis_tx_rx[0])

        # Symbol duration
        self._cb_t_symbol = tk.Checkbutton(master=top, variable=self._t_symbol_bool)
        self._label_t_symbol = tk.Label(master=top, text="Symbol duration:")
        self._entry_t_symbol = tk.OptionMenu(top, self._t_symbol, *t_symbols)
        self._label_unit_t_symbol = tk.Label(master=top, text="[s]")

        self._cb_t_symbol.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self._label_t_symbol.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self._entry_t_symbol.grid(row=0, column=2, padx=5, pady=5)
        self._label_unit_t_symbol.grid(row=0, column=3, padx=5, pady=5)

        # Guard interval
        self._cb_t_guard = tk.Checkbutton(master=top, variable=self._t_guard_bool)
        self._label_t_guard = tk.Label(master=top, text="Guard interval:")
        self._entry_t_guard = tk.OptionMenu(top, self._t_guard, *t_guards)
        self._label_unit_t_guard = tk.Label(master=top, text="[s]")

        self._cb_t_guard.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self._label_t_guard.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self._entry_t_guard.grid(row=1, column=2, padx=5, pady=5)
        self._label_unit_t_guard.grid(row=1, column=3, padx=5, pady=5)

        # Modulation order
        self._cb_mod_order = tk.Checkbutton(master=top, variable=self._mod_order_bool)
        self._label_mod_order = tk.Label(master=top, text="Modulation order:")
        self._entry_mod_order = tk.OptionMenu(top, self._mod_order, *mod_orders)

        self._cb_mod_order.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self._label_mod_order.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self._entry_mod_order.grid(row=3, column=2, padx=5, pady=5)

        # Use EX
        self._cb_use_ex = tk.Checkbutton(master=top, variable=self._use_ex_bool)
        self._label_use_ex = tk.Label(master=top, text="Use EX:")
        self._entry_use_ex = tk.OptionMenu(top, self._use_ex, "True", "False")

        self._cb_use_ex.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self._label_use_ex.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        self._entry_use_ex.grid(row=4, column=2, padx=5, pady=5)

        # Distance TX - RXX
        self._cb_dis = tk.Checkbutton(master=top, variable=self._dis_bool)
        self._label_dis = tk.Label(master=top, text="Distance TX - RX:")
        self._entry_dis = tk.OptionMenu(top, self._dis_tx_rx, *dis_tx_rx)

        self._cb_dis.grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self._label_dis.grid(row=5, column=1, padx=5, pady=5, sticky="w")
        self._entry_dis.grid(row=5, column=2, padx=5, pady=5)

        def _list_exp_filtered() -> None:
            filter_dict = dict()

            if self._t_symbol_bool.get():
                filter_dict["t_symbol"] = float(self._t_symbol.get())

            if self._t_guard_bool.get():
                filter_dict["t_guard"] = float(self._t_guard.get())

            if self._mod_order_bool.get():
                filter_dict["mod_order"] = int(self._mod_order.get())

            if self._use_ex_bool.get():
                filter_dict["use_ex"] = bool(self._use_ex.get())

            if self._dis_bool.get():
                filter_dict["dis_tx_rx"] = float(self._dis_tx_rx.get())

            self._set_list_entries(**filter_dict)
            top.destroy()


        self._apply_button = tk.Button(master=top, text="Apply", command=_list_exp_filtered)
        self._apply_button.grid(row=6, column=0, columnspan=4, padx=5, pady=5)

    def _confirm_event(self) -> None:
        self._root_win.quit()

    def get_selected_exp_data(self) -> list[dict]:
        ret_list = list()

        for date_exp_str in self._selected_list.get(0, "end"):
            date_exp_str = date_exp_str.split(')')
            date = date_exp_str[0].replace('(', '')
            exp_name = date_exp_str[1][1:]
            exp_list =  self._database.get_data(date=date, experiment_name=exp_name)

            if len(exp_list) == 0:
                raise ValueError(f"'{date_exp_str}' could not be found.")

            ret_list.extend(exp_list)

        return ret_list
    
    def get_selected_exp(self) -> list[str]:
        return self._selected_list.get(0, "end")

    def close(self) -> None:
        try:
            self._root_win.destroy()
        except:
            pass