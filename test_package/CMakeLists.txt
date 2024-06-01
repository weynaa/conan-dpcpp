cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(dpcpp CONFIG REQUIRED)

add_executable(sycl_test src/sycl_test.cpp)

set_target_properties(sycl_test PROPERTIES CXX_STANDARD 17)

target_compile_options(sycl_test PRIVATE -fsycl-unnamed-lambda)

if(SYCL_WITH_CUDA)
	target_compile_options(sycl_test PUBLIC
		-fsycl-targets=spir64,nvptx64-nvidia-cuda
	)
	target_link_options(sycl_test PUBLIC
		-fsycl-targets=spir64,nvptx64-nvidia-cuda
	)
endif()

target_link_libraries(sycl_test dpcpp::dpcpp)
