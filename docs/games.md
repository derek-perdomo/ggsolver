# Game objects

All game models in `ggsolver` are derived from `BaseGame` class, which defines common methods and properties shared by all games on played on graph-based transition systems. 
$$
\mathcal{G} = \langle G, A, \delta, \mathsf{pred}, \mathsf{succ} \rangle
$$


A game instance is created using following steps. 

* Instantiate game object. E.g. `game = Game()`
* Use `construct_XXX()` method to construct game. E.g. `game.construct_explicit(...)` 
* Add features to game using `make_XXX()` methods. E.g. `game.make_labeled(...)`
* Associate additional properties with game using `game.set_XXX(value)` methods. 

It is noted that different game models will have different `construct, make, set` definitions. Refer to respective documentation for more information. 



## Deterministic Two-player Turn-based Game

A deterministic two-player turn-based game is `BaseGame` with the following additional requirements.

1. All states must have a `turn` attribute. 
2. All edges must have an `action` attribute.
3. Transition function $\delta$ is deterministic. 



```pseudocode
Function SureWin(G, F, p)
	Attractor <- List()			// Level set of winning states of player p.
	Strategy <- Map()			// Set of winning edges for player p.
	While True
		If p = 1
			Sp, Ep <- Pre(Attractor, 1)
		Else p = 2
			Sp, Ep <- Pre(Attractor, 2)
		End If
		if Sp is empty
			Exit loop
		Add Sp to Attractor
		Update Strategy with Ep
	End While
	Return Attractor, Strategy
End Function 
```




```pseudocode
Function Pre(Z, p)
	Sp <- Set()
	Ep <- Map() 
	Y <- {s | there exists k s.t. s in Z[k]}
	For v in Y
		U <- G.pred(u)
		For u, _ in U
			T <- G.post(u)
			X <- Set.Intersection(Y, {t for t, _ in T})
			turn <- G.get_property(u, "turn")
			If turn == p and len(X) > 0
				Add u to Sp
				For t In X:
					Add (u, a, t) to Ep
			Else turn != p and len(X) == len(T)
				Add u to Sp
				For t In X:
					Add (u, a, t) to Ep
```



## Game on Markov Decision Process

A game on Markov decision process is `BaseGame` with the following additional requirements.

1. All edges must have an `action` attribute.
2. Transition function $\delta$ is deterministic. 



```pseudocode
Function ASWinReach(G, F)
	U <- {s | F is unreachable from s in graph G}
	L <- Set()
	Loop  
		R <- U
		While R is not empty
			u <- R.pop()
			For every t, a in G.pred(u) such that t not in U
				Remove a from EnabledActs(t)
				If EnabledActs(t) is empty
					Add t to R
					Add t to U
			Clear EnabledActs(u)
			Add u to L
		B <- {s | F is unreachable from s given new EnabledActs}
		U <- Set.Intersection(S - U, B)
    Until U is empty
	Return S - L
```



```pseudocode
Function ASLoseReach(G, F)
	T <- F
	R <- F
	While R is not empty
		t <- R.pop()
		For s, a in G.pred(t) such that t not in T
			Remove a from EnabledActs(s)
			If EnabledActs(s) is empty
				Add s to R
				Add s to T
	Return T
```



```pseudocode
Function PWinReach(G, F)
	P <- Set(F)
	Q <- List(F)
	W <- Set()
	Pi <- Map()
	While P is not empty
		u <- Q.pop(0)
		Remove u from P
		Add u to W
		For v, a in G.succ(u)
			If v in W
				Add a to Pi[u]
	return W, Pi
```



## Stochastic Two-player Turn-based Game

A stochastic two-player turn-based game is `MdpGame` with the following additional requirements.

1. All states must have a `turn` attribute. 



We use the following algorithms to compute almost-sure and positive winning for reachability objectives. 

```pseudocode
Function ASWinReach(G, F)
	U <- List({F})									  				// Level-set
	C <- List()														// Level-set
	gamma1 <- {s: {all a in A} for all s in G and turn(s) = 1}		// All P1 actions are enabled
	gamma2 <- {s: {all a in A} for all s in G and turn(s) = 2}		// All P2 actions are enabled
	Loop
		Y <- Safe2(U[-1] - F, gamma1, gamma2)
		Z <- Safe1(U[-1] - Y, gamma1, gamma2)
		gamma1 <- Stay1(Z, gamma1, gamma2)
		Add Y to C
		Add Z to U
	Until U[-1] != U[-2]
```

```
Function PWinReach(G, F)
	U <- List({F})									  				// Level-set
	C <- List()														// Level-set
    gamma1 <- {s: {all a in A} for all s in G and turn(s) = 1}		// All P1 actions are enabled
	gamma2 <- {s: {all a in A} for all s in G and turn(s) = 2}		// All P2 actions are enabled
	Loop
		Y <- Safe2(U[-1] - F, gamma1, gamma2)
		Z <- Safe1(U[-1] - Y, gamma1, gamma2)
		gamma1 <- Reach1(Z, gamma1, gamma2)
		Add Y to C
		Add Z to U
	Until U[-1] != U[-2]
```

**Note.** The only difference between `ASWin` and `PWin` algorithms is on line 9. This is because, for an action to be positive winning, it is sufficient that it enters `Z` with a positive probability. Thus, we modify `Stay` algorithm from de Alfaro's paper to define `Reach` algorithm.



 The helper functions are defined as follows.

```pseudocode
Function Safe1(U, gamma1, gamma2)
	V <- List()				// Level set
	Loop		
		Y1 <- Set()		
		For s in G.states()
			If G.turn(s) = 1 
				If Exists(G.delta(s, a) is subset of V for a in gamma1[s])
					Add s to Y1
		Y2 <- {s for s in G.states() if turn(s) = 2 and G.succ(s) is subset of V}
		Y <- Set.Intersection(Y, Set.Union(Y1, Y2))
		Add Y to V
	Until V[-1] = V[-2]		
```

```pseudocode
Function Safe2(U, gamma1, gamma2)
	V <- List()				// Level set
	Loop
		Y1 <- {s for s in G.states() if turn(s) = 1 and G.succ(s) is subset of V}
		Y2 <- Set()		
		For s in G.states()
			If G.turn(s) = 2 
				If Exists(G.delta(s, a) is subset of V for a in gamma2[s])
					Add s to Y2
		Y <- Set.Intersection(Y, Set.Union(Y1, Y2))
		Add Y to V
	Until V[-1] = V[-2]		
```

```pseudocode
Function Stay1(U, gamma1, gamma2)
    For u in G.states() and turn(u) == 1
        For a in gamma1[u]:
            If game.delta(u, a) is not subset of U
	            remove a from gamma1[a]
	return gamma1
```

```pseudocode
Function Stay2(U, gamma1, gamma2)
    For u in G.states() and turn(u) == 2
        For a in gamma2[u]:
            If game.delta(u, a) is not subset of U
	            remove a from gamma2[a]
	return gamma2
```

```pseudocode
Function Reach1(U, gamma1, gamma2)
    For u in G.states() and turn(u) == 1
        For a in gamma1[u]:
            If set.intersection(game.delta(u, a), U) is not empty
	            remove a from gamma1[a]
	return gamma1
```

```pseudocode
Function Reach2(U, gamma1, gamma2)
    For u in G.states() and turn(u) == 2
        For a in gamma2[u]:
            If set.intersection(game.delta(u, a), U) is not empty
	            remove a from gamma2[a]
	return gamma2
```

