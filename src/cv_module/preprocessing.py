"""Image preprocessing utilities."""
import cv2
import numpy as np
from typing import Tuple, Optional


def normalize_image(image: np.ndarray) -> np.ndarray:
    """
    Normalize image to [0, 1] range.
    
    Args:
        image: Input image array
        
    Returns:
        Normalized image
    """
    if image.dtype == np.uint8:
        return image.astype(np.float32) / 255.0
    return image


def denormalize_image(image: np.ndarray) -> np.ndarray:
    """
    Convert normalized image back to [0, 255] uint8.
    
    Args:
        image: Normalized image array
        
    Returns:
        Uint8 image
    """
    return (np.clip(image, 0, 1) * 255).astype(np.uint8)


def apply_contrast_stretch(image: np.ndarray) -> np.ndarray:
    """
    Apply CLAHE (Contrast Limited Adaptive Histogram Equalization).
    
    Args:
        image: Input image (3-channel or grayscale)
        
    Returns:
        Contrast-stretched image
    """
    if len(image.shape) == 3:
        # Convert to LAB, apply CLAHE to L channel
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        lab[:, :, 0] = clahe.apply(lab[:, :, 0])
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    else:
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        return clahe.apply(image)


def resize_image(image: np.ndarray, max_dimension: int = 1024) -> np.ndarray:
    """
    Resize image if any dimension exceeds max_dimension.
    
    Args:
        image: Input image
        max_dimension: Maximum allowed dimension
        
    Returns:
        Resized image
    """
    height, width = image.shape[:2]
    if max(height, width) > max_dimension:
        scale = max_dimension / max(height, width)
        new_width = int(width * scale)
        new_height = int(height * scale)
        return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    return image
