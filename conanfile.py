from conan import ConanFile
from conan.tools.files import copy
from conan.tools.files import get
from conan.tools.files import patch
from conan.tools.env import VirtualBuildEnv
from os.path import join
from conan.tools.microsoft import VCVars
from conan.tools.microsoft import is_msvc

class DpcppConan(ConanFile):
  name = "dpcpp"
 
  # Optional metadata
  license = "Apache v2.0"
  author = "LLVM Team, Intel"
  url = "https://github.com/intel/llvm"
  description = "Conan recipe for the Intel DPCPP toolchain and runtime libraries"
  topics = ("sycl", "dpcpp", "dpc++")

  settings = "os", "arch", "compiler", "build_type"
  options = {
    "cuda_runtime": ["None", "12.3"]
  }
  default_options = {
    "cuda_runtime": "None"
  }
  
  exports_sources = [ "patches/*.patch" ]

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
      if is_msvc(self): 
        vcvars = VCVars(self)
        vcvars.generate()
  
  def build(self):
    for p in self.conan_data["patches"][self.version]:
      patch_file = join(self.export_sources_folder, p["patch_file"])
      patch(self, patch_file=patch_file)
    configure_args = "--enable-all-llvm-targets"
    if self.options.cuda_runtime != "None":
      configure_args += " --cuda"
    self.run(f'python {self.source_folder}/buildbot/configure.py -o {self.build_folder} {configure_args}')
    self.run(f'python {self.source_folder}/buildbot/compile.py -o {self.build_folder}')
    if(self.settings.os == "Windows"):
      self.run(f'python {self.source_folder}/buildbot/compile.py -o {self.build_folder} --build-target=install-llvm-rc')

  def package(self):
    copy(self, "*", join(self.build_folder, "install"), self.package_folder)
    copy(self, "*.cmake", join(self.recipe_folder, "cmake"), join(self.package_folder, "cmake"))

  def compatibility(self):
    if self.info.compiler == "clang":
      return [
        { "settings": [
            ("compiler","msvc")
            ("compiler.version", 193)
          ]
        },
        { "settings":[
          ("compiler", "msvc")
          ("compiler.version", 192)
        ]}  
      ]
    return []
  
  def package_id(self):
    del self.info.settings.compiler
  
  def build_id(self):
    self.info_build.settings.build_type="Any"

  def package_info(self):
    isDebug = self.settings.build_type == "Debug"
    if self.settings.os == "Windows":
      self.cpp_info.libs = [ "sycl7d" if isDebug else "sycl7" , "sycl-devicelib-host"]
    else:
      self.cpp_info.libs = [ "sycld" if isDebug else "sycl" ]
    bindir = join(self.package_folder, "bin")
    cc = join(bindir, "clang") 
    cxx = join(bindir, "clang++")
    self.buildenv_info.define("CC", cc)
    self.buildenv_info.define("CXX", cxx)
    self.buildenv_info.define("LINKER", cxx)
    if(self.settings.os == "Windows"):
      rc = join(bindir, "llvm-rc")
      self.buildenv_info.define("RC", rc)
    linkflags = [ "-fsycl" ]
    if(is_msvc(self)):
      self.buildenv_info.define("CXXFLAGS", "-lmsvcrtd" if isDebug else "-lmsvcrt")
    self.cpp_info.includedirs = ["include/sycl", "include/std", "include/xpti", "include"]
    self.cpp_info.cxxflags=["-fsycl"]
    self.cpp_info.exelinkflags=linkflags
    self.cpp_info.sharedlinkflags=linkflags
    self.runenv_info.append_path("PATH", bindir)
