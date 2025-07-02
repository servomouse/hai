set(SOURCES
    network.c
    network_creator.c
)

add_library(network ${SOURCES})
# add_library(network SHARED ${SOURCES})

# set_target_properties(network PROPERTIES
#     OUTPUT_NAME "network"
#     RUNTIME_OUTPUT_DIRECTORY "${PROJECT_SOURCE_DIR}/bin"
# )

target_link_libraries(network
    PRIVATE
        neuron
        utils
)

target_include_directories(network
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}
)

set(CMAKE_C_FLAGS "")
set(CMAKE_CXX_FLAGS "")

target_compile_options(network
    PRIVATE
        -Wall
        -Wextra
        -Wno-unused-parameter   # DELETEME
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
