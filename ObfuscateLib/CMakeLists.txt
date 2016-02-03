cmake_minimum_required(VERSION 3.0)
project(ObfuscateLib)


find_package(OpenSSL REQUIRED)

FIND_PACKAGE(PythonLibs 2.7 REQUIRED)
INCLUDE_DIRECTORIES(${PYTHON_INCLUDE_DIRS})
find_package(Boost COMPONENTS python)
LINK_DIRECTORIES ( ${Boost_LIBRARY_DIRS} )
INCLUDE_DIRECTORIES ( ${Boost_INCLUDE_DIRS} )
ADD_DEFINITIONS(-DHAVE_BOOST)


include_directories(${OPENSSL_INCLUDE_DIR})
include_directories(src)


add_library(decode SHARED src/decode.cxx)
TARGET_LINK_LIBRARIES(decode ${OPENSSL_LIBRARIES} ${Boost_PYTHON_LIBRARY} ${PYTHON_LIBRARIES})

add_executable(generate src/generate.cxx)
TARGET_LINK_LIBRARIES(generate ${OPENSSL_LIBRARIES})

add_executable(decode_test src/decode.cxx)
TARGET_LINK_LIBRARIES(decode_test ${OPENSSL_LIBRARIES} ${Boost_PYTHON_LIBRARY} ${PYTHON_LIBRARIES})