set(SOURCES
    network.c
    network_creator.c
)

set(SHARED_BUILD TRUE)

add_library(network SHARED ${SOURCES})

set_target_properties(network PROPERTIES
    OUTPUT_NAME "network"
    RUNTIME_OUTPUT_DIRECTORY "${PROJECT_SOURCE_DIR}/bin"
)

# message(STATUS "Building static version of the network library")
# add_library(network ${SOURCES})

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
        -Werror=implicit-function-declaration   # Treat implicit declaration as an error, not as a warning
        -lm
        -shared
        -g
        -lws2_32
        # -m32    # Generate 32-bit dll
        -fstack-protector-all
        -Wl,--out-implib,libnetwork.a     # Also create a linkable library
)

# target_compile_definitions(network
#     PRIVATE
#         BCKP_DIR_PATH="${PROJECT_SOURCE_DIR}/backups"
# )

# target_compile_definitions(network PRIVATE CMAKE_EXPORT_COMPILE_COMMANDS=1)
