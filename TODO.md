# TODO List

+ Support serialization, deserialization of automata to 
  `graphml` and `cyjs` formats.
+ Refactor `validate_graph`. May call it `validate_game` or something like it.
+ All `delta, pred, succ` must return list of tuples. This will allow returning 
  data dictionaries.
+ Replace `{s for s, _ in game.delta/pred/succ(...)}` with yield statements.
  Introduce helper `get_states(game.delta/pred/succ(...))` to get yield states. 
  Motive is to allow returning data dictionaries and ease of access for users.
+ Optimize solvers. E.g. `stptb.ASWinReach, stptb.PWinReach` have a lot of common code. 
