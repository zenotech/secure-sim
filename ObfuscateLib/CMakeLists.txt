cmake_minimum_required(VERSION 3.4)
project(ObfuscateLib)


find_package(OpenSSL REQUIRED)

include_directories(${OPENSSL_INCLUDE_DIR})


add_library(decode SHARED src/decode.cxx)
TARGET_LINK_LIBRARIES(decode ${OPENSSL_LIBRARIES})

add_executable(generate src/generate.cxx)
TARGET_LINK_LIBRARIES(generate ${OPENSSL_LIBRARIES})

add_executable(decode_test src/decode.cxx)
TARGET_LINK_LIBRARIES(decode_test ${OPENSSL_LIBRARIES})