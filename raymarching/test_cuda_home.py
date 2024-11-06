import os
import torch

# Check CUDA_HOME
cuda_home = os.environ.get('CUDA_HOME')
print("CUDA_HOME:", cuda_home)

# Check if torch detects CUDA
print("Is CUDA available:", torch.cuda.is_available())

# Additional verification of paths
if cuda_home:
    nvcc_path = os.path.join(cuda_home, 'bin', 'nvcc.exe')
    print("Does nvcc exist:", os.path.isfile(nvcc_path))
    lib64_path = os.path.join(cuda_home, 'lib', 'x64')
    print("Does lib64 exist:", os.path.isdir(lib64_path))
