set(SOURCES
    # network.c
)

add_library(network SHARED ${SOURCES})

set_target_properties(network PROPERTIES
    OUTPUT_NAME "network"
)

# target_link_libraries(network
#     PRIVATE
#         neuron
#         utils
# )

target_include_directories(network
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
)

set(CMAKE_C_FLAGS "")
set(CMAKE_CXX_FLAGS "")

target_compile_options(network
    PRIVATE
        -Wall
        -Wextra
        -lm
        -g
        -lws2_32
        -fstack-protector-all
)

# target_compile_definitions(network
#     PRIVATE
#         BCKP_DIR_PATH="${PROJECT_SOURCE_DIR}/backups"
# )

# target_compile_definitions(network PRIVATE CMAKE_EXPORT_COMPILE_COMMANDS=1)
