add_executable(network_linear_test network_linear_test.c)

target_link_libraries(network_linear_test
    PRIVATE
        network_static
        neuron
        utils
)

target_include_directories(network_linear_test
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
)

set(CMAKE_C_FLAGS "")
set(CMAKE_CXX_FLAGS "")

target_compile_options(network_linear_test
    PRIVATE
        -Wall
        -Wextra
        -lm
        -Wno-unused-parameter   # DELETEME
        -Werror=implicit-function-declaration   # Treat implicit declaration as an error, not as a warning
        -g
        -lws2_32
        -fstack-protector-all
)

add_test(NAME network_linear_test COMMAND network_linear_test)

# target_compile_definitions(network_linear_test
#     PRIVATE
#         BCKP_DIR_PATH="${PROJECT_SOURCE_DIR}/backups"
# )