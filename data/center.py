import numpy as np
import cv2
import os

# Prefix for file names
prefix = 'cabin4'

# Check if files exist before proceeding
mask_path = f"{prefix}_mask.png"
depth_path = f"{prefix}.npy"
image_path = f"{prefix}.png"

if not os.path.exists(mask_path):
    raise FileNotFoundError(f"Mask file not found: {mask_path}")
if not os.path.exists(depth_path):
    raise FileNotFoundError(f"Depth file not found: {depth_path}")
if not os.path.exists(image_path):
    raise FileNotFoundError(f"Image file not found: {image_path}")

# Load files
msk = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE) / 255.0
depth = np.load(depth_path)
im = cv2.imread(image_path)

# Resize depth map to 512x512
depth = cv2.resize(depth, (512, 512))

# Validate shapes
if msk.shape != (512, 512):
    raise ValueError(f"Mask shape mismatch. Expected (512, 512), got {msk.shape}")
if im.shape[:2] != (512, 512):
    raise ValueError(f"Image shape mismatch. Expected (512, 512), got {im.shape[:2]}")

print(f"Loaded shapes - Mask: {msk.shape}, Depth: {depth.shape}, Image: {im.shape}")

# Get non-zero positions in the mask
positions = np.nonzero(msk)

if len(positions[0]) == 0 or len(positions[1]) == 0:
    raise ValueError("Mask is empty, no non-zero positions found.")

# Find bounding box of the non-zero mask area
top = positions[0].min()
bottom = positions[0].max()
left = positions[1].min()
right = positions[1].max()

# Create new centered mask, depth, and image
new_mask = np.zeros((512, 512), dtype=np.float32)
new_depth = np.zeros((512, 512), dtype=np.float32)
new_im = np.zeros((512, 512, 3), dtype=np.uint8)

# Calculate new bounding box centered in the 512x512 image
new_left = 256 - (right - left) // 2
new_right = new_left + (right - left)
new_top = 256 - (bottom - top) // 2
new_bottom = new_top + (bottom - top)

# Center the object within the new mask, depth, and image
new_mask[new_top:new_bottom, new_left:new_right] = msk[top:bottom, left:right]
new_depth[new_top:new_bottom, new_left:new_right] = depth[top:bottom, left:right]
new_im[new_top:new_bottom, new_left:new_right, :] = im[top:bottom, left:right, :]

# Save the centered outputs
cv2.imwrite(f"{prefix}_centered_mask.png", (new_mask * 255).astype(np.uint8))
np.save(f"{prefix}_centered.npy", new_depth)
cv2.imwrite(f"{prefix}_centered.png", new_im)

print("Centered mask, depth, and image have been saved successfully.")
