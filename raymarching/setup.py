import os
from setuptools import setup
from torch.utils.cpp_extension import BuildExtension, CUDAExtension
import torch

_src_path = os.path.dirname(os.path.abspath(__file__))

# Get the CUDA version that PyTorch was compiled with
torch_cuda_version = torch.version.cuda
print(f"PyTorch was compiled with CUDA version: {torch_cuda_version}")

# Set the CUDA_HOME based on the PyTorch version
if torch_cuda_version.startswith("11.8"):
    os.environ['CUDA_HOME'] = r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8'
elif torch_cuda_version.startswith("12.6"):
    os.environ['CUDA_HOME'] = r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6'
else:
    raise RuntimeError(f"Unsupported CUDA version: {torch_cuda_version}. Please install a compatible CUDA version.")

# Verify CUDA_HOME
print(f"Using CUDA_HOME: {os.environ['CUDA_HOME']}")

# Set the CUDA architecture for your GPU
os.environ['TORCH_CUDA_ARCH_LIST'] = '7.5'

# NVCC (CUDA Compiler) Flags
nvcc_flags = [
    '-O3', '-std=c++17',
    '-U__CUDA_NO_HALF_OPERATORS__',
    '-U__CUDA_NO_HALF_CONVERSIONS__',
    '-U__CUDA_NO_HALF2_OPERATORS__',
    '--expt-relaxed-constexpr',
    '-allow-unsupported-compiler'
]

# Compiler flags based on operating system
c_flags = ['/O2', '/std:c++17']

setup(
    name='raymarching',
    ext_modules=[
        CUDAExtension(
            name='_raymarching',
            sources=[os.path.join(_src_path, 'src', f) for f in [
                'raymarching.cu',
                'bindings.cpp',
            ]],
            extra_compile_args = {
            'cxx': ['/std:c++17'],  # For MSVC
            'nvcc': [
                '--expt-relaxed-constexpr',
                '-std=c++17',
                '-O3',
                '-U__CUDA_NO_HALF_OPERATORS__',
                '-U__CUDA_NO_HALF_CONVERSIONS__',
                '-U__CUDA_NO_HALF2_OPERATORS__',
                '--use_fast_math',
                '-allow-unsupported-compiler'
            ]
        }
        ),
    ],
    cmdclass={
        'build_ext': BuildExtension,
    }
)
