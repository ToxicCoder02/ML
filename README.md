# NeuralLift-360: Elevating 2D Images to Immersive 3D Models with Full 360° Views

## Overview

NeuralLift-360 provides an innovative approach for transforming standard 2D images into fully navigable 3D models with 360° views. This project leverages depth estimation and neural rendering techniques, allowing creators to build high-fidelity 3D objects from photos captured in unconstrained environments.

### Quick Links
- **[Paper](https://arxiv.org/abs/2211.16431)**
- **[Project Website](https://vita-group.github.io/NeuralLift-360/)**

### Recent Updates
- **March 12, 2023**: Initial workflow and Gradio application have been released, enabling users to explore and experiment with the tool through a user-friendly interface.

## Pipeline Overview

NeuralLift-360 uses a multi-step pipeline to create realistic 3D representations from 2D photos. Below is a high-level breakdown of the process:

1. **Depth Estimation**: Integrates the output from robust depth estimation models.
2. **Foreground Segmentation**: Isolates the primary object for accurate modeling.
3. **3D Reconstruction**: Leverages neural rendering to create a 3D model with full 360° views.
4. **Refinement and Training**: Uses specialized techniques to optimize the quality of the 3D model.

![NeuralLift-360 Pipeline](./docs/static/media/framework-crop-1.b843bf7d1c3c29c01fb2.jpg)

## Setting Up Your Environment

Install all the required dependencies with a single command:

```bash
pip install -r requirements.txt
```

For users interested in running the interactive application, install Gradio separately:

```bash
pip install gradio
```

### Gradio Application

To run the interactive Gradio App for testing your 3D transformations:

```bash
python gradio_app.py
# Use `--share` to create a public link
```

**Note**: The current version loads configurations from pre-defined YAML files. The app is slower than the direct training script as it includes rendering during training.

## Preparing Your Data

**Depth Estimation**: NeuralLift-360 requires accurate depth maps to build convincing 3D models. We recommend using [Boost Your Own Depth](https://github.com/compphoto/BoostingMonocularDepth) alongside [LeRes](https://github.com/aim-uofa/AdelaiDepth/tree/main/LeReS) for robust depth estimation.

- Export depth maps in NumPy format using this [Google Colab Notebook](https://colab.research.google.com/drive/15YCsqaO6l94HueVwPQgHqVVDUJzdOEO5?usp=sharing).

**Foreground Masking**: To extract the main object from its background, use the [image-background-remove-tool](https://github.com/Ir1d/image-background-remove-tool).

## Training Your Model

Configurations for training are provided in YAML format within the `configs` directory. To start training:

```bash
python main.py --config configs/cabin.yaml
```

### Optional: Textual Inversion for Enhanced Embeddings

To improve text embeddings, you can run text inversion. This step provides a more context-aware model for generating 3D objects:

```bash
export MODEL_NAME="runwayml/stable-diffusion-v1-5"
accelerate launch text_inversion.py \
  --pretrained_model_name_or_path=$MODEL_NAME \
  --learnable_property="object" \
  --placeholder_token="<cabin>" --initializer_token="cabin" \
  --resolution=512 \
  --train_batch_size=1 \
  --gradient_accumulation_steps=4 \
  --max_train_steps=1000 \
  --learning_rate=5.0e-04 --scale_lr \
  --lr_scheduler="constant" \
  --lr_warmup_steps=0 \
  --output_dir="cabin_ti" \
  --im_path='data/cabin4_centered.png' \
  --mask_path='data/cabin4_centered_mask.png'
```

After training, validate the performance using `test_dm.py`. Configuration for textual inversion can be found in `configs/cabin_ti.yaml`. To train using these settings:

```bash
python main.py --config configs/cabin_ti.yaml
```

### Future Features: Imagic Fine-tuning

We are working on implementing advanced fine-tuning methods, such as Imagic, to further enhance the generated 3D models. Stay tuned for upcoming updates!

## Testing and Output

Once training is complete, the code automatically generates a video named `lift_ep0100_rgb.mp4` showcasing the 360° view of the 3D object. To locate these videos in your project directory:

```bash
find ./ -name lift_ep0100_rgb.mp4 -printf "%T@ %Tc %p\n" | sort -n
```

### Running Tests Only

To run tests without additional training, modify your YAML configuration:

- Set `test: False` to `test: True`.
- Update the `ckpt` path to your trained checkpoint.

## Acknowledgements

NeuralLift-360 is built upon the foundations laid by [Stable DreamFusion](https://github.com/ashawkey/stable-dreamfusion). Special thanks to [Jiaxiang Tang](https://me.kiui.moe/) for invaluable discussions and insights that contributed to this project.

## Citing NeuralLift-360

If you use NeuralLift-360 in your research or projects, please consider citing:

```
@InProceedings{Xu_2022_neuralLift,
author = {Xu, Dejia and Jiang, Yifan and Wang, Peihao and Fan, Zhiwen and Wang, Yi and Wang, Zhangyang},
title = {NeuralLift-360: Lifting An In-the-wild 2D Photo to A 3D Object with 360° Views},
journal={arXiv preprint arXiv:2211.16431},
year={2022}
}
```

## Future Work and Roadmap

We are committed to enhancing NeuralLift-360 with additional features, improved performance, and user-friendly tutorials. Follow the [project website](https://vita-group.github.io/NeuralLift-360/) for the latest updates and resources.
