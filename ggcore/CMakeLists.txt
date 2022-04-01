# CMakeList.txt : CMake project for ggcore, include source and define
# project specific logic here.
#
cmake_minimum_required (VERSION 3.8)

# Add source to this project's executable.
set(GGCORE_HEADERS
	"entity.h"
	"version.h"
	"types.h"
)

# Define ggcore libraries
add_library (ggcore INTERFACE)
target_include_directories(ggcore INTERFACE ${GGCORE_DIRS})

# Generate python bindings
add_subdirectory("python")
message("Configured for python bindings.")

#add_executable(main "main.cpp")
add_executable(main "test_types.cpp")
target_link_libraries(main PUBLIC snapcore pybind11::embed pybind11::module pybind11::lto pybind11::windows_extras)
