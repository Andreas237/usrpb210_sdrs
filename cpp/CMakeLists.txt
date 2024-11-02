cmake_minimum_required(VERSION 3.20)
project(uhd_scanner LANGUAGES CXX)

add_executable(uhd_scanner)

# set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${PROJECT_BINARY_DIR}")
# set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${PROJECT_BINARY_DIR}")
# set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${PROJECT_BINARY_DIR}")

option(BUILD_SHARED_LIBS "Build using shared libraries" ON)

target_sources(uhd_scanner PRIVATE "main.cpp")

find_package(PkgConfig REQUIRED)

find_package(Armadillo REQUIRED)  # Find Armadillo (report error if not found)
include_directories(${ARMADILLO_INCLUDE_DIRS})  # Add Armadillo include paths
target_link_libraries(uhd_scanner ${ARMADILLO_LIBRARIES})  # Link against Armadillo libraries

find_package(Boost COMPONENTS program_options REQUIRED)
include_directories(${Boost_INCLUDE_DIRS})
target_link_libraries(uhd_scanner uhd ${Boost_LIBRARIES})

find_package(spdlog REQUIRED)
target_link_libraries(uhd_scanner spdlog::spdlog_header_only)


add_library(uhd_scanner_lib SHARED main.cpp)
install(TARGETS uhd_scanner)