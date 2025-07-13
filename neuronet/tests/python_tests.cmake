
set(Python3_EXECUTABLE "${CMAKE_SOURCE_DIR}/myenv/Scripts/python")

# message(STATUS "CMAKE_SOURCE_DIR: ${CMAKE_SOURCE_DIR}")

# Define the test command
set(TEST_COMMAND ${Python3_EXECUTABLE} -m unittest discover -s ${CMAKE_SOURCE_DIR}/tests -p *.py)

# Use a consistent name for the test
set(TEST_NAME "python_tests")

# Add a custom target for Python tests
add_custom_target(${TEST_NAME}
    COMMAND ${TEST_COMMAND}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/tests
)

add_dependencies(${TEST_NAME} network_shared)

# Add the custom target to the test suite
add_test(NAME ${TEST_NAME} COMMAND ${TEST_COMMAND})
set_tests_properties(${TEST_NAME} PROPERTIES WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/tests)