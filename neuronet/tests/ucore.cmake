add_executable(ucore_test ucore_test.c)

target_link_libraries(ucore_test
    PRIVATE
        ucore
        neuron
        utils
)

target_include_directories(ucore_test
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
)

set(CMAKE_C_FLAGS "")
set(CMAKE_CXX_FLAGS "")

target_compile_options(ucore_test
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

add_test(NAME ucore_test COMMAND ucore_test)