from conan import ConanFile
from conan.tools.files import copy
from conan.tools.files import get
from conan.tools.files import patch
from conan.tools.env import VirtualBuildEnv
from os.path import join

class DpcppConan(ConanFile):
  name = "dpcpp"
  version = "2023.2"
   # Optional metadata
  license = "Apache v2.0"
  author = "LLVM Team, Intel"
  url = "https://github.com/intel/llvm"
  description = "<Description of Cppsample here>"
  topics = ("sycl", "dpcpp", "dpc++")

  settings = "os", "arch", "compiler", "build_type"
  options = {
    "cuda_runtime": ["None", "12.0"]
  }
  default_options = {
    "cuda_runtime": "None"
  }
  
  exports_sources = "*.patch"

  def build_requirements(self):
    self.tool_requires("ninja/[>=1.11]")

  def layout(self):
    self.folders.source = "src"
    self.folders.build = "build"

  def source(self):
    get(self, **self.conan_data["sources"][self.version])

  def generate(self):
      ms = VirtualBuildEnv(self)
      ms.generate()

  def build(self):
    for p in self.conan_data["patches"][self.version]:
      patch_file = join(self.export_sources_folder, p["patch_file"])
      patch(self, patch_file=patch_file)
    configure_args = ""
    if self.options.cuda_runtime != "None":
      configure_args += " --cuda"
    self.run(f'python {self.source_folder}/buildbot/configure.py -o {self.build_folder} {configure_args}')
    self.run(f'python {self.source_folder}/buildbot/compile.py -o {self.build_folder}')

  def package(self):
    copy(self, "*", join(self.build_folder, "install"), self.package_folder)

  def package_info(self):
    if self.settings.os == "Windows":
      self.cpp_info.libs = [ "sycl7" ]
    else:
      self.cpp_info.libs = [ "sycl" ]
