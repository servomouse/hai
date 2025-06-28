# add_subdirectory(linear)
# add_subdirectory(poly)

set(NEURON_SOURCES
    # neuron.c
    # neuron_mutations.c
    # neuron_save_restore.c
)

add_library(neuron ${NEURON_SOURCES})

# target_link_libraries(neuron
#     PRIVATE
#         utils
#         poly_neuron
#         linear_neuron
# )

target_include_directories(neuron
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}
)

set(CMAKE_C_FLAGS "")
set(CMAKE_CXX_FLAGS "")

target_compile_options(neuron
    PRIVATE
        -Wall
        -Wextra
        -lm
        -g
        -lws2_32
        -fstack-protector-all
)

# target_compile_definitions(neuron
#     PRIVATE
#         BCKP_DIR_PATH="${PROJECT_SOURCE_DIR}/backups"
# )
