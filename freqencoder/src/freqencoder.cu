#include <stdint.h>
#include <cuda.h>
#include <cuda_fp16.h>
#include <cuda_runtime.h>

#include <ATen/cuda/CUDAContext.h>
#include <torch/torch.h>

#include <algorithm>
#include <stdexcept>
#include <cstdio>

#define CHECK_CUDA(x) TORCH_CHECK(x.device().is_cuda(), #x " must be a CUDA tensor")
#define CHECK_CONTIGUOUS(x) TORCH_CHECK(x.is_contiguous(), #x " must be a contiguous tensor")
#define CHECK_IS_FLOATING(x) TORCH_CHECK(x.scalar_type() == at::ScalarType::Float || x.scalar_type() == at::ScalarType::Half || x.scalar_type() == at::ScalarType::Double, #x " must be a floating tensor")

inline constexpr __device__ float PI() { return 3.141592653589793f; }

template <typename T>
__host__ __device__ T div_round_up(T val, T divisor) {
    return (val + divisor - 1) / divisor;
}

// Forward Pass Kernel
__global__ void kernel_freq(
    const float * __restrict__ inputs, 
    uint32_t B, uint32_t D, uint32_t deg, uint32_t C,
    float * outputs
) {
    const uint32_t t = threadIdx.x + blockIdx.x * blockDim.x;
    if (t >= B * C) return;

    const uint32_t b = t / C;
    const uint32_t c = t % C;

    inputs += b * D;
    outputs += t;

    if (c < D) {
        outputs[0] = inputs[c];
    } else {
        const uint32_t col = c / D - 1;
        const uint32_t d = c % D;
        const uint32_t freq = col / 2;
        const float phase_shift = (col % 2) * (PI() / 2);
        outputs[0] = sinf(inputs[d] * (1 << freq) + phase_shift);
    }
}

// Backward Pass Kernel
__global__ void kernel_freq_backward(
    const float * __restrict__ grad,
    const float * __restrict__ outputs,
    uint32_t B, uint32_t D, uint32_t deg, uint32_t C,
    float * grad_inputs
) {
    const uint32_t t = threadIdx.x + blockIdx.x * blockDim.x;
    if (t >= B * D) return;

    const uint32_t b = t / D;
    const uint32_t d = t % D;

    grad += b * C;
    outputs += b * C;
    grad_inputs += t;

    float result = grad[d];
    grad += D;
    outputs += D;

    for (uint32_t f = 0; f < deg; ++f) {
        result += (1 << f) * (grad[d] * outputs[d] - grad[D + d] * outputs[d]);
        grad += 2 * D;
        outputs += 2 * D;
    }
    grad_inputs[0] = result;
}

// Forward Function
void freq_encode_forward(at::Tensor inputs, uint32_t B, uint32_t D, uint32_t deg, uint32_t C, at::Tensor outputs) {
    CHECK_CUDA(inputs);
    CHECK_CUDA(outputs);
    CHECK_CONTIGUOUS(inputs);
    CHECK_CONTIGUOUS(outputs);
    CHECK_IS_FLOATING(inputs);
    CHECK_IS_FLOATING(outputs);

    constexpr uint32_t N_THREADS = 128;
    const uint32_t num_blocks = div_round_up(B * C, N_THREADS);

    kernel_freq<<<num_blocks, N_THREADS>>>(inputs.data_ptr<float>(), B, D, deg, C, outputs.data_ptr<float>());

    // Error checking
    cudaError_t err = cudaGetLastError();
    if (err != cudaSuccess) {
        throw std::runtime_error("CUDA error in freq_encode_forward: " + std::string(cudaGetErrorString(err)));
    }
}

// Backward Function
void freq_encode_backward(at::Tensor grad, at::Tensor outputs, uint32_t B, uint32_t D, uint32_t deg, uint32_t C, at::Tensor grad_inputs) {
    CHECK_CUDA(grad);
    CHECK_CUDA(outputs);
    CHECK_CUDA(grad_inputs);
    CHECK_CONTIGUOUS(grad);
    CHECK_CONTIGUOUS(outputs);
    CHECK_CONTIGUOUS(grad_inputs);
    CHECK_IS_FLOATING(grad);
    CHECK_IS_FLOATING(outputs);
    CHECK_IS_FLOATING(grad_inputs);

    constexpr uint32_t N_THREADS = 128;
    const uint32_t num_blocks = div_round_up(B * D, N_THREADS);

    kernel_freq_backward<<<num_blocks, N_THREADS>>>(grad.data_ptr<float>(), outputs.data_ptr<float>(), B, D, deg, C, grad_inputs.data_ptr<float>());

    // Error checking
    cudaError_t err = cudaGetLastError();
    if (err != cudaSuccess) {
        throw std::runtime_error("CUDA error in freq_encode_backward: " + std::string(cudaGetErrorString(err)));
    }
}
