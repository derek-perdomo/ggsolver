import sys, os
ggsolver_tests_python_dir = os.path.dirname(os.path.abspath(__file__))
ggsolver_dir = os.path.dirname(os.path.dirname(ggsolver_tests_python_dir))
ggsolver_build_pybindings_dir = os.path.join(ggsolver_dir, "build", "pybindings")
sys.path.insert(0, sys.path.append(ggsolver_build_pybindings_dir))
print(ggsolver_tests_python_dir, ggsolver_build_pybindings_dir)

import pytest


@pytest.fixture
def SetUp():
    import ggsolver
    return ggsolver


def test_Version(SetUp):
    ggsolver = SetUp
    assert ggsolver.Version() == "0.1.0"


def test_PybindJson(SetUp):
    ggsolver = SetUp
    
    ggsolver.take_json({"name": 20})
    assert ggsolver.return_json()["value"] == 1


def test_Entity(SetUp):
    ggsolver = SetUp
    
    # Default instantiation
    _ = ggsolver.TEntity()

    # Instantiation with name
    ent0 = ggsolver.TEntity()
    # assert ent0.HasAttr("name")
    # assert ent0.GetAttr("name") == "namedEntity"

    # Instantiation with name and identity attributes
    ent1 = ggsolver.TEntity({ "planet": "earth", "windows": ent0})
    #assert ent1.HasAttr("name")
    assert ent1.HasAttr("planet")
    assert ent1.HasAttr("windows")
    assert ent1.IsReadOnlyAttr("name")
    assert ent1.IsReadOnlyAttr("planet")
    assert ent1.GetAttr("planet") == "earth"
    assert ent1.GetAttr("windows") == 10

    # Copy constructor
    ent2 = ggsolver.TEntity(ent1)
    assert ent2.HasAttr("name")
    assert ent2.HasAttr("planet")
    assert ent2.HasAttr("windows")
    assert ent2.IsReadOnlyAttr("name")
    assert ent2.IsReadOnlyAttr("planet")
    assert ent2.GetAttr("planet") == "earth"
    assert ent2.GetAttr("windows") == 10

    # Construction from jsonified (in python: dict) id properties
    id_attr = { "planet": "earth", "windows": 10, "entity": ent0}
    # id_attr = { "planet": "earth", "windows": 10}


    ent4 = ggsolver.TEntity(id_attr)
    assert ent4.HasAttr("name") == False
    assert ent4.HasAttr("planet")
    assert ent4.HasAttr("windows")
    assert ent4.IsReadOnlyAttr("name") == False
    assert ent4.IsReadOnlyAttr("planet")
    assert ent4.GetAttr("planet") == "earth"
    assert ent4.GetAttr("windows") == 10
    
    # We need this hack for now.
    retEnt = ent4.GetAttr("entity")
    entTmp = ggsolver.TEntity(retEnt)
    assert entTmp == ent0

    # Construction from jsonified TEntity object
    ent5 = ggsolver.TEntity(ent4.Serialize())
    print(str(ent5))
    assert ent5.HasAttr("name") == False
    assert ent5.HasAttr("planet")
    assert ent5.HasAttr("windows")
    assert ent5.IsReadOnlyAttr("name") == False
    assert ent5.IsReadOnlyAttr("planet")
    assert ent5.GetAttr("planet") == "earth"
    assert ent5.GetAttr("windows") == 10
    
    # We need this hack for now.
    print(ent2.Serialize())
    print(ent5.GetAttr("entity"))
    retEnt = ent5.GetAttr("entity")
    entTmp = ggsolver.TEntity(retEnt)
    assert entTmp == ent0

    # Test set attributes
    ent5.SetAttr("bool", True, False)
    ent5.SetAttr("int", 10, False)
    ent5.SetAttr("double", 0.1, False)
    ent5.SetAttr("str", "ok", False)
    ent5.SetAttr("json", {"key0": "value"}, False)


if __name__ == "__main__":
    import ggsolver 

    ent1 = ggsolver.TEntity()
    ent2 = ggsolver.TEntity("named entity")
    ent3 = ggsolver.TEntity({"name": "named entity", "attr": 10})
    print("OK")
    ent4 = ggsolver.TEntity({"name": ent1})
    print(ent4.HasAttr("name"))

    # print(ent1.Serialize())
    # print(ent2.Serialize())
    # print(ent3.Serialize())

    # print()
    # obj = {'__ggsolver_attr': {
    #             'attr': 10, 
    #             'name': 'named entity'
    #             }, 
    #         '__ggsolver_header': {
    #             '__ggsolver_apiversion': '0.1.0', 
    #             '__ggsolver_class': ['ggsolver.core.TEntity'], 
    #             '__ggsolver_idattr': ['attr', 'name'], 
    #             '__ggsolver_readonly': ['attr', 'name']
    #             }
    #       }

    # ent = ggsolver.TEntity(obj)
    # print(ent.Serialize())

