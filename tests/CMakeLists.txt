# CMakeList.txt : CMake project for ggcore, include source and define
# project specific logic here.
#
cmake_minimum_required (VERSION 3.8)

# Add sources for pybind tests
pybind11_add_module(TEST_PYBIND11_INSTALLATION "test_pybind.cpp")
if ( MSVC )
    set_target_properties(TEST_PYBIND11_INSTALLATION PROPERTIES LIBRARY_OUTPUT_DIRECTORY "${PYTHON_LIBRARY_DIR}")
    set_target_properties(TEST_PYBIND11_INSTALLATION PROPERTIES LIBRARY_OUTPUT_DIRECTORY_DEBUG "${PYTHON_LIBRARY_DIR}")
    set_target_properties(TEST_PYBIND11_INSTALLATION PROPERTIES LIBRARY_OUTPUT_DIRECTORY_RELEASE "${PYTHON_LIBRARY_DIR}")
endif ( MSVC )

# Test Eigen3
#include_directories("${THIRD_PARTY_DIR}/eigen-3.3.9")
add_executable (TEST_EIGEN3_INSTALLATION "test_eigen3.cpp")

# Test Snap
add_executable (TEST_SNAP_INSTALLATION "test_snap.cpp")
target_link_libraries(TEST_SNAP_INSTALLATION PUBLIC snapcore)

# Googletests
set(GGCORE_TEST_SOURCES 
    "test_entity.cpp"
)

add_executable(GGCORE_TEST ${GGCORE_TEST_SOURCES})
target_link_libraries(GGCORE_TEST PUBLIC
    gtest_main
    #ggcore
)

add_test(
    NAME GGCORE_TEST
    COMMAND GGCORE_TEST
)