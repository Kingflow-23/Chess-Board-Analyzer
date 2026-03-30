"""Main Pipeline - Integrates all modules (CV → FEN → Evaluation → Explanation)."""
import numpy as np
import chess
from typing import Optional, Dict, Any
from dataclasses import dataclass

from .cv_module import BoardDetector, PieceClassifier
from .position_module import FENConverter
from .evaluation_engine import PositionEvaluator, EvaluationResult
from .explanation_layer import GameAnalyzer


@dataclass
class PipelineOutput:
    """Complete output from the full pipeline."""
    # Input
    input_image: Optional[np.ndarray]
    
    # CV Output
    board_detected: bool
    board_image: Optional[np.ndarray]
    board_matrix: Optional[np.ndarray]
    piece_confidence_map: Optional[np.ndarray]
    
    # Position Output
    fen: Optional[str]
    fen_valid: bool
    
    # Evaluation Output
    evaluation: Optional[EvaluationResult]
    
    # Analysis Output
    summary: str
    advantage_str: str
    details: list
    highlights: list
    
    # Metadata
    success: bool
    error_message: Optional[str] = None


class ChessBoardAnalyzerPipeline:
    """
    Complete pipeline for chess board analysis.
    
    Flow: Image → Board Detection → Piece Classification → FEN Conversion → Evaluation → Analysis
    """
    
    def __init__(self, board_size: int = 512):
        """
        Initialize pipeline.
        
        Args:
            board_size: Normalized board size (512x512 is recommended)
        """
        self.board_detector = BoardDetector(board_size=board_size)
        self.piece_classifier = PieceClassifier()
        self.fen_converter = FENConverter()
        self.evaluator = PositionEvaluator()
        self.analyzer = GameAnalyzer()
    
    def analyze_image(
        self,
        image: np.ndarray,
        white_to_move: bool = True
    ) -> PipelineOutput:
        """
        Analyze a chess board image from start to finish.
        
        Args:
            image: Input image (BGR or RGB)
            white_to_move: Assume white to move (can be refined later)
        
        Returns:
            PipelineOutput with complete analysis
        """
        try:
            # ========================================
            # 1. COMPUTER VISION: Detect Board
            # ========================================
            detection_result = self.board_detector.detect(image)
            
            if not detection_result.success:
                return PipelineOutput(
                    input_image=image,
                    board_detected=False,
                    board_image=None,
                    board_matrix=None,
                    piece_confidence_map=None,
                    fen=None,
                    fen_valid=False,
                    evaluation=None,
                    summary="Could not detect chessboard in image.",
                    advantage_str="0.0",
                    details=[],
                    highlights=[],
                    success=False,
                    error_message="Board detection failed"
                )
            
            # Segment board into squares
            board_image = detection_result.board_image
            squares = self.board_detector.segment_squares(board_image)
            
            # ========================================
            # 2. COMPUTER VISION: Classify Pieces
            # ========================================
            classification_result = self.piece_classifier.classify(squares)
            board_matrix = classification_result.board_matrix
            confidence_map = classification_result.confidence_map
            
            # ========================================
            # 3. POSITION RECONSTRUCTION: FEN
            # ========================================
            position_result = self.fen_converter.board_matrix_to_fen(
                board_matrix,
                white_to_move=white_to_move,
                castling_rights='KQkq',
                en_passant_square=None
            )
            
            fen = position_result.fen
            fen_valid = position_result.is_valid
            
            # ========================================
            # 4. EVALUATION ENGINE
            # ========================================
            if fen_valid:
                board = chess.Board(fen)
                evaluation = self.evaluator.evaluate(board)
            else:
                evaluation = None
            
            # ========================================
            # 5. EXPLANATION LAYER
            # ========================================
            if evaluation and fen_valid:
                board = chess.Board(fen)
                analysis = self.analyzer.analyze(board)
                summary = analysis.summary
                advantage_str = analysis.advantage_str
                details = analysis.details
                highlights = analysis.highlights
            else:
                summary = "Could not evaluate position."
                advantage_str = "0.0"
                details = []
                highlights = []
            
            # ========================================
            # Return Complete Output
            # ========================================
            return PipelineOutput(
                input_image=image,
                board_detected=True,
                board_image=board_image,
                board_matrix=board_matrix,
                piece_confidence_map=confidence_map,
                fen=fen,
                fen_valid=fen_valid,
                evaluation=evaluation,
                summary=summary,
                advantage_str=advantage_str,
                details=details,
                highlights=highlights,
                success=fen_valid,
                error_message=None
            )
        
        except Exception as e:
            return PipelineOutput(
                input_image=image,
                board_detected=False,
                board_image=None,
                board_matrix=None,
                piece_confidence_map=None,
                fen=None,
                fen_valid=False,
                evaluation=None,
                summary="An error occurred during analysis.",
                advantage_str="0.0",
                details=[],
                highlights=[],
                success=False,
                error_message=str(e)
            )
    
    def print_analysis(self, output: PipelineOutput):
        """
        Print analysis in a readable format.
        
        Args:
            output: PipelineOutput from analyze_image
        """
        print("\n" + "="*60)
        print("CHESS POSITION ANALYSIS")
        print("="*60)
        
        if not output.success:
            print(f"❌ Analysis failed: {output.error_message}")
            print(f"   {output.summary}")
            return
        
        print(f"\n✓ Board detected and analyzed successfully")
        print(f"\nFEN: {output.fen}")
        
        if output.evaluation:
            print(f"\nEVALUATION:")
            print(f"  Advantage: {output.advantage_str}")
            print(f"  Assessment: {output.evaluation.best_side}")
            
            print(f"\nFEATURE BREAKDOWN:")
            for feature_name, score in output.evaluation.features.items():
                indicator = "+" if score > 0 else ""
                print(f"  • {feature_name}: {indicator}{score:.2f}p")
        
        print(f"\nSUMMARY:")
        print(f"  {output.summary}")
        
        if output.highlights:
            print(f"\nHIGHLIGHTS:")
            for highlight in output.highlights:
                print(f"  • {highlight}")
        
        if output.details:
            print(f"\nDETAILS:")
            for i, detail in enumerate(output.details, 1):
                print(f"  {i}. {detail}")
        
        print("\n" + "="*60)
