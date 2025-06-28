cmake_minimum_required(VERSION 4.0.2)
set(CMAKE_C_COMPILER gcc)
set(CMAKE_CXX_COMPILER g++)
project(project_name)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)   # Generate compile_commands.json for vscode
include(CTest)

add_subdirectory(neurons)
add_subdirectory(network)
add_subdirectory(tests)

add_custom_target(cleanup
    COMMAND ${CMAKE_COMMAND} -E echo "Cleaning up build folder..."
    COMMAND ${CMAKE_COMMAND} -P ${CMAKE_CURRENT_SOURCE_DIR}/cleanup.cmake
)
