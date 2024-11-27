#include <torch/extension.h>
#include "gridencoder.h"

// Registering the CUDA functions with PyTorch using pybind11
PYBIND11_MODULE(TORCH_EXTENSION_NAME, m) {
    m.def("grid_encode_forward", &grid_encode_forward, "grid_encode_forward (CUDA)");
    m.def("grid_encode_backward", &grid_encode_backward, "grid_encode_backward (CUDA)");
}
