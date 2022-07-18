
def register_property(ptype):
    def register_function(func):
        ptype[func.__name__] = func
        return func
    return register_function


class A:
    NODE_PROPERTY = dict()
    EDGE_PROPERTY = dict()
    GRAPH_PROPERTY = dict()

    @register_property(NODE_PROPERTY)
    def foo(self):
        print(10)


class B(A):
    NODE_PROPERTY = A.NODE_PROPERTY.copy()

    @register_property(NODE_PROPERTY)
    def bar(self):
        print(10)

    def foo(self):
        print(20)


print(A.NODE_PROPERTY)
print(B.NODE_PROPERTY)
