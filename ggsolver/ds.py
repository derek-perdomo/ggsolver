# Add path
import os.path
import sys
sys.path.append(os.path.dirname(__file__))

# Import ggsolver
from ggsolver import *


class Entity(TEntity):
    def __init__(self, name, attr_map=None):
        map = {"name": name, "__entity__": "Entity"}
        if attr_map is not None:
            assert "name" not in attr_map and "__entity__" not in attr_map
            map.update(attr_map)
        super(Entity, self).__init__(map)

    def __str__(self):
        return f"Entity(name: {self.__getattr__('name')})"

    def __getattr__(self, item):
        val = super(Entity, self).get_attr(item)
        if val.get_type() == TValueType.gg_entity:
            return construct_entity(val.get_entity())
        else:
            return val.get_object()

    def __setattr__(self, key, value):
        # print(key, value)
        super(Entity, self).set_attr(key, value)

    def is_special_attr(self, key):
        if isinstance(key, str):
            return super(Entity, self).is_special_attr(key)

# class Graph(Entity, TGraph):


def construct_entity(entity):
    class_ = entity.entity_
    # TODO: use globals() to find appropriate class
    # TODO: use __new__ to construct object of appropriate class
    # TODO: use entity attributes to update __dict__
    return entity


if __name__ == '__main__':
    ent0 = Entity("ent0")
    ent1 = Entity("ent1")
    print(dir(ent0))
    ent1.__setattr__("tmp", ent0)
    # print(str(ent0.my_attr))

