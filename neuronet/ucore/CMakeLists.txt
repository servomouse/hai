set(SOURCES ucore.c)

add_library(ucore ${SOURCES})

target_link_libraries(ucore
    PRIVATE
        utils
        neuron
)

target_include_directories(ucore
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}
        ${PROJECT_SOURCE_DIR}/lib
)

set(CMAKE_C_FLAGS "")
set(CMAKE_CXX_FLAGS "")

target_compile_options(ucore
    PRIVATE
        -Wall
        -Wextra
        -Wno-unused-parameter   # DELETEME
        -Werror=implicit-function-declaration   # Treat implicit declaration as an error, not as a warning
        -lm
        -g
        -lws2_32
        -fstack-protector-all
)
