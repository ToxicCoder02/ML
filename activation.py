import torch
from torch.autograd import Function
from torch.cuda.amp import custom_bwd, custom_fwd 

class _trunc_exp(Function):
    @custom_fwd(cast_inputs=torch.float)
    def forward(ctx, x):
        ctx.save_for_backward(x)
        return torch.exp(x.clamp(max=5)) - 1

    @custom_bwd
    def backward(ctx, g):
        x, = ctx.saved_tensors
        return g * torch.exp(x.clamp(max=5))

trunc_exp = _trunc_exp.apply