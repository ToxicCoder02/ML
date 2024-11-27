import torch
import argparse
import shutil
from nerf.provider import NeRFDataset
from nerf.utils_neurallift import *
import gradio as gr
import gc

<<<<<<< HEAD
=======
from datetime import datetime

# Replace colons with hyphens in the timestamp


>>>>>>> repoB/main
from optimizer import Shampoo

import pdb
import os
import yaml, json, types
from datetime import datetime

os.environ['CUDA_HOME'] = r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6'  # Replace with your path
print(torch.cuda.is_available())  # Should return True if CUDA is set up correctly


css = """
.gradio-container {
    max-width: 512px; margin: auto;
} 
"""

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='configs/cabin.yaml', help='load config')
    parser.add_argument('--share', action='store_true', help="do you want to share gradio app to external network?")
    args = parser.parse_args()

    # Load configuration
    with open(args.config, "r") as stream:
        try:
            opt = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    def load_object(dct):
        return types.SimpleNamespace(**dct)
    opt = json.loads(json.dumps(opt), object_hook=load_object)
    print(opt)

    # Set up workspace with Windows-compatible timestamp
    opt.workspace = os.path.basename(args.config).replace('.yaml', '')
<<<<<<< HEAD
    opt.workspace = os.path.join(
        'logs', 
        datetime.today().strftime('%Y-%m-%d'), 
        opt.workspace + '_' + datetime.today().strftime('%H-%M-%S')  # hyphens in timestamp for Windows compatibility
    )
=======
    opt.workspace = os.path.join('logs', str(datetime.today().strftime('%Y-%m-%d')), opt.workspace + '_' + datetime.today().strftime('%H:%M:%S'))
    import os, shutil
    opt.workspace = f"logs/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}/{opt.text.replace(' ', '_')}"
>>>>>>> repoB/main
    os.makedirs(opt.workspace, exist_ok=True)
    shutil.copy(args.config, os.path.join(opt.workspace, os.path.basename(args.config)))

    print('Double Check data path:')
    print(opt.mask_path)
    print(opt.rgb_path)
    print(opt.depth_path)
    print('====================')

    # Backbone selection
    if opt.backbone == 'vanilla':
        from nerf.network import NeRFNetwork
    elif opt.backbone == 'grid_finite':    
        from nerf.network_grid_finite import NeRFNetwork
    else:
        raise NotImplementedError(f'--backbone {opt.backbone} is not implemented!')

    print(opt)

    # Initialize variables
    trainer = None
    model = None

    # Define UI with Gradio
    with gr.Blocks(css=css) as demo:

        # Title and Input Layout
        gr.Markdown('[NeuralLift-360](https://github.com/VITA-Group/NeuralLift-360) Image-to-3D Example')

        with gr.Row().style(equal_height=True):
            ref_im = gr.Image(label="reference_image", elem_id="ref_im", value=opt.rgb_path)
            mask = gr.Image(label="reference_mask", elem_id="ref_mask", value=opt.mask_path)
            with gr.Column(scale=1, min_width=600):
                prompt = gr.Textbox(label="Prompt", max_lines=1, value=opt.text)
                iters = gr.Slider(label="Iters", minimum=1000, maximum=20000, value=opt.iters, step=100)
                seed = gr.Slider(label="Seed", minimum=0, maximum=2147483647, step=1, randomize=True)
        
        button = gr.Button('Generate')

        # Outputs
        image = gr.Image(label="image", visible=True)
        video = gr.Video(label="video", visible=False)
        logs = gr.Textbox(label="logging")

        def submit(text, iters, seed):
            global trainer, model
            opt.seed = seed
            opt.text = text
            opt.iters = iters
    
            seed_everything(opt.seed)

            # Clean up existing model and trainer to free memory
            if trainer is not None:
                del model
                del trainer
                gc.collect()
                torch.cuda.empty_cache()
                print('[INFO] Clean up!')

            # Initialize model
            model = NeRFNetwork(opt)
            print(model)

            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            if opt.guidance == 'sd_clipguide':
                from nerf.sd_clipguide import StableDiffusion
                guidance = StableDiffusion(opt, device, sd_name=opt.sd_name)
            else:
                raise NotImplementedError(f'--guidance {opt.guidance} is not implemented.')

            optimizer = lambda model: torch.optim.AdamW(model.get_params(opt.lr), betas=(0.9, 0.99), eps=1e-15)

            train_loader = NeRFDataset(opt, device=device, type='train', H=opt.h, W=opt.w, size=100).dataloader()
            test_loader = NeRFDataset(opt, device=device, type='test', H=opt.H, W=opt.W, size=100).dataloader()

            opt.max_epoch = int(np.ceil(opt.iters / len(train_loader)))

            scheduler = lambda optimizer: torch.optim.lr_scheduler.LambdaLR(optimizer, lambda iter: 1)  # fixed scheduler

            # Initialize trainer
            trainer = Trainer(
                'lift', opt, model, guidance, device=device, 
                workspace=opt.workspace, optimizer=optimizer, ema_decay=None, 
                fp16=opt.fp16, lr_scheduler=scheduler, use_checkpoint=opt.ckpt, 
                eval_interval=opt.eval_interval, scheduler_update_every_step=True
            )

            trainer.writer = tensorboardX.SummaryWriter(os.path.join(opt.workspace, "run", 'lift'))

            valid_loader = NeRFDataset(opt, device=device, type='val', H=opt.H, W=opt.W, size=5).dataloader()
            opt.max_epoch = int(np.ceil(opt.iters / len(train_loader)))

            # Training loop with progressive updates
            loader = iter(valid_loader)
            start_t = time.time()

            for epoch in tqdm.tqdm(range(opt.max_epoch)):
                STEPS = 100
                
                trainer.train_gui(train_loader, epoch=epoch, step=STEPS)
                
                # Intermediate testing and results display
                try:
                    data = next(loader)
                except StopIteration:
                    loader = iter(valid_loader)
                    data = next(loader)

                trainer.model.eval()
                if trainer.ema is not None:
                    trainer.ema.store()
                    trainer.ema.copy_to()

                with torch.no_grad():
                    with torch.amp.autocast(device_type='cuda', enabled=trainer.fp16):
                        preds, preds_depth, pred_mask = trainer.test_step(data, perturb=False)

                if trainer.ema is not None:
                    trainer.ema.restore()

                pred = (preds[0].detach().cpu().numpy() * 255).astype(np.uint8)

                yield {
                    image: gr.update(value=pred, visible=True),
                    video: gr.update(visible=False),
                    logs: f"Training iters: {epoch * STEPS} / {iters}, lr: {trainer.optimizer.param_groups[0]['lr']:.6f}",
                }

            # Final test and retrieve video result
            trainer.test(test_loader)
            results = sorted(
                glob.glob(os.path.join(opt.workspace, 'results', '*rgb*.mp4')),
                key=lambda x: os.path.getmtime(x)
            )
            
            end_t = time.time()
            
            yield {
                image: gr.update(visible=False),
                video: gr.update(value=results[-1], visible=True),
                logs: f"Generation Finished in {(end_t - start_t) / 60:.4f} minutes!",
            }

        # Button click event
        button.click(submit, [prompt, iters, seed], [image, video, logs])

    # Allow only one concurrent process
    demo.queue(concurrency_count=1)
    demo.launch(share=args.share, debug=True)
