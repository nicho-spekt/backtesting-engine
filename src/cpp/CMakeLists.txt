cmake_minimum_required(VERSION 3.18)

project(metrics_cpp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(PYBIND11_FINDPYTHON ON)

find_package(
    Python
    COMPONENTS Interpreter Development
    REQUIRED
)

find_package(
    pybind11
    CONFIG
    REQUIRED
)

pybind11_add_module(
    metrics_cpp
    src/bindings.cpp
    src/MetricsEngine.cpp
)

target_include_directories(
    metrics_cpp
    PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)