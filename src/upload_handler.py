"""
Image Upload Handler
Validates and manages chess board image uploads
"""

import os
import hashlib
from pathlib import Path
from typing import Tuple, Optional, Dict
import tempfile
from datetime import datetime
import cv2
import numpy as np


class ImageUploadHandler:
    """Handle image uploads and validation for chess board analysis"""
    
    ALLOWED_FORMATS = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_DIMENSION = 4096  # Maximum image dimension
    MIN_DIMENSION = 200   # Minimum image dimension
    
    def __init__(self, upload_dir: Optional[str] = None):
        """
        Initialize upload handler
        
        Args:
            upload_dir: Directory for temporary uploads (defaults to temp dir)
        """
        if upload_dir is None:
            upload_dir = os.path.join(tempfile.gettempdir(), 'chess_uploads')
        
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)
    
    def validate_image(self, file_path: str) -> Tuple[bool, str]:
        """
        Validate uploaded image file
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file exists
        if not os.path.exists(file_path):
            return False, "File does not exist"
        
        # Check file extension
        ext = Path(file_path).suffix.lower()
        if ext not in self.ALLOWED_FORMATS:
            return False, f"Invalid format. Allowed: {', '.join(self.ALLOWED_FORMATS)}"
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > self.MAX_FILE_SIZE:
            return False, f"File too large. Max: {self.MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
        
        if file_size < 1000:
            return False, "File too small"
        
        # Check image validity and dimensions
        try:
            img = cv2.imread(file_path)
            if img is None:
                return False, "Cannot read image file"
            
            height, width = img.shape[:2]
            
            if height < self.MIN_DIMENSION or width < self.MIN_DIMENSION:
                return False, f"Image too small. Min: {self.MIN_DIMENSION}x{self.MIN_DIMENSION}"
            
            if height > self.MAX_DIMENSION or width > self.MAX_DIMENSION:
                return False, f"Image too large. Max: {self.MAX_DIMENSION}x{self.MAX_DIMENSION}"
            
            # Check if image has reasonable aspect ratio (not too stretched)
            aspect_ratio = max(width, height) / min(width, height)
            if aspect_ratio > 3:
                return False, f"Image aspect ratio too extreme ({aspect_ratio:.1f}:1)"
            
            return True, "Valid image"
            
        except Exception as e:
            return False, f"Error reading image: {str(e)}"
    
    def save_uploaded_image(self, file_path: str, custom_name: Optional[str] = None) -> str:
        """
        Save uploaded image to managed directory
        
        Args:
            file_path: Source file path
            custom_name: Custom name for the file (without extension)
            
        Returns:
            Path to saved image
            
        Raises:
            ValueError: If image is invalid
        """
        is_valid, error_msg = self.validate_image(file_path)
        if not is_valid:
            raise ValueError(f"Image validation failed: {error_msg}")
        
        ext = Path(file_path).suffix.lower()
        
        if custom_name:
            saved_name = f"{custom_name}{ext}"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            hash_suffix = hashlib.md5(open(file_path, 'rb').read()).hexdigest()[:8]
            saved_name = f"chess_{timestamp}_{hash_suffix}{ext}"
        
        saved_path = os.path.join(self.upload_dir, saved_name)
        
        # Copy or move file
        import shutil
        shutil.copy2(file_path, saved_path)
        
        return saved_path
    
    def get_image_metadata(self, file_path: str) -> Dict:
        """
        Get metadata about uploaded image
        
        Args:
            file_path: Path to image file
            
        Returns:
            Dictionary with image metadata
        """
        try:
            img = cv2.imread(file_path)
            if img is None:
                return {}
            
            height, width = img.shape[:2]
            channels = img.shape[2] if len(img.shape) > 2 else 1
            file_size = os.path.getsize(file_path)
            
            # Calculate histogram statistics
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if channels >= 3 else img
            
            return {
                "file_size": file_size,
                "width": int(width),
                "height": int(height),
                "channels": int(channels),
                "aspect_ratio": float(width / height),
                "mean_brightness": float(np.mean(gray)),
                "std_brightness": float(np.std(gray)),
                "file_name": os.path.basename(file_path),
                "upload_time": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def cleanup_old_uploads(self, max_age_hours: int = 24):
        """
        Clean up old temporary uploads
        
        Args:
            max_age_hours: Remove files older than this many hours
        """
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for filename in os.listdir(self.upload_dir):
                file_path = os.path.join(self.upload_dir, filename)
                file_age = current_time - os.path.getmtime(file_path)
                
                if file_age > max_age_seconds:
                    os.remove(file_path)
        except Exception as e:
            print(f"Warning: Could not cleanup old uploads: {e}")
    
    def preprocess_for_analysis(self, file_path: str, target_size: int = 1024) -> np.ndarray:
        """
        Preprocess image for chess board analysis
        
        Args:
            file_path: Path to image
            target_size: Target size to resize to
            
        Returns:
            Preprocessed image array
        """
        img = cv2.imread(file_path)
        
        # Resize maintaining aspect ratio
        h, w = img.shape[:2]
        scale = target_size / max(h, w)
        new_h, new_w = int(h * scale), int(w * scale)
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        # Pad to square
        canvas = np.zeros((target_size, target_size, 3), dtype=img.dtype)
        y_offset = (target_size - new_h) // 2
        x_offset = (target_size - new_w) // 2
        canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = img
        
        # Enhance contrast using CLAHE
        gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray_enhanced = clahe.apply(gray)
        
        # Convert back to BGR
        result = cv2.cvtColor(gray_enhanced, cv2.COLOR_GRAY2BGR)
        
        return result


if __name__ == "__main__":
    # Test the upload handler
    handler = ImageUploadHandler()
    print(f"Upload directory: {handler.upload_dir}")
    print(f"Allowed formats: {handler.ALLOWED_FORMATS}")
    print(f"Max file size: {handler.MAX_FILE_SIZE / 1024 / 1024:.1f}MB")
