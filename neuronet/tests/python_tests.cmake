
set(Python3_EXECUTABLE "${CMAKE_SOURCE_DIR}/myenv/Scripts/python")

# Manually specify the list of Python test files
set(PYTHON_TEST_FILES
    linear_net_instantiation
    linear_net_evolution
    linear_net_backpropagation
)

foreach(TEST_NAME ${PYTHON_TEST_FILES})
    set(TEST_COMMAND ${Python3_EXECUTABLE} -m unittest ${TEST_NAME})

    add_custom_target(${TEST_NAME}
        COMMAND ${TEST_COMMAND}
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/tests
    )
    add_dependencies(${TEST_NAME} network_shared)

    # Add the custom target to the test suite
    add_test(NAME ${TEST_NAME} COMMAND ${TEST_COMMAND})
    set_tests_properties(${TEST_NAME} PROPERTIES WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/tests)
endforeach()