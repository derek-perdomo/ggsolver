## Game objects

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



### Deterministic Two-player Turn-based Game

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

