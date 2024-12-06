Here’s an updated version of the README with the workflow shown separately, ensuring clarity and better visibility:

---

# **NeuralLift-360: Single-Image 3D Reconstruction**

### **A Forked and Extended Implementation of NeuralLift-360**

---

## **Table of Contents**
1. [Introduction](#introduction)
2. [Core Features](#core-features)
3. [Team Members and Contributions](#team-members-and-contributions)
4. [Workflow](#workflow)
5. [Installation](#installation)
6. [Usage Guide](#usage-guide)
7. [Experimental Results](#experimental-results)
8. [Visual Outputs](#visual-outputs)
9. [Optimized Hyperparameters](#optimized-hyperparameters)
10. [Google Colab Links](#google-colab-links)
11. [Acknowledgments and References](#acknowledgments-and-references)

---

## **Introduction**

NeuralLift-360 is a state-of-the-art neural rendering framework designed to generate photorealistic 3D objects from single 2D images. By integrating advanced methodologies like CLIP embeddings and Neural Radiance Fields (NeRF), the framework reconstructs unseen textures and geometry with exceptional accuracy. 

This repository extends the original implementation with significant optimizations for hardware constraints, systematic hyperparameter tuning, and performance analysis.

---

## **Core Features**
- **Photorealistic Textures**: Reconstructs textures with high fidelity using CLIP-guided models.
- **Geometry Consistency**: Maintains 3D object structural coherence across all angles.
- **Efficiency**: Adapted for Google Colab and T4 GPUs (15GB VRAM).
- **Customizability**: Parameter tuning for batch size, resolution, and training stability.

---

## **Team Members and Contributions**

| Name                 | GitHub Username              | Contribution                                    |
|----------------------|------------------------------|------------------------------------------------|
| **Aryan Sharma**     | [@ToxicCoder02](https://github.com/ToxicCoder02) | Project Lead: Hyperparameter tuning, result validation, and overall framework optimization. |
| **Shreyas Gupta**    | [@ShreyasG](#)              | NFC integration and debugging.                 |
| **Niraj Patel**      | [@NirajP](#)                | LoRa communication system and testing.         |
| **Atchyut Kumar**    | [@AtchyutK](#)              | UI enhancements, testing coordination, and documentation. |

To verify contributions, refer to the `git log` in the repository.

---

## **Workflow**

The following diagram illustrates the complete pipeline for generating 3D reconstructions from a single 2D image using NeuralLift-360:

![Workflow Diagram](images/Workflow.png)

---

## **Installation**

Clone the repository and install dependencies:
```bash
git clone https://github.com/ToxicCoder02/ML-Project.git
cd ML-Project
pip install -r requirements.txt
```

---

## **Usage Guide**

1. **Prepare Input**: Place your 2D image in the `inputs/` folder.
2. **Run the Pipeline**:
   ```bash
   python main.py --input inputs/sample.jpg --output outputs/
   ```
3. **Adjust Parameters**: Edit `config.yaml` for batch size, resolution, and CLIP weights.
4. **Output Files**: Results will be saved in the `outputs/` directory.

---

## **Experimental Results**

### **Training Efficiency**

#### **CLIP Weight Observations**
| CLIP Weight | GPU VRAM Usage | Training Time | Final Loss | Output Quality                                                                                     |
|-------------|-----------------|---------------|------------|---------------------------------------------------------------------------------------------------|
| 1           | ~9 GB           | ~20 minutes   | 0.2543     | Poor alignment: Textures lacked clarity, geometry was overly simplified, and output diverged.    |
| **10**      | **~11 GB**      | **~22 minutes** | **0.2113** | **Balanced alignment**: Textures were sharper, geometry was stable, closely resembling input.    |
| 20          | ~13 GB          | ~22.5 minutes | 0.2198     | Over-sharpening: Textures became overly detailed, leading to artifacts, and geometry inconsistencies. |

#### **Optimized Parameters**
| Parameter            | Value             |
|----------------------|-------------------|
| Batch Size           | 256               |
| Training Resolution  | 128×128           |
| Rendering Resolution | 200×200           |
| CLIP Guidance Weight | 10                |
| Timestep Annealing   | Exponential Decay |
| Iterations           | 6000              |

---

## **Visual Outputs**

### **Reconstructed 3D Outputs**

#### **Comparative Outputs with Resolutions**
| Training Resolution | RGB Output                                      | Depth Output                                      |
|----------------------|------------------------------------------------|--------------------------------------------------|
| 32×32               | <video src="/images/lift_ep0010_rgb (2)_32.mp4" controls width="300"></video> | <video src="/images/lift_ep0010_depth (2)_32.mp4" controls width="300"></video> |
| 128×128             | <video src="/images/lift_ep0010_rgb (2)_128.mp4" controls width="300"></video> | <video src="/images/lift_ep0010_depth (2)_128.mp4" controls width="300"></video> |
| 256×256             | <video src="/images/lift_ep0010_rgb (2)_256.mp4" controls width="300"></video> | <video src="/images/lift_ep0010_depth (2)_256.mp4" controls width="300"></video> |

#### **Single Image to RGB 360° View**
- Input Image:
  <img src="/images/input_image.jpg" alt="Input Image Example" width="300">

- Reconstructed RGB 360° View:
  <video src="/images/lift_ep0010_rgb.mp4" controls width="600"></video>

- Depth 360° View:
  <video src="/images/lift_ep0010_depth.mp4" controls width="600"></video>

---

## **Google Colab Links**

Here are some pre-configured notebooks for quick experimentation:
1. [Quick Start with Default Parameters](#)
2. [Advanced Reconstruction](#)
3. [Resolution vs. Quality Testing](#)
4. [CLIP Weight Optimization](#)
5. [Multi-Object Batch Processing](#)

---

## **Acknowledgments and References**

### **Acknowledgments**
- Original framework by [VITA-Group](https://github.com/VITA-Group/NeuralLift-360).
- GPU resources and development environment provided by Google Colab.

### **References**
1. [NeuralLift-360: GitHub Repository](https://github.com/VITA-Group/NeuralLift-360)
2. [CLIP: Learning Transferable Visual Models From Natural Language Supervision](https://arxiv.org/abs/2103.00020)
3. [NeRF: Neural Radiance Fields](https://arxiv.org/abs/2003.08934)
4. [NVIDIA T4 GPU Architecture](https://www.nvidia.com/en-us/data-center/tesla-t4/)

---

This README separates the workflow into its own section and maintains clarity by emphasizing key outputs and configurations with better organization.
