## Automata

### Base Automaton

Abstract base class for all automaton. 
$$
\mathcal{A} = \langle G, \Sigma, \delta, \mathsf{Pred}, \mathsf{Succ}, v_0, F, Acc \rangle
$$
where 

* $G = (V, E)$ is a directed multi-graph representing the nodes and edges of automaton graph;
* $\Sigma$ is the alphabet; 
* $\delta$ is a transition function - when automaton is deterministic, we have $\delta: V \times \Sigma \rightarrow V$, and when automaton is non-deterministic, we have $\delta: V \times \Sigma \rightarrow \mathcal{P}(V)$. Here, $\mathcal{P}$ stands for the powerset.
* $\mathsf{Pred}: S \rightarrow 2^{V \times \Sigma}$ is the predecessor function defined as following. Given $v \in V$, 
  * Case I. $\cal A$ is deterministic:  $\mathsf{Pred}(v) = \{(u, \sigma) \mid \delta(u, \sigma) = v\}$. 
  * Case II. $\cal A$ is non-deterministic:  $\mathsf{Pred}(v) = \{(u, \sigma) \mid \delta(u, \sigma) \cap \{v\} \neq \emptyset\}$. 
* $\mathsf{Succ}: S \rightarrow 2^{V \times \Sigma}$ is the successor function defined as follows. Given $u \in V$
  * Case I. $\cal A$ is deterministic:  $\mathsf{Succ}(u) = \{(v, \sigma) \mid \delta(u, \sigma) = v\}$. 
  * Case II. $\cal A$ is non-deterministic:  $\mathsf{Succ}(u) = \{(v, \sigma) \mid \delta(u, \sigma) \cap \{v\} \neq \emptyset\}$. 
* $v_0 \in V$ is a unique initial state of the automaton. 

* $F, Acc$ define the set of final states and acceptance condition of the automaton. These will be fixed in the specialized classes that derive from `BaseAutomaton`. 



### Deterministic Finite Automaton

DFA is a `BaseAutomaton` with `REACHABILITY` acceptance condition and a requirement that `final` must be a set.





