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

set(PAIMON_LOCAL_FILE_SYSTEM local_file.cpp local_file_system.cpp
                             local_file_system_factory.cpp)

add_paimon_lib(paimon_local_file_system
               SOURCES
               ${PAIMON_LOCAL_FILE_SYSTEM}
               DEPENDENCIES
               paimon_shared
               STATIC_LINK_LIBS
               fmt
               arrow
               SHARED_LINK_LIBS
               paimon_shared
               SHARED_LINK_FLAGS
               ${PAIMON_VERSION_SCRIPT_FLAGS})

# Ensure the objlib sees dependency include directories (Arrow, fmt)
if(TARGET Arrow::arrow)
    target_include_directories(paimon_local_file_system_objlib SYSTEM PUBLIC $<TARGET_PROPERTY:Arrow::arrow,INTERFACE_INCLUDE_DIRECTORIES>)
elseif(TARGET arrow::arrow)
    target_include_directories(paimon_local_file_system_objlib SYSTEM PUBLIC $<TARGET_PROPERTY:arrow::arrow,INTERFACE_INCLUDE_DIRECTORIES>)
elseif(TARGET arrow)
    target_include_directories(paimon_local_file_system_objlib SYSTEM PUBLIC $<TARGET_PROPERTY:arrow,INTERFACE_INCLUDE_DIRECTORIES>)
endif()
if(TARGET fmt::fmt)
    target_include_directories(paimon_local_file_system_objlib SYSTEM PUBLIC $<TARGET_PROPERTY:fmt::fmt,INTERFACE_INCLUDE_DIRECTORIES>)
elseif(TARGET fmt)
    target_include_directories(paimon_local_file_system_objlib SYSTEM PUBLIC $<TARGET_PROPERTY:fmt,INTERFACE_INCLUDE_DIRECTORIES>)
endif()
