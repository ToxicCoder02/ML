import os
from setuptools import setup
from torch.utils.cpp_extension import BuildExtension, CUDAExtension

_src_path = os.path.dirname(os.path.abspath(__file__))

os.environ['TORCH_CUDA_ARCH_LIST'] = '7.5'

nvcc_flags = [
    '-O3', '-std=c++17',  # Change from c++14 to c++17
    '-U__CUDA_NO_HALF_OPERATORS__', '-U__CUDA_NO_HALF_CONVERSIONS__', '-U__CUDA_NO_HALF2_OPERATORS__',
    '-allow-unsupported-compiler'  # Keep the unsupported compiler flag if needed
]


if os.name == "posix":
    c_flags = ['-O3', '-std=c++17']  # Change from c++14 to c++17 if needed for POSIX
elif os.name == "nt":
    c_flags = ['/O2', '/std:c++17']  # Set to c++17 for Windows


    # Function to find the path to cl.exe (Visual Studio compiler)
    def find_cl_path():
        import glob
        for edition in ["Enterprise", "Professional", "BuildTools", "Community"]:
            paths = sorted(glob.glob(r"C:\\Program Files (x86)\\Microsoft Visual Studio\\*\\%s\\VC\\Tools\\MSVC\\*\\bin\\Hostx64\\x64" % edition), reverse=True)
            if paths:
                return paths[0]

    # If cl.exe is not in PATH, add it manually
    if os.system("where cl.exe >nul 2>nul") != 0:
        cl_path = find_cl_path()
        if cl_path is None:
            raise RuntimeError("Could not locate a supported Microsoft Visual C++ installation")
        os.environ["PATH"] += ";" + cl_path

'''
Usage:

python setup.py build_ext --inplace # Build extensions locally, do not install (only usable from the parent directory)
python setup.py install # Build extensions and install (copy) to PATH
pip install . # Preferred alternative, handles dependency & metadata
python setup.py develop # Build extensions and install (symbolic) to PATH
pip install -e . # Preferred alternative, handles dependency & metadata
'''

setup(
    name='raymarching',  # Package name, import this to use Python API
    ext_modules=[
        CUDAExtension(
            name='_raymarching',  # Extension name, import this to use CUDA API
            sources=[os.path.join(_src_path, 'src', f) for f in [
                'raymarching.cu',
                'bindings.cpp',
            ]],
            extra_compile_args={
                'cxx': c_flags,
                'nvcc': nvcc_flags,
            }
        ),
    ],
    cmdclass={
        'build_ext': BuildExtension,
    }
)
