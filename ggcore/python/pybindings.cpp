#include "pybindings.h"
#include "../version.h"
#include "../types.h"
//#include "../entity.h"
#include "../graph.h"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>


using namespace ggsolver;
using namespace pybind11::literals;
namespace py = pybind11;


PYBIND11_MODULE(ggsolver, m) {

	// Public methods
	m.def("Version", &ggsolver_version);

    // TValue::Type (Enum class)
    py::enum_<Type>(m, "TValueType")
            .value("py_none", Type::py_none)
            .value("py_bool", Type::py_bool)
            .value("py_int", Type::py_int)
            .value("py_float", Type::py_float)
            .value("py_str", Type::py_str)
            .value("py_function", Type::py_function)
            .value("py_tuple", Type::py_tuple)
            .value("py_list", Type::py_list)
            .value("py_set", Type::py_set)
            .value("py_dict", Type::py_dict)
            .value("py_object", Type::py_object)
            .value("gg_t_entity", Type::gg_t_entity)
            .export_values();

    // TValue class
    py::class_<TValue, std::shared_ptr<TValue>>(m, "TValue")
            .def(py::init<const bool&>())
            .def(py::init<const long&>())
            .def(py::init<const double&>())
            .def(py::init<const std::string&>())
            .def(py::init<const PEntity&>())
            .def(py::init<const std::vector<PValue>&>())
            .def(py::init<const std::unordered_set<PValue>&>())
            .def(py::init<const std::unordered_map<std::string, PValue>&>())
            .def(py::init<const py::handle&>())
            .def("set_object", &TValue::set_object)
            .def("set_entity", &TValue::set_entity)
            .def("get_type", &TValue::get_type)
            .def("get_object", &TValue::get_object)
            .def("get_function", &TValue::get_function<py::function>)
            .def("get_entity", &TValue::get_entity<TEntity>)
            ;

    // Entity class
    py::class_<TEntity, std::shared_ptr<TEntity>>(m, "TEntity")
            .def(py::init<>())
            .def(py::init<const py::handle&>())
            .def(py::init<const TAttrMap&>())
            .def("is_reserved_attr", &TEntity::is_reserved_attr)
            .def("has_attr", &TEntity::has_attr)
            .def("get_type", &TEntity::get_type)
            .def("get_attr", &TEntity::get_attr)
            .def("get_attr_list", &TEntity::get_attr_list)
            .def("set_attr", py::overload_cast<const std::string&, const py::handle&>(&TEntity::set_attr))
            .def("set_attr", py::overload_cast<const std::string&, PValue>(&TEntity::set_attr))
            ;


    py::class_<TNode, std::shared_ptr<TNode>, TEntity>(m, "TNode")
            .def(py::init<>())
            .def(py::init<const py::handle&>())
            .def(py::init<const TAttrMap&>())
            .def("get_nid", &TNode::get_nid)
            ;


    py::class_<TEdge, std::shared_ptr<TEdge>, TEntity>(m, "TEdge")
            .def(py::init<>())
            .def(py::init<const TAttrMap&>())
            .def(py::init<const py::handle&>())
            .def("get_eid", &TEdge::get_eid)
            .def("get_uid", &TEdge::get_uid)
            .def("get_vid", &TEdge::get_vid)
            ;


    py::class_<TGraph, std::shared_ptr<TGraph>>(m, "TGraph")
            .def(py::init<>())
            .def("add_node", py::overload_cast<>(&TGraph::add_node))
            .def("add_node", py::overload_cast<const py::handle&>(&TGraph::add_node))
            .def("add_node", py::overload_cast<const TAttrMap&>(&TGraph::add_node))
            .def("add_edge", py::overload_cast<const unsigned long&, const unsigned long&>(&TGraph::add_edge))
            .def("add_edge", py::overload_cast<const unsigned long&, const unsigned long&, const TAttrMap&>(&TGraph::add_edge))
            .def("add_edge", py::overload_cast<const unsigned long&, const unsigned long&, const py::handle&>(&TGraph::add_edge))
            .def("add_edge", py::overload_cast<const PNode&, const PNode&>(&TGraph::add_edge))
            .def("add_edge", py::overload_cast<const PNode&, const PNode&, const TAttrMap&>(&TGraph::add_edge))
            .def("add_edge", py::overload_cast<const PNode&, const PNode&, const py::handle&>(&TGraph::add_edge))
            .def("add_nodes_from", py::overload_cast<const unsigned long&>(&TGraph::add_nodes_from))
            .def("add_nodes_from", py::overload_cast<const std::vector<py::handle>&>(&TGraph::add_nodes_from))
            .def("add_nodes_from", py::overload_cast<const std::vector<TAttrMap>&>(&TGraph::add_nodes_from))
            .def("add_edges_from", py::overload_cast<std::vector<std::pair<unsigned long, unsigned long>>>(&TGraph::add_edges_from))
            .def("add_edges_from", py::overload_cast<std::vector<std::pair<PNode, PNode>>>(&TGraph::add_edges_from))
            .def("add_edges_from", py::overload_cast<std::vector<std::tuple<unsigned long, unsigned long, TAttrMap>>>(&TGraph::add_edges_from))
            .def("add_edges_from", py::overload_cast<std::vector<std::tuple<unsigned long, unsigned long, py::handle>>>(&TGraph::add_edges_from))
            .def("add_edges_from", py::overload_cast<std::vector<std::tuple<PNode, PNode, TAttrMap>>>(&TGraph::add_edges_from))
            .def("add_edges_from", py::overload_cast<std::vector<std::tuple<PNode, PNode, py::handle>>>(&TGraph::add_edges_from))
            .def("rem_node", py::overload_cast<const unsigned long&>(&TGraph::rem_node))
            .def("rem_node", py::overload_cast<const PNode&>(&TGraph::rem_node))
            .def("rem_nodes_from", py::overload_cast<std::vector<unsigned long>>(&TGraph::rem_nodes_from))
            .def("rem_nodes_from", py::overload_cast<std::vector<PNode>>(&TGraph::rem_nodes_from))
            .def("rem_edge", py::overload_cast<const unsigned long&>(&TGraph::rem_edge))
            .def("rem_edge", py::overload_cast<const PEdge&>(&TGraph::rem_edge))
            .def("rem_edges_from", py::overload_cast<std::vector<unsigned long>>(&TGraph::rem_edges_from))
            .def("rem_edges_from", py::overload_cast<std::vector<PEdge>>(&TGraph::rem_edges_from))
            .def("has_node", py::overload_cast<const PNode&>(&TGraph::has_node))
            .def("has_node", py::overload_cast<const unsigned long&>(&TGraph::has_node))
            .def("has_edge", py::overload_cast<const unsigned long&>(&TGraph::has_edge))
            .def("has_edge", py::overload_cast<const PEdge&>(&TGraph::has_edge))
            .def("nodes", &TGraph::nodes)
            .def("edges", &TGraph::edges)
            .def("in_edges", py::overload_cast<const unsigned long&>(&TGraph::in_edges))
            .def("in_edges", py::overload_cast<const PNode&>(&TGraph::in_edges))
            .def("out_edges", py::overload_cast<const unsigned long&>(&TGraph::out_edges))
            .def("out_edges", py::overload_cast<const PNode&>(&TGraph::out_edges))
            .def("successors", py::overload_cast<const unsigned long&>(&TGraph::successors))
            .def("successors", py::overload_cast<const PNode&>(&TGraph::successors))
            .def("predecessors", py::overload_cast<const unsigned long&>(&TGraph::predecessors))
            .def("predecessors", py::overload_cast<const PNode&>(&TGraph::predecessors))
            .def("number_of_nodes", &TGraph::number_of_nodes)
            .def("number_of_edges", &TGraph::number_of_edges)
            .def("size", &TGraph::size)
            .def("clear", &TGraph::clear)
            .def("reserve", &TGraph::reserve)
            .def("get_nodes_dict", &TGraph::get_nodes_dict)
            .def("get_edges_dict", &TGraph::get_edges_dict)
            ;

}
