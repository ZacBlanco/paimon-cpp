from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy
from conan.tools.scm import Git
import os


class PaimonCppConan(ConanFile):
    name = "paimon-cpp"
    version = "0.9.0"
    package_type = "library"
    license = "Apache-2.0"
    url = "https://github.com/alibaba/paimon-cpp"  # informational
    description = "Paimon C++ core library and optional plugins"
    topics = ("paimon", "lakehouse", "arrow", "parquet", "orc")

    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_orc": [True, False],
        "with_avro": [True, False],
        "with_lance": [True, False],
        "with_jindo": [True, False],
        "with_lumina": [True, False],
        "with_lucene": [True, False],
    }

    default_options = {
        "shared": True,
        "fPIC": True,
        "with_orc": True,
        "with_avro": True,
        "with_lance": False,
        "with_jindo": False,
        "with_lumina": False,
        "with_lucene": False,
    }

    def requirements(self):
        """Declare runtime dependencies so the Conan graph is not empty.

        Versions intentionally align with Bolt's dependency tree.
        Do not set package options here to avoid misconfiguration errors.
        """
        # Core dependencies
        self.requires("arrow/15.0.1-oss")
        self.requires("fmt/9.0.0")
        self.requires("onetbb/2021.12.0")
        self.requires("glog/0.7.1")
        self.requires("rapidjson/1.1.0")
        self.requires("zlib/1.2.13")
        self.requires("zstd/1.5.7")
        self.requires("lz4/1.9.4")
        self.requires("snappy/1.2.1")

        # Optional dependencies
        if bool(self.options.with_orc):
            # protobuf is only required when ORC is enabled
            self.requires("protobuf/3.21.4")
            # If ORC is available in the remote, use it; otherwise ORC will be built locally
            # Uncomment below if your remote provides `orc/2.1.1`
            # self.requires("orc/2.1.1")
        if bool(self.options.with_avro):
            # Some environments package Avro C++ as `avro-cpp`. Keep this optional.
            # Uncomment if provided in the remote:
            # self.requires("avro-cpp/1.11.0")
            pass

    def source(self):
        """Retrieve the sources from git"""
        git = Git(self)
        # Use self.url from the recipe attributes
        git.clone(url=self.url, target=".", args=["--depth", "1", "--branch", self.version])

    def layout(self):
        cmake_layout(self)

    def _use_cxx11_abi(self) -> bool:
        compiler = str(self.settings.compiler)
        if compiler not in ("gcc", "clang", "apple-clang"):
            return True

        # Conan encodes the libstdc++ ABI choice here.
        libcxx = str(getattr(self.settings.compiler, "libcxx", ""))
        if libcxx == "libstdc++":
            return False
        return True

    def generate(self):
        tc = CMakeToolchain(self)

        tc.variables["PAIMON_BUILD_TESTS"] = False
        tc.variables["PAIMON_BUILD_SHARED"] = bool(self.options.shared)
        tc.variables["PAIMON_BUILD_STATIC"] = not bool(self.options.shared)

        tc.variables["PAIMON_ENABLE_ORC"] = bool(self.options.with_orc)
        tc.variables["PAIMON_ENABLE_AVRO"] = bool(self.options.with_avro)
        tc.variables["PAIMON_ENABLE_LANCE"] = bool(self.options.with_lance)
        tc.variables["PAIMON_ENABLE_JINDO"] = bool(self.options.with_jindo)
        tc.variables["PAIMON_ENABLE_LUMINA"] = bool(self.options.with_lumina)
        tc.variables["PAIMON_ENABLE_LUCENE"] = bool(self.options.with_lucene)

        tc.variables["PAIMON_USE_CXX11_ABI"] = self._use_cxx11_abi()

        if "fPIC" in self.options:
            tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = bool(self.options.fPIC)

        tc.generate()
        # Provide find_package configs for declared requirements
        deps = CMakeDeps(self)
        deps.generate()

    def configure(self):
        """Adjust transitive dependency options required by recipes.

        onetbb requires hwloc to be built as shared in your remote. Enforce it
        here to avoid Invalid configuration errors during resolution.
        """
        # Ensure hwloc is shared to satisfy onetbb's constraint
        try:
            self.options["hwloc/*"].shared = True
        except Exception:
            # If not present in graph yet, Conan will still apply the pattern
            # when hwloc enters via transitive requirements.
            pass

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "NOTICE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        # Expose nice Conan/CMake target names; consumers can also link by lib names.
        self.cpp_info.set_property("cmake_file_name", "Paimon")

        # Core library
        core = self.cpp_info.components["core"]
        core.libs = ["paimon"]
        core.set_property("cmake_target_name", "Paimon::core")
        core.includedirs = ["include"]

        # Many targets link libdl + pthread somewhere in the chain on Linux.
        if str(self.settings.os) == "Linux":
            core.system_libs = ["dl", "pthread"]

        # Always-built plugins in this repo
        fs_local = self.cpp_info.components["fs_local"]
        fs_local.libs = ["paimon_local_file_system"]
        fs_local.requires = ["core"]
        fs_local.set_property("cmake_target_name", "Paimon::fs_local")

        file_index = self.cpp_info.components["file_index"]
        file_index.libs = ["paimon_file_index"]
        file_index.requires = ["core"]
        file_index.set_property("cmake_target_name", "Paimon::file_index")

        global_index = self.cpp_info.components["global_index"]
        global_index.libs = ["paimon_global_index"]
        global_index.requires = ["core", "file_index"]
        global_index.set_property("cmake_target_name", "Paimon::global_index")

        fmt_parquet = self.cpp_info.components["format_parquet"]
        fmt_parquet.libs = ["paimon_parquet_file_format"]
        fmt_parquet.requires = ["core"]
        fmt_parquet.set_property("cmake_target_name", "Paimon::format_parquet")

        fmt_blob = self.cpp_info.components["format_blob"]
        fmt_blob.libs = ["paimon_blob_file_format"]
        fmt_blob.requires = ["core"]
        fmt_blob.set_property("cmake_target_name", "Paimon::format_blob")

        # Optional plugins
        if bool(self.options.with_orc):
            fmt_orc = self.cpp_info.components["format_orc"]
            fmt_orc.libs = ["paimon_orc_file_format"]
            fmt_orc.requires = ["core"]
            fmt_orc.set_property("cmake_target_name", "Paimon::format_orc")

        if bool(self.options.with_avro):
            fmt_avro = self.cpp_info.components["format_avro"]
            fmt_avro.libs = ["paimon_avro_file_format"]
            fmt_avro.requires = ["core"]
            fmt_avro.set_property("cmake_target_name", "Paimon::format_avro")

        if bool(self.options.with_lance):
            fmt_lance = self.cpp_info.components["format_lance"]
            fmt_lance.libs = ["paimon_lance_file_format"]
            fmt_lance.requires = ["core"]
            fmt_lance.set_property("cmake_target_name", "Paimon::format_lance")

        if bool(self.options.with_jindo):
            fs_jindo = self.cpp_info.components["fs_jindo"]
            fs_jindo.libs = ["paimon_jindo_file_system"]
            fs_jindo.requires = ["core"]
            fs_jindo.set_property("cmake_target_name", "Paimon::fs_jindo")

        if bool(self.options.with_lumina):
            idx_lumina = self.cpp_info.components["index_lumina"]
            idx_lumina.libs = ["paimon_lumina_index"]
            idx_lumina.requires = ["core"]
            idx_lumina.set_property("cmake_target_name", "Paimon::index_lumina")

        if bool(self.options.with_lucene):
            idx_lucene = self.cpp_info.components["index_lucene"]
            idx_lucene.libs = ["paimon_lucene_index"]
            idx_lucene.requires = ["core"]
            idx_lucene.set_property("cmake_target_name", "Paimon::index_lucene")
