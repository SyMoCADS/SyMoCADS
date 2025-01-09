[mmtb](../../README.md)/[dtypes](../dtypes.md)/TransmissionParameters

# mmtb.dtypes.TransmissionParameters

**class** $\color{purple}TransmissionParameters$  (t_symbol: float, t_guard: float, mod_type: str, mod_order: int, symbol_map: dict[str, float], symbol_string: str, n_reps: int, tx_leds: list[int], ex_intensity: float, ex_leds: list[int])

> Parameters

+ `t_symbol: float`
+ `t_guard: float`
+ `mod_type: str`
+ `mod_order: int`
+ `symbol_map: dict[str, float]`
+ `symbol_string: str`
+ `n_reps: int`
+ `tx_leds: list[int]`
+ `ex_intensity: float`
+ `ex_leds: list[int]`

> Attributes

+ `t_symbol: float`
+ `t_irradiation: float`
+ `t_guard: float`
+ `mod_type: str`
+ `mod_order: int`
+ `symbol_map: dict[str, float]`
+ `symbol_string: str`
+ `total_symbol_string: str` (symbol_string * n_reps)
+ `n_reps: int`
+ `n_symbols: int` (len(symbol_string) * n_reps)
+ `tx_leds: list[int]`
+ `ex_intensity: float`
+ `ex_leds: list[int]`