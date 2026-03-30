"""Board Detection Module - Detects and normalizes chessboard perspective."""
import cv2
import numpy as np
from typing import Tuple, Optional, List
from dataclasses import dataclass


@dataclass
class BoardDetectionResult:
    """Result of board detection."""
    board_image: np.ndarray  # Top-down normalized board
    corners: np.ndarray  # 4 corners of the detected board in original image
    warp_matrix: np.ndarray  # Perspective transform matrix
    confidence: float  # Detection confidence [0, 1]
    success: bool  # Whether detection succeeded


class BoardDetector:
    """Detects chessboard in images and applies perspective transform."""
    
    def __init__(self, board_size: int = 512, min_area_ratio: float = 0.1):
        """
        Initialize board detector.
        
        Args:
            board_size: Output size for normalized board (board_size x board_size)
            min_area_ratio: Minimum area ratio of board w.r.t. image
        """
        self.board_size = board_size
        self.min_area_ratio = min_area_ratio
    
    def detect(self, image: np.ndarray) -> BoardDetectionResult:
        """
        Detect chessboard in image and return normalized perspective.
        
        Args:
            image: Input image (BGR or grayscale)
            
        Returns:
            BoardDetectionResult with detected board and corners
        """
        original_shape = image.shape
        
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # 1. Edge detection
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        
        # 2. Dilate to connect edges
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        edges = cv2.dilate(edges, kernel, iterations=2)
        
        # 3. Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return BoardDetectionResult(
                board_image=np.zeros((self.board_size, self.board_size, 3), dtype=np.uint8),
                corners=np.array([]),
                warp_matrix=np.eye(3),
                confidence=0.0,
                success=False
            )
        
        # 4. Find largest quadrilateral contour
        best_quad = None
        best_area = 0
        
        for contour in contours:
            # Approximate to polygon
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Check if it's a quadrilateral
            if len(approx) == 4:
                area = cv2.contourArea(approx)
                if area > best_area:
                    best_area = area
                    best_quad = approx.reshape(4, 2)
        
        if best_quad is None:
            return BoardDetectionResult(
                board_image=np.zeros((self.board_size, self.board_size, 3), dtype=np.uint8),
                corners=np.array([]),
                warp_matrix=np.eye(3),
                confidence=0.0,
                success=False
            )
        
        # 5. Check if detected area is large enough
        image_area = original_shape[0] * original_shape[1]
        if best_area < image_area * self.min_area_ratio:
            return BoardDetectionResult(
                board_image=np.zeros((self.board_size, self.board_size, 3), dtype=np.uint8),
                corners=np.array([]),
                warp_matrix=np.eye(3),
                confidence=0.0,
                success=False
            )
        
        # 6. Order corners (top-left, top-right, bottom-right, bottom-left)
        corners_ordered = self._order_corners(best_quad)
        
        # 7. Apply perspective transform
        dst_corners = np.array([
            [0, 0],
            [self.board_size - 1, 0],
            [self.board_size - 1, self.board_size - 1],
            [0, self.board_size - 1]
        ], dtype=np.float32)
        
        warp_matrix = cv2.getPerspectiveTransform(
            corners_ordered.astype(np.float32),
            dst_corners.astype(np.float32)
        )
        
        # Apply transform to original image
        if len(image.shape) == 3:
            board_normalized = cv2.warpPerspective(image, warp_matrix, (self.board_size, self.board_size))
        else:
            board_normalized = cv2.warpPerspective(image, warp_matrix, (self.board_size, self.board_size))
            board_normalized = cv2.cvtColor(board_normalized, cv2.COLOR_GRAY2BGR)
        
        # Compute confidence based on corner angles near 90 degrees
        confidence = self._compute_confidence(corners_ordered)
        
        return BoardDetectionResult(
            board_image=board_normalized,
            corners=corners_ordered,
            warp_matrix=warp_matrix,
            confidence=confidence,
            success=True
        )
    
    def _order_corners(self, corners: np.ndarray) -> np.ndarray:
        """
        Order corners in order: top-left, top-right, bottom-right, bottom-left.
        
        Args:
            corners: 4x2 array of corner coordinates
            
        Returns:
            Ordered corners
        """
        # Sort by y-coordinate, then x-coordinate
        corners_sorted = corners[np.lexsort((corners[:, 0], corners[:, 1]))]
        
        # Top two points
        if corners_sorted[0, 0] < corners_sorted[1, 0]:
            tl, tr = corners_sorted[0], corners_sorted[1]
        else:
            tr, tl = corners_sorted[0], corners_sorted[1]
        
        # Bottom two points
        if corners_sorted[2, 0] < corners_sorted[3, 0]:
            bl, br = corners_sorted[2], corners_sorted[3]
        else:
            br, bl = corners_sorted[2], corners_sorted[3]
        
        return np.array([tl, tr, br, bl], dtype=np.float32)
    
    def _compute_confidence(self, corners: np.ndarray) -> float:
        """
        Compute confidence based on corner angles.
        
        Args:
            corners: 4 corners ordered
            
        Returns:
            Confidence score [0, 1]
        """
        angles = []
        for i in range(4):
            p1 = corners[i]
            p2 = corners[(i + 1) % 4]
            p3 = corners[(i + 2) % 4]
            
            v1 = p1 - p2
            v2 = p3 - p2
            
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
            angle = np.arccos(np.clip(cos_angle, -1, 1)) * 180 / np.pi
            
            angles.append(angle)
        
        # Should be close to 90 degrees
        angles = np.array(angles)
        angle_deviations = np.abs(angles - 90)
        confidence = np.exp(-np.mean(angle_deviations) / 30.0)
        
        return float(np.clip(confidence, 0, 1))
    
    def segment_squares(self, board_image: np.ndarray) -> np.ndarray:
        """
        Segment normalized board into 8x8 squares.
        
        Args:
            board_image: Normalized board image (board_size x board_size)
            
        Returns:
            Array of shape (8, 8, square_size, square_size, 3) containing square images
        """
        square_size = self.board_size // 8
        squares = np.zeros((8, 8, square_size, square_size, 3), dtype=np.uint8)
        
        for row in range(8):
            for col in range(8):
                y_start = row * square_size
                x_start = col * square_size
                
                square = board_image[
                    y_start:y_start + square_size,
                    x_start:x_start + square_size
                ]
                
                # Pad if necessary (last row/col might be one pixel short)
                if square.shape[0] < square_size or square.shape[1] < square_size:
                    square = np.pad(
                        square,
                        ((0, square_size - square.shape[0]), 
                         (0, square_size - square.shape[1]), 
                         (0, 0)),
                        mode='edge'
                    )
                
                squares[row, col] = square
        
        return squares
