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

}
