# Clear build folder:
set(to_keep_list ".gitignore")

file(GLOB dir_contents LIST_DIRECTORIES true RELATIVE ${CMAKE_CURRENT_BINARY_DIR} ${CMAKE_BINARY_DIR}/*)

foreach(element ${dir_contents})
    message(STATUS "Checking ${element}")
    list(FIND to_keep_list ${element} index)
    if (${index} EQUAL -1)
        message(STATUS "Removing ${element}")
        if(IS_DIRECTORY ${CMAKE_BINARY_DIR}/${element})
            file(REMOVE_RECURSE ${CMAKE_BINARY_DIR}/${element})
        else()
            file(REMOVE ${CMAKE_BINARY_DIR}/${element})
        endif()
    endif()
endforeach()
