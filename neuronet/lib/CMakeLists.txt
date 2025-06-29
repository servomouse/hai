add_library(utils
    utils.c
    mymath.c
    stack_guard.c
)

target_include_directories(utils
    PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}
)
