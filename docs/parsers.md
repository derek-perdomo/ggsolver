## Parsers

### Propositional logic (`pl.lark, pl.py`)

$$
\varphi := \mathsf{true} \mid \mathsf{false} \mid \neg \varphi \mid \varphi \lor \varphi
$$

The operators defined.

* Atoms. `[a-z][a-z 0-9_]*`    [**Note.** We do not allow any capital letters in proposition names.]

* Negation. `~` or `!`

* Or. `|` or `||`

* And. `&` or `&&`

* Implies. `->` or `=>`

* Equivalence. `<->` or `<=>`

  



### Syntactically Co-safe Linear Temporal Logic (`scltl.lark, scltl.py`)

$$
\varphi := p \mid \neg p \mid \varphi \land \varphi \mid \varphi \lor \varphi \mid X\varphi \mid \varphi \mathsf{U} \varphi
$$



**Constraint.** Negation only appears in front of atoms, when formula is written in positive normal form. 

**Remark.** For the ggsolver parser, we assume formula is given in PNF. 



In addition to PL, ScLTL has the following new operators:

* Next. `X`
* 9Always. `G`
* Eventually. `F`





