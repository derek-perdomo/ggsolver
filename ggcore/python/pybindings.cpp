#include "pybindings.h"
#include "../version.h"
#include "../types.h"
#include "../entity.h"
//#include "../graph.h"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>


using namespace ggsolver;
using namespace pybind11::literals;
namespace py = pybind11;


PYBIND11_MODULE(ggsolver, m) {

	// Public methods
	m.def("Version", &Version);

    // Attribute Map
    py::class_<TAttrMap, std::shared_ptr<TAttrMap>>(m, "TAttrMap")
        .def(py::init<>())
        .def(py::init<json>())
        .def(py::init<py::dict>())
        .def("GetKeys", &TAttrMap::GetKeys)
        ;

    py::class_<TEntity, std::shared_ptr<TEntity>>(m, "TEntity")
            .def(py::init<>())
            .def("is_special_attr", &TEntity::is_special_attr)
            .def("has_attr", &TEntity::has_attr)
            .def("get_attr_type", &TEntity::get_attr_type)
            .def("get_attr", &TEntity::get_attr<json>)
            .def("set_attr", &TEntity::set_attr<json>)
            ;
}
