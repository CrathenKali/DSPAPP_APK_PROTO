
cmake_minimum_required(VERSION 3.6)
project(native_dsp)

set(CMAKE_CXX_STANDARD 14)
add_library(native_dsp SHARED native_dsp.cpp kiss_fft.c)

find_library(log-lib log)

target_include_directories(native_dsp PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
target_compile_definitions(native_dsp PRIVATE KISS_FFT_PROTOTYPE=1)
target_link_libraries(native_dsp ${log-lib})
