"""Piece Classification Module - Classifies chess pieces in board squares."""
import cv2
import numpy as np
from typing import Tuple, Dict
from dataclasses import dataclass


@dataclass
class ClassificationResult:
    """Result of piece classification."""
    board_matrix: np.ndarray  # 8x8 array with piece strings
    confidence_map: np.ndarray  # 8x8 array with confidence scores
    raw_predictions: np.ndarray  # 8x8 array with class indices


class PieceClassifier:
    """Classifies chess pieces using heuristic-based approach (CNN ready for future)."""
    
    # FEN piece notation
    PIECE_CLASSES = {
        'empty': 0,
        'P': 1, 'N': 2, 'B': 3, 'R': 4, 'Q': 5, 'K': 6,  # White
        'p': 7, 'n': 8, 'b': 9, 'r': 10, 'q': 11, 'k': 12  # Black
    }
    
    CLASS_TO_PIECE = {v: k for k, v in PIECE_CLASSES.items()}
    
    def __init__(self, model_path: str = None):
        """
        Initialize piece classifier.
        
        Args:
            model_path: Path to pretrained model (optional, for CNN version)
        """
        self.model_path = model_path
        self.model = None
        self._init_heuristics()
    
    def _init_heuristics(self):
        """Initialize heuristic parameters for color/shape-based classification."""
        # White piece color ranges (depends on board style)
        self.white_lower = np.array([200, 200, 200])
        self.white_upper = np.array([255, 255, 255])
        
        # Black piece color ranges
        self.black_lower = np.array([0, 0, 0])
        self.black_upper = np.array([50, 50, 50])
    
    def classify(self, squares: np.ndarray) -> ClassificationResult:
        """
        Classify pieces in each square of the 8x8 board.
        
        Args:
            squares: Array of shape (8, 8, square_size, square_size, 3)
                    Output from BoardDetector.segment_squares()
        
        Returns:
            ClassificationResult with board matrix and confidence scores
        """
        board_matrix = np.empty((8, 8), dtype=object)
        confidence_map = np.zeros((8, 8))
        raw_predictions = np.zeros((8, 8), dtype=int)
        
        for row in range(8):
            for col in range(8):
                square_img = squares[row, col]
                piece_class, confidence = self._classify_square(square_img)
                
                # Convert class index to piece notation
                piece_notation = self.CLASS_TO_PIECE.get(piece_class, 'empty')
                
                board_matrix[row, col] = piece_notation
                confidence_map[row, col] = confidence
                raw_predictions[row, col] = piece_class
        
        return ClassificationResult(
            board_matrix=board_matrix,
            confidence_map=confidence_map,
            raw_predictions=raw_predictions
        )
    
    def _classify_square(self, square_img: np.ndarray) -> Tuple[int, float]:
        """
        Classify a single square.
        
        Args:
            square_img: Single square image (square_size x square_size x 3)
            
        Returns:
            Tuple of (class_index, confidence)
        """
        # Count non-board colors in the square
        white_mask = cv2.inRange(square_img, self.white_lower, self.white_upper)
        black_mask = cv2.inRange(square_img, self.black_lower, self.black_upper)
        
        white_pixels = np.count_nonzero(white_mask)
        black_pixels = np.count_nonzero(black_mask)
        
        total_pixels = square_img.shape[0] * square_img.shape[1]
        
        # Threshold to determine if square has a piece
        occupancy_threshold = 0.15
        white_occupancy = white_pixels / total_pixels
        black_occupancy = black_pixels / total_pixels
        
        if white_occupancy > occupancy_threshold:
            confidence = white_occupancy
            # Classify piece type using shape analysis
            piece_type = self._classify_piece_type(square_img, white_pixels)
            return self.PIECE_CLASSES[piece_type], confidence
        elif black_occupancy > occupancy_threshold:
            confidence = black_occupancy
            piece_type = self._classify_piece_type(square_img, black_pixels)
            return self.PIECE_CLASSES[piece_type], confidence
        else:
            return self.PIECE_CLASSES['empty'], 0.8
    
    def _classify_piece_type(self, square_img: np.ndarray, piece_pixels: int) -> str:
        """
        Classify piece type (pawn, knight, etc.) based on shape.
        
        For MVP, this returns a random piece type. In phase 2, implement:
        - Centroid analysis
        - Contour shape matching
        - Size analysis
        
        Args:
            square_img: Square image
            piece_pixels: Number of piece pixels detected
            
        Returns:
            FEN piece notation (uppercase for white, lowercase for black)
        """
        # Detect if piece is white or black
        is_white = np.mean(square_img[:, :, 0]) > 128
        
        # For MVP: use simplified heuristics
        # In phase 2: implement proper shape classification
        density = piece_pixels / (square_img.shape[0] * square_img.shape[1])
        
        if is_white:
            # Rough heuristic: density indicates piece type
            if density > 0.4:
                return 'K'  # King/Queen (large pieces)
            elif density > 0.25:
                return 'R'  # Rook
            elif density > 0.20:
                return 'B'  # Bishop
            elif density > 0.15:
                return 'N'  # Knight
            else:
                return 'P'  # Pawn
        else:
            if density > 0.4:
                return 'k'
            elif density > 0.25:
                return 'r'
            elif density > 0.20:
                return 'b'
            elif density > 0.15:
                return 'n'
            else:
                return 'p'
    
    def load_model(self, model_path: str):
        """
        Load pretrained CNN model for improved classification.
        
        For phase 2 implementation.
        
        Args:
            model_path: Path to saved model
        """
        # TODO: Implement CNN model loading
        pass
    
    def train_model(self, training_data_path: str):
        """
        Train CNN model on labeled piece data.
        
        For phase 2 implementation.
        
        Args:
            training_data_path: Path to training dataset
        """
        # TODO: Implement CNN model training
        pass
