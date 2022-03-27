#include "pybindings.h"
#include "../version.h"
#include "../types.h"
#include "../entity.h"
#include "../graph.h"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>


using namespace ggsolver;
using namespace pybind11::literals;
namespace py = pybind11;


PYBIND11_MODULE(ggsolver, m) {

	// Public methods
	m.def("Version", &Version);

    // Attribute Map
    py::class_<TEntity, std::shared_ptr<TEntity>>(m, "TEntity")
            .def(py::init<>())
            .def("is_special_attr", &TEntity::is_special_attr)
            .def("has_attr", &TEntity::has_attr)
            .def("get_attr_type", &TEntity::get_attr_type)
            .def("get_attr", &TEntity::get_attr<json>)
            .def("set_attr", &TEntity::set_attr<json>)
            ;

    py::class_<TNode, std::shared_ptr<TNode>>(m, "TNode")
            .def(py::init<>())
            .def("is_special_attr", &TNode::is_special_attr)
            .def("has_attr", &TNode::has_attr)
            .def("get_attr_type", &TNode::get_attr_type)
            .def("get_attr", &TNode::get_attr<json>)
            .def("set_attr", &TNode::set_attr<json>)
            .def("get_node_id", &TNode::get_node_id)
            ;

    py::class_<TEdge, std::shared_ptr<TEdge>>(m, "TEdge")
            .def(py::init<>())
            .def("is_special_attr", &TEdge::is_special_attr)
            .def("has_attr", &TEdge::has_attr)
            .def("get_attr_type", &TEdge::get_attr_type)
            .def("get_attr", &TEdge::get_attr<json>)
            .def("set_attr", &TEdge::set_attr<json>)
            .def("get_edge_id", &TEdge::get_edge_id)
            .def("get_uid", &TEdge::get_uid)
            .def("get_vid", &TEdge::get_vid)
            ;

    py::class_<TGraph, std::shared_ptr<TGraph>>(m, "TGraph")
            .def(py::init<>())
            .def("add_node", py::overload_cast<>(&TGraph::add_node))
            .def("add_node", py::overload_cast<const json&>(&TGraph::add_node))
            .def("add_edge", py::overload_cast<const unsigned long&, const unsigned long&>(&TGraph::add_edge))
            .def("add_edge", py::overload_cast<const unsigned long&, const unsigned long&, const json&>(&TGraph::add_edge))
            .def("add_edge", py::overload_cast<const PNode&, const PNode&>(&TGraph::add_edge))
            .def("add_edge", py::overload_cast<const PNode&, const PNode&, const json&>(&TGraph::add_edge))
            .def("add_nodes_from", py::overload_cast<const unsigned long&>(&TGraph::add_nodes_from))
            .def("add_nodes_from", py::overload_cast<const std::vector<json>&>(&TGraph::add_nodes_from))
            .def("add_edges_from", py::overload_cast<std::vector<std::pair<unsigned long, unsigned long>>>(&TGraph::add_edges_from))
            .def("add_edges_from", py::overload_cast<std::vector<std::pair<PNode, PNode>>>(&TGraph::add_edges_from))
            .def("add_edges_from", py::overload_cast<std::vector<std::tuple<unsigned long, unsigned long, json>>>(&TGraph::add_edges_from))
            .def("add_edges_from", py::overload_cast<std::vector<std::tuple<PNode, PNode, json>>>(&TGraph::add_edges_from))
            .def("has_node", py::overload_cast<const PNode&>(&TGraph::has_node))
            .def("has_node", py::overload_cast<const unsigned long&>(&TGraph::has_node))
            .def("has_attr", &TGraph::has_attr)
            .def("get_attr_type", &TGraph::get_attr_type)
            .def("get_attr", &TGraph::get_attr<json>)
            .def("set_attr", &TGraph::set_attr<json>)
            ;

}
