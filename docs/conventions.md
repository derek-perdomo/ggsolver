## Common Approach

All graphical models defined in `ggsolver` provide the following features

* `delta`: Transition function of the graphical model. 	
  * `delta(u, a) -> v` when model is deterministic.
  * `delta(u, a) -> subset(V)` when model is non-deterministic.
  * `delta(u, a) -> Dist(V)` when model is stochastic.

* `pred`: Given a state `v`, the predecessor function returns a set of `(u, d0, ..., dn)` pairs, such that `(u, v, d0, ..., dn)` determines a unique edge of graphical model. Associated edge properties `d0, ..., dn` must include edge defining parameters, but might also include any additional parameters needed by the user.
* `succ`: Given a state `u`, the successor function returns a set of `(v, d0, ..., dn)` pairs, such that `(u, v, d0, ..., dn)` determines a unique edge of graphical model. Associated edge properties `d0, ..., dn` must include edge defining parameters, but might also include any additional parameters needed by the user.

* `states(data=False)`: returns the set of states in graphical model. When the parameter `data` is set to `True`, the function returns the set `{(v, data_v)}`, otherwise returns the set `{v}`. 

  

All graphical models in `ggsolver` allow at least two modes of creation - `explicit` and `symbolic`. 

* In `explicit` mode, the user must provide a graph (`networkx.MultiDigraph()` object) in addition to other defining parameters of a graphical model. 
* In `symbolic` mode, the user must provide a `delta, pred` and `succ` functions in addition to other defining parameters of a graphical model. 



The `symbolic` mode allows users to build complex models on using simpler models; e.g., given a transition system and an automaton, a product game may be defined as follows. 

```python
game = DeterministicTSys()		# Placeholder.
aut = Automaton()				# Placeholder.

# Define delta function for product game.
def delta(v, a):
	s, q = v
    next_s = game.delta(s, a)
    next_q = aut.delta(q, game.label(next_s))
    return next_s, next_q

# Define predecessor function for product game
def pred(v):
    t, q = v
    pred_t = game.pred(t)
    pred_q = aut.pred(q)
    
    predecessors = set()
    for (s, data_st), (p, data_pq) in itertools.product(pred_t, pred_q):
        a = data_st["action"]
        sigma = data_pq["sigma"]
        if game.label(t) == sigma:
            predecessors.add(((s, p), a))
	
    return predecessors

# Define predecessor function for product game
def succ(u):
    s, p = u
    succ_s = game.succ(s)
    succ_p = aut.pred(p)
    
    successors = set()
    for (t, data_st), (q, data_pq) in itertools.product(succ_s, succ_p):
        a = data_st["action"]
        sigma = data_pq["sigma"]
        if game.label(t) == sigma:
            successors.add(((t, q), a))
	
    return successors

product_game = DeterministicTSys()
product_game.construct_symbolic(states, delta, pred, succ, ...)		
```

When graphical models are large, using symbolic approach is advisable since it saves a lot of memory. 



All graphical models can be serialized and deserialized into respective models. If a model is constructed symbolically, it must be made explicit before saving. For this purpose, the user must implement `make_explicit` method of the graphical model. Typically, this may involve generating all edges in the graph by iterating over all states. 

**Remark.** In most cases, saving the base graphical models and defining the complex graphical models symbolically using these models should suffice. For example, if `product_game` is defined symbolically as above, then it is sufficient to save the `game` and `aut` objects only. 





## Conventions

### Naming conventions

We follow PEP8 conventions. 



**Remark.** When using full words as class names: use `DeterministicAutomaton`. When using abbreviations as class names: use `Dfa` and not `DFA`. 





### Import statement sequence

Import statements are alphabetically ordered. Start with `import ...` statement, then followed by `from ... import ...` statements. 

```python
# import ... 
import abc
import itertools
import networkx as nx

# from ... import ... 
from abc import abstractmethod
```

