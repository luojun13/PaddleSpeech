cmake_minimum_required(VERSION 3.14 FATAL_ERROR)

project(paddlespeech VERSION 0.1)

set(CMAKE_VERBOSE_MAKEFILE on)
# set std-14
set(CMAKE_CXX_STANDARD 14)

# include file 
include(FetchContent)
include(ExternalProject)
# fc_patch dir
set(FETCHCONTENT_QUIET off)
get_filename_component(fc_patch "fc_patch" REALPATH BASE_DIR "${CMAKE_SOURCE_DIR}")
set(FETCHCONTENT_BASE_DIR ${fc_patch})


###############################################################################
# Option Configurations
###############################################################################
# option configurations 
option(TEST_DEBUG "option for debug" OFF)


###############################################################################
# Include third party
###############################################################################
# #example for include third party
# FetchContent_Declare()
# # FetchContent_MakeAvailable was not added until CMake 3.14
# FetchContent_MakeAvailable()
# include_directories()

# ABSEIL-CPP
include(FetchContent)
FetchContent_Declare(
  absl
  GIT_REPOSITORY "https://github.com/abseil/abseil-cpp.git"
  GIT_TAG "20210324.1"
)
FetchContent_MakeAvailable(absl)

# libsndfile
include(FetchContent)
FetchContent_Declare(
  libsndfile
  GIT_REPOSITORY "https://github.com/libsndfile/libsndfile.git"
  GIT_TAG "1.0.31"
)
FetchContent_MakeAvailable(libsndfile)

# gflags
FetchContent_Declare(
  gflags
  URL      https://github.com/gflags/gflags/archive/v2.2.1.zip
  URL_HASH SHA256=4e44b69e709c826734dbbbd5208f61888a2faf63f239d73d8ba0011b2dccc97a
)
FetchContent_MakeAvailable(gflags)
include_directories(${gflags_BINARY_DIR}/include)

# glog
FetchContent_Declare(
  glog
  URL      https://github.com/google/glog/archive/v0.4.0.zip
  URL_HASH SHA256=9e1b54eb2782f53cd8af107ecf08d2ab64b8d0dc2b7f5594472f3bd63ca85cdc
)
FetchContent_MakeAvailable(glog)
include_directories(${glog_BINARY_DIR})

# gtest
FetchContent_Declare(googletest
  URL      https://github.com/google/googletest/archive/release-1.10.0.zip
  URL_HASH SHA256=94c634d499558a76fa649edb13721dce6e98fb1e7018dfaeba3cd7a083945e91
)
FetchContent_MakeAvailable(googletest)

# openfst
set(openfst_SOURCE_DIR ${fc_patch}/openfst-src)
set(openfst_BINARY_DIR ${fc_patch}/openfst-build)
set(openfst_PREFIX_DIR ${fc_patch}/openfst-subbuild/openfst-populate-prefix)
ExternalProject_Add(openfst
  URL               https://github.com/mjansche/openfst/archive/refs/tags/1.7.2.zip
  URL_HASH          SHA256=ffc56931025579a8af3515741c0f3b0fc3a854c023421472c07ca0c6389c75e6
  SOURCE_DIR        ${openfst_SOURCE_DIR}
  BINARY_DIR        ${openfst_BINARY_DIR}
  CONFIGURE_COMMAND ${openfst_SOURCE_DIR}/configure --prefix=${openfst_PREFIX_DIR}
                      "CPPFLAGS=-I${gflags_BINARY_DIR}/include -I${glog_SOURCE_DIR}/src -I${glog_BINARY_DIR}"
                      "LDFLAGS=-L${gflags_BINARY_DIR} -L${glog_BINARY_DIR}"
                      "LIBS=-lgflags_nothreads -lglog -lpthread"
  BUILD_COMMAND     make -j 4
)
add_dependencies(openfst gflags glog)
link_directories(${openfst_PREFIX_DIR}/lib)
include_directories(${openfst_PREFIX_DIR}/include)

add_subdirectory(speechx)

#openblas
#set(OpenBLAS_INSTALL_PREFIX ${fc_patch}/OpenBLAS)
#set(OpenBLAS_SOURCE_DIR ${fc_patch}/OpenBLAS-src)
#ExternalProject_Add(
#  OpenBLAS
#  GIT_REPOSITORY https://github.com/xianyi/OpenBLAS
#  GIT_TAG v0.3.13
#  GIT_SHALLOW TRUE
#  GIT_PROGRESS TRUE
#  CONFIGURE_COMMAND ""
#  BUILD_IN_SOURCE TRUE
#  BUILD_COMMAND make USE_LOCKING=1 USE_THREAD=0
#  INSTALL_COMMAND make PREFIX=${OpenBLAS_INSTALL_PREFIX} install
#  UPDATE_DISCONNECTED TRUE
#)

###############################################################################
# Add local library
###############################################################################
# system lib 
#find_package()
# if dir have CmakeLists.txt 
#add_subdirectory(speechx)
# if dir do not have CmakeLists.txt 
#add_library(lib_name STATIC file.cc)
#target_link_libraries(lib_name item0 item1)
#add_dependencies(lib_name depend-target)