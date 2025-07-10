set(TESTS_DIR ${CMAKE_CURRENT_SOURCE_DIR})

include(${CMAKE_CURRENT_SOURCE_DIR}/neurons.cmake)
include(${CMAKE_CURRENT_SOURCE_DIR}/network.cmake)
include(${CMAKE_CURRENT_SOURCE_DIR}/python_tests.cmake)

add_custom_target(runtests
    COMMAND ${CMAKE_CTEST_COMMAND} --output-on-failure  # --rerun-failed
)

# Function to create a custom target for running a specific test
function(add_runtest test_name)
    add_custom_target(run_${test_name}
        COMMAND ${CMAKE_CTEST_COMMAND} -R ${test_name} --output-on-failure
        DEPENDS ${test_name}
    )
endfunction()

# Function to create tests and their corresponding targets
function(create_tests)
    set(tests_list ${ARGN})

    # Iterate over the list of tests and create individual targets
    foreach(test_name IN LISTS tests_list)
        add_dependencies(runtests ${test_name})
        message(STATUS "Creating the run_${test_name} target")
        add_runtest(${test_name})
    endforeach()
endfunction()

create_tests(
    network_linear_test
    py_tests
)