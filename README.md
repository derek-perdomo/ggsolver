# ggsolver 


# User Tips

## Creating a new graphical model

To create a new graphical model, inherit from the relevant model in `models.py`.
For instance, the following template shows how to define a new game.  

```python


class MyGame(Game):
    NODE_PROPERTY = Game.NODE_PROPERTY.copy()
    EDGE_PROPERTY = Game.EDGE_PROPERTY.copy()
    GRAPH_PROPERTY = Game.GRAPH_PROPERTY.copy()
    
    ...
```

The `NODE_PROPERTY, EDGE_PROPERTY, GRAPH_PROPERTY` register the node, edge and graph 
properties to be serialized. To mark a function as node property, 

```python
from ggsolver.models import Game, register_property

class MyGame(Game):
    NODE_PROPERTY = Game.NODE_PROPERTY.copy()
    EDGE_PROPERTY = Game.EDGE_PROPERTY.copy()
    GRAPH_PROPERTY = Game.GRAPH_PROPERTY.copy()
    
    @register_property(NODE_PROPERTY)
    def state_property(self, state):
        return "value"
    
    @register_property(EDGE_PROPERTY)
    def transition_property(self, from_state, action, to_state):
        return "value"
    
    @register_property(GRAPH_PROPERTY)
    def graph_property(self):
        return "value"
```







