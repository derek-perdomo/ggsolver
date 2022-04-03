# Add path
import os.path
import sys
sys.path.append(os.path.dirname(__file__))

# Import ggsolver
from ggsolver import *


class Entity(TEntity):
    def __init__(self, name, attr_map=None):
        map = {"name": name}
        if attr_map is not None:
            assert "name" not in attr_map, "`name` is a reserved attribute. Do not include it in `attr_map` parameter. "
            map.update(attr_map)

        super(Entity, self).__init__(map)

    def __str__(self):
        return f"{self.__class__.__name__}({self.__getattr__('name')})"

    def __getattr__(self, item):
        print(f"(py) {self.__class__.__name__}.__getattr__", item)
        try:
            val = self.get_attr(item)
            print(val)
            return val.get_object()
        except Exception as err:
            print(err)

    def __setattr__(self, key, value):
        print(f"(py) {self.__class__.__name__}.__setattr__: ", key)
        self.set_attr(key, value)

    def is_special_attr(self, key):
        if isinstance(key, str):
            return super(Entity, self).is_special_attr(key)


class Node(TNode):
    def __init__(self, name, attr_map=None):
        map = {"name": name}
        if attr_map is not None:
            assert "name" not in attr_map, "`name` is a reserved attribute. Do not include it in `attr_map` parameter. "
            map.update(attr_map)

        super(Node, self).__init__(map)

    def __str__(self):
        return f"Node({self.__getattr__('name')})"

    def __getattr__(self, item):
        print("(py) Node.__getattr__", item)
        try:
            val = self.get_attr(item)
            print(val)
            return val.get_object()
        except Exception as err:
            print(err)

    def __setattr__(self, key, value):
        print("(py) Node.__setattr__: ", key)
        self.set_attr(key, value)



if __name__ == '__main__':
    ent0 = Node("ent0")
    print(f"(py) ent0.get_type('__entity__'): {ent0.get_type('__entity__')}")
    # ent1 = Entity("ent1")
    # print(f"(py) ent0.get_attr_list()={ent0.get_attr_list()}")
    # print(f"(py) ent1.get_attr_list()={ent1.get_attr_list()}")
    # ent1.tmp = ent0
    # print(ent1.get_attr_list())
    # print("---", str(ent1.tmp))
    # # ent1.tmp.my_func()
    #
    # ent1.tmp = 10
    # print("---", str(ent1.__entity__))

    # n1 = TNode()
    # n2 = TNode({"nbr": n1})
    #
    # print("n1: ", n1.get_attr_list())
    # print("n2: ", n2.get_attr_list())
    #
    # node = n2.get_attr("nbr")
    # node = node.get_object()
    # print(type(n1), type(node))



