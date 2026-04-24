# Copyright 2024-present Alibaba Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# PaimonConanDeps.cmake
#
# Resolves dependencies from Conan CMakeDeps-generated configs and populates
# the exact same variables and targets that ThirdpartyToolchain does when building
# from source.  This allows all downstream CMakeLists to work identically in both
# modes without any per-file conan/thirdparty branching.

macro(paimon_setup_conan_deps)

    # --- Find all Conan packages ---
    # This loads the *-data.cmake files which set *_INCLUDE_DIRS_RELEASE etc.
    find_package(Arrow QUIET CONFIG)
    find_package(arrow QUIET CONFIG)
    find_package(Parquet QUIET CONFIG)
    find_package(TBB QUIET CONFIG)
    find_package(fmt)
    find_package(glog QUIET CONFIG)
    find_package(RapidJSON REQUIRED CONFIG)

    find_package(ZLIB QUIET)
    find_package(zstd QUIET CONFIG)
    find_package(lz4 QUIET CONFIG)
    find_package(snappy QUIET CONFIG)
    find_package(Protobuf QUIET CONFIG)

    # --- Populate *_INCLUDE_DIR variables (same names ThirdpartyToolchain uses) ---
    # Conan CMakeDeps generates <pkg>_INCLUDE_DIRS_RELEASE with plain paths.
    # These are set by the *-data.cmake files that find_package() includes.
    # Note: variable names use the Conan package name (e.g. onetbb not TBB).
    set(ARROW_INCLUDE_DIR  ${arrow_INCLUDE_DIRS_RELEASE})
    set(TBB_INCLUDE_DIR    ${onetbb_INCLUDE_DIRS_RELEASE})
    set(FMT_INCLUDE_DIR    ${fmt_INCLUDE_DIRS_RELEASE})
    set(GLOG_INCLUDE_DIR   ${glog_INCLUDE_DIRS_RELEASE})
    set(LZ4_INCLUDE_DIR    ${lz4_INCLUDE_DIRS_RELEASE})
    set(SNAPPY_INCLUDE_DIR ${snappy_INCLUDE_DIRS_RELEASE})
    set(ZSTD_INCLUDE_DIR   ${zstd_INCLUDE_DIRS_RELEASE})
    set(ZLIB_INCLUDE_DIR   ${zlib_INCLUDE_DIRS_RELEASE})

    # RapidJSON's variable name is lowercase (rapidjson not RapidJSON)
    set(RAPIDJSON_INCLUDE_DIR ${rapidjson_INCLUDE_DIRS_RELEASE})

    # --- Create unified alias targets (same names ThirdpartyToolchain uses) ---
    # Must be INTERFACE IMPORTED with explicit target_link_libraries.
    # This must happen at macro scope (not inside a function) so that
    # generator expressions in link libraries propagate correctly at build time.

    # Arrow: aggregate target. Link to arrow::arrow for transitive deps.
    if(NOT TARGET arrow)
        add_library(arrow INTERFACE IMPORTED)
        if(TARGET Arrow::arrow)
            target_link_libraries(arrow INTERFACE Arrow::arrow)
        elseif(TARGET arrow::arrow)
            target_link_libraries(arrow INTERFACE arrow::arrow)
        endif()
        if(ARROW_INCLUDE_DIR)
            target_include_directories(arrow INTERFACE ${ARROW_INCLUDE_DIR})
        endif()
    endif()

    if(NOT TARGET parquet)
        add_library(parquet INTERFACE IMPORTED)
        if(TARGET Parquet::parquet)
            target_link_libraries(parquet INTERFACE Parquet::parquet)
        endif()
    endif()

    if(NOT TARGET tbb)
        add_library(tbb INTERFACE IMPORTED)
        if(TARGET TBB::tbb)
            target_link_libraries(tbb INTERFACE TBB::tbb)
            target_include_directories(tbb INTERFACE ${TBB_INCLUDE_DIR})
        endif()
    endif()

    if(NOT TARGET fmt)
        add_library(fmt INTERFACE IMPORTED)
        if(TARGET fmt::fmt)
            target_link_libraries(fmt INTERFACE fmt::fmt)
            target_include_directories(fmt INTERFACE ${FMT_INCLUDE_DIR})
        endif()
    endif()

    if(NOT TARGET glog)
        add_library(glog INTERFACE IMPORTED)
        if(TARGET glog::glog)
            target_link_libraries(glog INTERFACE glog::glog)
            target_include_directories(glog INTERFACE ${GLOG_INCLUDE_DIR})
            target_compile_definitions(glog INTERFACE GLOG_USE_GLOG_EXPORT)
        endif()
    endif()

    if(NOT TARGET RapidJSON)
        add_library(RapidJSON INTERFACE IMPORTED)
        if(TARGET RapidJSON::RapidJSON)
            target_link_libraries(RapidJSON INTERFACE RapidJSON::RapidJSON)
            target_include_directories(RapidJSON INTERFACE ${RAPIDJSON_INCLUDE_DIR})
        elseif(TARGET rapidjson)
            target_link_libraries(RapidJSON INTERFACE rapidjson)
            target_include_directories(RapidJSON INTERFACE ${RAPIDJSON_INCLUDE_DIR})
        endif()
    endif()

    if(NOT TARGET zlib)
        add_library(zlib INTERFACE IMPORTED)
        if(TARGET ZLIB::ZLIB)
            target_link_libraries(zlib INTERFACE ZLIB::ZLIB)
            target_include_directories(zlib INTERFACE ${ZLIB_INCLUDE_DIR})
        endif()
    endif()

    if(NOT TARGET zstd)
        add_library(zstd INTERFACE IMPORTED)
        if(TARGET zstd::zstd)
            target_link_libraries(zstd INTERFACE zstd::zstd)
            target_include_directories(zstd INTERFACE ${ZSTD_INCLUDE_DIR})
        elseif(TARGET zstd::libzstd_static)
            target_link_libraries(zstd INTERFACE zstd::libzstd_static)
            target_include_directories(zstd INTERFACE ${ZSTD_INCLUDE_DIR})
        endif()
    endif()

    if(NOT TARGET lz4)
        add_library(lz4 INTERFACE IMPORTED)
        if(TARGET LZ4::lz4_static)
            target_link_libraries(lz4 INTERFACE LZ4::lz4_static)
            target_include_directories(lz4 INTERFACE ${LZ4_INCLUDE_DIR})
        elseif(TARGET lz4::lz4)
            target_link_libraries(lz4 INTERFACE lz4::lz4)
            target_include_directories(lz4 INTERFACE ${LZ4_INCLUDE_DIR})
        endif()
    endif()

    if(NOT TARGET snappy)
        add_library(snappy INTERFACE IMPORTED)
        if(TARGET snappy::snappy)
            target_link_libraries(snappy INTERFACE snappy::snappy)
            target_include_directories(snappy INTERFACE ${SNAPPY_INCLUDE_DIR})
        endif()
    endif()

    if(NOT TARGET libprotobuf)
        add_library(libprotobuf INTERFACE IMPORTED)
        if(TARGET protobuf::libprotobuf)
            target_link_libraries(libprotobuf INTERFACE protobuf::libprotobuf)
        endif()
    endif()

endmacro()
