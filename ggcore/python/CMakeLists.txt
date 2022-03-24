set(GGCORE_SOURCES
    "pybindings.cpp"
)

# Define iglpy bindings
pybind11_add_module(ggsolver ${GGCORE_SOURCES})
target_link_libraries(ggsolver PUBLIC snapcore ggcore)
set_target_properties(ggsolver PROPERTIES LIBRARY_OUTPUT_DIRECTORY "${PYTHON_LIBRARY_DIR}")

#message("--------------- ${LIBRARY_OUTPUT_PATH}")
#link_directories("${LIBRARY_OUTPUT_PATH}")
#target_link_libraries(ggsolver PUBLIC ggcore)
if ( MSVC )
    set_target_properties(ggsolver PROPERTIES LIBRARY_OUTPUT_DIRECTORY "${PYTHON_LIBRARY_DIR}")
    set_target_properties(ggsolver PROPERTIES LIBRARY_OUTPUT_DIRECTORY_DEBUG "${PYTHON_LIBRARY_DIR}")
    set_target_properties(ggsolver PROPERTIES LIBRARY_OUTPUT_DIRECTORY_RELEASE "${PYTHON_LIBRARY_DIR}")
endif ( MSVC )