from ggsolver import TGraph
import types

JSON_TYPES = (
    bool,
    int,
    float,
    str,
    list,
    tuple,
    set,
    dict,
)


def serialize(value):
    print("serialzie--------------")
    if "__getstate__" in dir(value):
        print("value get state", value.__getstate__())
        value_dict = value.__getstate__()
    elif "__dict__" in dir(value):
        print("value dict", value.__dict__)
        value_dict = value.__dict__
    else:
        raise AttributeError(f"serialize:: value = {value} is not serializable.")

    for key in value_dict:
        if not (value_dict[key] is None or isinstance(value_dict[key], JSON_TYPES)):
            value_dict[key] = serialize(value_dict[key])

    value_dict["_gg_class"] = value.__class__.__name__
    print("serialized: ", value_dict)
    return value_dict


def unserialize(value_dict):
    class_name = value_dict["_gg_class"]
    print("class_name", class_name)
    class_ = globals()[class_name]
    obj = class_.__new__(class_)
    obj.__dict__.update(value_dict)
    print(obj)
    return obj


class Graph(TGraph):
    def __init__(self, name):
        super(Graph, self).__init__()
        self.__setattr__("name", name)

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return f"Graph({self.name})"

    # def __setstate__(self, state):
    #     pass
    #
    # def __getstate__(self):
    #     pass

    def __setattr__(self, key, value):
        if key in dir(self):
            raise AttributeError(f"Cannot overwrite C++ bound functions.")
        if key in ("nodes", "edges", "graph"):       # Needs to be synced with `m_special_attr_names` in graph.h
            raise AttributeError(f"Cannot set values of specialized attributes of {repr(self)}.")

        if value is None or isinstance(value, JSON_TYPES):
            super(Graph, self).set_attr(key, value)
        else:
            try:
                serialized_value = serialize(value)
            except AttributeError:
                raise AttributeError(f"Graph.__setattr__: value: {value} is not a JSON_TYPE and cannot be serialized.")

    def __getattr__(self, item):
        if item == "nodes":
            return super(Graph, self).get_nodes_factory()
        elif item == "edges":
            return super(Graph, self).get_edges_factory()
        elif item == "graph":
            raise AttributeError(f"Cannot access `graph` attribute in {repr(self)} because it is not bound.")
        else:
            # TODO If value type is Entity, deserialize it.
            return super(Graph, self).get_attr(item)

    def add_node(self, n):
        pass

    def add_edge(self, e):
        pass

    def add_nodes_from(self, nodes):
        pass

    def add_edges_from(self, edges):
        pass

    def rem_node(self, node):
        pass

    def rem_edge(self, edge):
        pass

    def has_node(self, node):
        pass

    def has_edge(self, edge):
        pass


if __name__ == '__main__':
    graph = Graph("new graph")

    # Test str, repr.
    print(repr(graph))
    print(str(graph))

    # Testing getattr, setattr
    graph.mysize = (10, 20)
    print(graph.mysize)

    g = serialize(graph)
    unserialize(g)