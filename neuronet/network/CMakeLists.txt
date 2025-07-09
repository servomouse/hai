set(SOURCES
    network.c
    network_creator.c
)

add_library(network_dependencies INTERFACE)

target_link_libraries(network_dependencies
    INTERFACE
        neuron
        utils
)

add_library(network OBJECT ${SOURCES})

set_property(TARGET network PROPERTY POSITION_INDEPENDENT_CODE 1)   # shared libraries need PIC

target_link_libraries(network PUBLIC network_dependencies)

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
        -Wno-unused-parameter   # DELETEME
        -Werror=implicit-function-declaration   # Treat implicit declaration as an error, not as a warning
        -lm
        -shared
        -g
        -lws2_32
        -fstack-protector-all
)

# shared and static libraries built from the same object files
add_library(network_shared SHARED $<TARGET_OBJECTS:network>)
add_library(network_static STATIC $<TARGET_OBJECTS:network>)

target_link_libraries(network_shared PUBLIC network_dependencies)
target_link_libraries(network_static PUBLIC network_dependencies)

set_target_properties(network_shared PROPERTIES
    OUTPUT_NAME "network"
    RUNTIME_OUTPUT_DIRECTORY "${PROJECT_SOURCE_DIR}/bin"
)

target_include_directories(network_static PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
