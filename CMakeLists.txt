# CMakeList.txt : Top-level CMake project file, do global configuration
# and include sub-projects here.
#
cmake_minimum_required (VERSION 3.8)
project ("ggcore")
set(CMAKE_CXX_STANDARD 17)

# Define important directories
set(GGCORE_DIRS "${CMAKE_CURRENT_SOURCE_DIR}/ggcore")
set(GGCORE_TESTS "${CMAKE_CURRENT_SOURCE_DIR}/tests")
set(THIRD_PARTY_DIR "${CMAKE_CURRENT_SOURCE_DIR}/thirdparty")
set(PYTHON_LIBRARY_DIR "${CMAKE_CURRENT_SOURCE_DIR}/ggsolver")
set(LIBRARY_OUTPUT_PATH  "${CMAKE_CURRENT_SOURCE_DIR}/build/lib")

# Set compile options
if(CMAKE_SYSTEM_NAME STREQUAL "Windows")
   add_compile_options("/D_ITERATOR_DEBUG_LEVEL=0") 
   add_compile_options("/MT") 
elseif(CMAKE_SYSTEM_NAME STREQUAL "Linux")
    #set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -fPIC -O3 -DNDEBUG -fopenmp -fmax-errors=1 -g")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -fPIC -O3 -DNDEBUG -fopenmp -g")
endif(CMAKE_SYSTEM_NAME STREQUAL "Windows")

# Pybind11 library 
find_package(PythonLibs 3)
message("PythonLibs ${PYTHONLIBS_FOUND} with version ${PYTHONLIBS_VERSION_STRING}")
if (${PYTHONLIBS_VERSION_STRING} VERSION_LESS "3.7")
    message(FATAL_ERROR "Python 3.7+ is required. Found ${Python3_VERSION_MAJOR}.${Python3_VERSION_MINOR}")
endif()
message(${PYTHON_INCLUDE_DIRS})
include_directories(${PYTHON_INCLUDE_DIRS})
include_directories(${Python3_INCLUDE_DIRS})
add_subdirectory("${THIRD_PARTY_DIR}/pybind11-2.6.1")

# Snap graph library
include_directories("${THIRD_PARTY_DIR}/snap/glib-core")
include_directories("${THIRD_PARTY_DIR}/snap/snap-core")
add_subdirectory("${THIRD_PARTY_DIR}/snap")

# Eigen3 library
include_directories("${THIRD_PARTY_DIR}/eigen-3.3.9")

# nlohmann/json library
include_directories("${THIRD_PARTY_DIR}/json-3.9.1/single_include")

# pybind11_json library
include_directories("${THIRD_PARTY_DIR}/pybind11_json-0.2.7/include")

# Include sub-projects.
add_subdirectory (${GGCORE_DIRS})

# Google tests
#option(PACKAGE_TESTS "Build the tests" ON)
#if(PACKAGE_TESTS)
#    enable_testing()
#    add_subdirectory("${THIRD_PARTY_DIR}/googletest")
#   add_subdirectory(${GGCORE_TESTS})
#endif()
