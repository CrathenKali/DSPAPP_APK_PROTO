cmake_minimum_required(VERSION 3.10)
project(dsp_app_native LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(SRC_DIR ${CMAKE_CURRENT_SOURCE_DIR}/src)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

add_library(native-lib SHARED
    ${SRC_DIR}/native-lib.cpp
    ${SRC_DIR}/dsp_controller.cpp
)

# Optionally include oboe adapter from native module
add_subdirectory("${CMAKE_SOURCE_DIR}/../../native" "${CMAKE_BINARY_DIR}/native" EXCLUDE_FROM_ALL)
target_link_libraries(native-lib PUBLIC dsp_oboe_adapter)

find_library(log-lib log)
target_link_libraries(native-lib PUBLIC ${log-lib} z)
target_include_directories(native-lib PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
