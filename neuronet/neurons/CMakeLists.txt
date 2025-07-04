set(SOURCES
    neuron.c
    neuron_mutations.c
)

add_library(neuron ${SOURCES})

# set_target_properties(neuron PROPERTIES
#     OUTPUT_NAME "neuron"
# )

target_link_libraries(neuron
    PRIVATE
        utils
)

target_include_directories(neuron
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}
        ${PROJECT_SOURCE_DIR}/lib
)

set(CMAKE_C_FLAGS "")
set(CMAKE_CXX_FLAGS "")

target_compile_options(neuron
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

# target_compile_definitions(neuron
#     PRIVATE
#         BCKP_DIR_PATH="${PROJECT_SOURCE_DIR}/backups"
# )
