# find_package(Python3 COMPONENTS Development REQUIRED)

# # Should be set by find_package(Python3..., if it isn't, set it manually
# if(NOT Python3_EXECUTABLE)
#     set(Python3_EXECUTABLE "python")  # or "python3" depending on your system
# endif()
set(Python3_EXECUTABLE "${CMAKE_SOURCE_DIR}/myenv/Scripts/python")

# Add a custom target for Python tests
add_custom_target(py_tests
    COMMAND ${Python3_EXECUTABLE} -m unittest discover -s . -p "*.py"
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)

# Add the custom target to the test suite
add_test(NAME py_tests COMMAND ${Python3_EXECUTABLE} -m unittest discover -s . -p "*.py")