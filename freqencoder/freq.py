import numpy as np
import torch
import torch.nn as nn
from torch.autograd import Function
from torch.cuda.amp import custom_bwd, custom_fwd

# Attempt to import the CUDA extension
try:
    import _freqencoder as _backend
except ImportError:
    from .backend import _backend


class _freq_encoder(Function):
    @staticmethod
    @custom_fwd(cast_inputs=torch.float32)
    def forward(ctx, inputs, degree, output_dim):
        """
        Forward pass for frequency encoding.
        Args:
            inputs (Tensor): Input tensor of shape [B, input_dim]
            degree (int): Degree of encoding
            output_dim (int): Output dimension after encoding
        Returns:
            Tensor: Encoded output of shape [B, output_dim]
        """
        if not inputs.is_cuda:
            inputs = inputs.cuda()
        inputs = inputs.contiguous()

        B, input_dim = inputs.shape  # Batch size, coordinate dimension
        outputs = torch.empty(B, output_dim, dtype=inputs.dtype, device=inputs.device)

        # Call the CUDA backend for forward pass
        _backend.freq_encode_forward(inputs, B, input_dim, degree, output_dim, outputs)

        # Save tensors and dimensions for backward pass
        ctx.save_for_backward(inputs, outputs)
        ctx.dims = (B, input_dim, degree, output_dim)

        return outputs

    @staticmethod
    @custom_bwd
    def backward(ctx, grad):
        """
        Backward pass for frequency encoding.
        Args:
            grad (Tensor): Gradient tensor of shape [B, output_dim]
        Returns:
            Tensor: Gradient w.r.t. inputs of shape [B, input_dim]
        """
        grad = grad.contiguous()
        inputs, outputs = ctx.saved_tensors
        B, input_dim, degree, output_dim = ctx.dims

        # Initialize gradient tensor for inputs
        grad_inputs = torch.zeros_like(inputs)

        # Call the CUDA backend for backward pass
        _backend.freq_encode_backward(grad, outputs, B, input_dim, degree, output_dim, grad_inputs)

        return grad_inputs, None, None


# Alias for the custom function
freq_encode = _freq_encoder.apply


class FreqEncoder(nn.Module):
    def __init__(self, input_dim=3, degree=4):
        """
        Frequency encoder module.
        Args:
            input_dim (int): Dimension of input coordinates.
            degree (int): Degree of frequency encoding.
        """
        super().__init__()
        self.input_dim = input_dim
        self.degree = degree
        self.output_dim = input_dim + input_dim * 2 * degree

    def __repr__(self):
        return f"FreqEncoder(input_dim={self.input_dim}, degree={self.degree}, output_dim={self.output_dim})"

    def forward(self, inputs):
        """
        Forward pass for the frequency encoder.
        Args:
            inputs (Tensor): Input tensor of shape [..., input_dim]
        Returns:
            Tensor: Encoded output tensor of shape [..., output_dim]
        """
        prefix_shape = list(inputs.shape[:-1])
        inputs = inputs.reshape(-1, self.input_dim)

        # Apply frequency encoding
        outputs = freq_encode(inputs, self.degree, self.output_dim)

        # Reshape the output to match the input's batch dimensions
        outputs = outputs.reshape(prefix_shape + [self.output_dim])
        return outputs
