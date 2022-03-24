#include "pybindings.h"
#include "../version.h"
#include "../types.h"
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
}
