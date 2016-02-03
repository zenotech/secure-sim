cmake_minimum_required(VERSION 3.0)
project(ObfuscateLib)

find_package(OpenSSL REQUIRED)

find_package(Boost COMPONENTS python)

if(Boost_FOUND)
	find_package(PythonLibs 2.7 REQUIRED)
	include_directories(${PYTHON_INCLUDE_DIRS})

	link_directories ( ${Boost_LIBRARY_DIRS} )
	include_directories ( ${Boost_INCLUDE_DIRS} )
	add_definitions(-DHAVE_BOOST)
endif()

include_directories(${OPENSSL_INCLUDE_DIR})
include_directories(src)

add_library(decode SHARED src/decode.cxx)
target_link_libraries(decode ${OPENSSL_LIBRARIES} ${Boost_PYTHON_LIBRARY} ${PYTHON_LIBRARIES})

add_executable(generate src/generate.cxx)
target_link_libraries(generate ${OPENSSL_LIBRARIES})

add_executable(decode_test src/decode.cxx)
target_link_libraries(decode_test ${OPENSSL_LIBRARIES} ${Boost_PYTHON_LIBRARY} ${PYTHON_LIBRARIES})