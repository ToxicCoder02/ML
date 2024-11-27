import os
from torch.utils.cpp_extension import load

_src_path = os.path.dirname(os.path.abspath(__file__))

# CUDA compilation flags
nvcc_flags = [
    '-O3', '-std=c++14',
    '-U__CUDA_NO_HALF_OPERATORS__', '-U__CUDA_NO_HALF_CONVERSIONS__', '-U__CUDA_NO_HALF2_OPERATORS__',
    '--use_fast_math',
    '-gencode', 'arch=compute_86,code=sm_86',  # Adjust based on your GPU architecture
    '-I"C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.6/include"',
    '-L"C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.6/lib/x64"'
]

# Compilation flags for Windows (MSVC)
if os.name == "posix":
    c_flags = ['-O3', '-std=c++14']
elif os.name == "nt":
    c_flags = ['/O2', '/std:c++17']

    # Find cl.exe for MSVC
    def find_cl_path():
        import glob
        for edition in ["Enterprise", "Professional", "BuildTools", "Community"]:
            paths = sorted(
                glob.glob(r"C:\\Program Files (x86)\\Microsoft Visual Studio\\*\\%s\\VC\\Tools\\MSVC\\*\\bin\\Hostx64\\x64" % edition),
                reverse=True
            )
            if paths:
                return paths[0]

    # Add cl.exe to PATH if not found
    if os.system("where cl.exe >nul 2>nul") != 0:
        cl_path = find_cl_path()
        if cl_path is None:
            raise RuntimeError("Could not locate a supported Microsoft Visual C++ installation")
        os.environ["PATH"] += ";" + cl_path

# Load the CUDA extension
_backend = load(
    name='_freqencoder',
    extra_cflags=c_flags,
    extra_cuda_cflags=nvcc_flags,
    sources=[os.path.join(_src_path, 'src', f) for f in [
        'freqencoder.cu',
        'bindings.cpp',
    ]]
)

__all__ = ['_backend']
