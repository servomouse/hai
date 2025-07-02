add_executable(network_linear_test network_linear_test.c)

target_link_libraries(network_linear_test
    PRIVATE
        network
        neuron
        utils
)

target_include_directories(network_linear_test
    PRIVATE
        # ${TESTS_DIR}
        ${CMAKE_CURRENT_SOURCE_DIR}
)

set(CMAKE_C_FLAGS "")
set(CMAKE_CXX_FLAGS "")

target_compile_options(network_linear_test
    PRIVATE
        -Wall
        -Wextra
        -lm
        -g
        -lws2_32
        -fstack-protector-all
)

add_test(NAME network_linear_test COMMAND network_linear_test)

# target_compile_definitions(network_linear_test
#     PRIVATE
#         BCKP_DIR_PATH="${PROJECT_SOURCE_DIR}/backups"
# )