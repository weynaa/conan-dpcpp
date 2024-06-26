import os

from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout, CMakeToolchain
from conan.tools.build import can_run

class DPCPPTestConan(ConanFile):
    settings = "os", "build_type", "compiler", "arch"
    generators = "CMakeDeps", 
    test_type = "explicit"
    def build_requirements(self):
        self.tool_requires("ninja/[>=1.11]") 
        self.tool_requires(self.tested_reference_str)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        tc = CMakeToolchain(self, "Ninja")
        if self.dependencies[self.tested_reference_str].options["cuda_runtime"]:
            tc.cache_variables["SYCL_WITH_CUDA"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def layout(self):
        cmake_layout(self)
    
    def test(self):
        if can_run(self):
            cmd = os.path.join(self.build_folder, "sycl_test")
            self.run(cmd, env="conanrun")
