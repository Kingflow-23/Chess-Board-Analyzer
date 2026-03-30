"""
Enhanced Pipeline - Full Integration with Image Upload, CNN, JSON Output, and Evaluation Bars
Orchestrates all components for complete chess position analysis
"""

import numpy as np
import chess
import os
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

from cv_module import BoardDetector
from cv_module.cnn_classifier import PieceClassifier as CNNPieceClassifier
from position_module import FENConverter
from evaluation_engine import PositionEvaluator
from explanation_layer import GameAnalyzer
from upload_handler import ImageUploadHandler
from output_formatter import JSONOutputFormatter, ChessAnalysisJSONBuilder
from visualization import EvaluationBarGenerator


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EnhancedPipelineOutput:
    """Complete output from the enhanced pipeline with JSON and visualization."""
    # Input metadata
    input_image_path: Optional[str]
    upload_timestamp: str
    
    # CV Output
    board_detected: bool
    board_confidence: float
    board_image: Optional[np.ndarray]
    board_matrix: Optional[list]
    piece_confidences: Optional[np.ndarray]
    
    # Position Output
    fen: Optional[str]
    fen_valid: bool
    
    # Evaluation Output
    evaluation_scores: Optional[Dict[str, float]]
    total_score: float
    best_side: str
    
    # Visualization Output
    eval_bar: Optional[Dict]
    
    # Analysis Output
    analysis_summary: str
    strengths: list
    weaknesses: list
    key_highlights: list
    
    # JSON Output
    json_output: Dict
    
    # Metadata
    success: bool
    processing_time: float
    error_message: Optional[str] = None


class EnhancedChessBoardAnalyzerPipeline:
    """
    Enhanced pipeline for chess board analysis with image upload, CNN classification,
    and JSON + visualization output.
    
    Complete Flow:
    Image Upload → Validation → Board Detection → CNN Piece Classification → 
    FEN Conversion → Evaluation → Evaluation Bar → Analysis → JSON Output
    """
    
    def __init__(self, 
                 board_size: int = 512,
                 cnn_model_path: Optional[str] = None,
                 upload_dir: Optional[str] = None):
        """
        Initialize enhanced pipeline.
        
        Args:
            board_size: Normalized board size (512x512 recommended)
            cnn_model_path: Path to trained CNN model (optional)
            upload_dir: Directory for uploaded images
        """
        logger.info("Initializing Enhanced Chess Board Analyzer Pipeline...")
        
        self.board_size = board_size
        self.upload_handler = ImageUploadHandler(upload_dir=upload_dir)
        self.board_detector = BoardDetector(board_size=board_size)
        self.piece_classifier = CNNPieceClassifier(model_path=cnn_model_path)
        self.fen_converter = FENConverter()
        self.evaluator = PositionEvaluator()
        self.analyzer = GameAnalyzer()
        self.bar_generator = EvaluationBarGenerator()
        self.json_formatter = JSONOutputFormatter()
        
        logger.info("Pipeline initialized successfully")
    
    def analyze_uploaded_image(self, 
                              image_path: str,
                              white_to_move: bool = True,
                              save_json: Optional[str] = None) -> EnhancedPipelineOutput:
        """
        Complete analysis pipeline for uploaded image.
        
        Args:
            image_path: Path to uploaded image file
            white_to_move: Assume white to move
            save_json: Optional path to save JSON output
            
        Returns:
            EnhancedPipelineOutput with complete analysis
        """
        import time
        start_time = time.time()
        
        try:
            # ========================================
            # 1. IMAGE VALIDATION AND UPLOAD
            # ========================================
            logger.info(f"Validating image: {image_path}")
            is_valid, error_msg = self.upload_handler.validate_image(image_path)
            
            if not is_valid:
                logger.error(f"Image validation failed: {error_msg}")
                return self._create_error_output(image_path, error_msg, start_time)
            
            # Get image metadata
            metadata = self.upload_handler.get_image_metadata(image_path)
            logger.info(f"Image metadata: {metadata}")
            
            # Preprocess image
            image = self.upload_handler.preprocess_for_analysis(image_path)
            
            # ========================================
            # 2. COMPUTER VISION: BOARD DETECTION
            # ========================================
            logger.info("Detecting chessboard...")
            detection_result = self.board_detector.detect(image)
            
            if not detection_result.success:
                logger.error("Board detection failed")
                return self._create_error_output(
                    image_path, 
                    "Could not detect chessboard in image",
                    start_time
                )
            
            logger.info(f"Board detected with confidence: {detection_result.confidence_score:.2%}")
            
            # Segment board into squares
            board_image = detection_result.board_image
            squares = self.board_detector.segment_squares(board_image)
            
            # ========================================
            # 3. COMPUTER VISION: CNN PIECE CLASSIFICATION
            # ========================================
            logger.info("Classifying pieces using CNN...")
            classification_result = self.piece_classifier.classify_squares(squares)
            
            board_matrix = classification_result["board_matrix"]
            piece_confidences = classification_result["confidences"]
            
            logger.info(f"Piece classification complete. "
                       f"Mean confidence: {np.mean(piece_confidences):.2%}")
            
            # ========================================
            # 4. POSITION RECONSTRUCTION: FEN CONVERSION
            # ========================================
            logger.info("Converting board matrix to FEN...")
            position_result = self.fen_converter.board_matrix_to_fen(
                board_matrix,
                white_to_move=white_to_move,
                castling_rights='KQkq',
                en_passant_square=None
            )
            
            fen = position_result.fen
            fen_valid = position_result.is_valid
            
            if not fen_valid:
                logger.error("FEN conversion invalid")
                return self._create_error_output(
                    image_path,
                    f"Invalid FEN position: {fen}",
                    start_time
                )
            
            logger.info(f"FEN: {fen}")
            
            # ========================================
            # 5. POSITION EVALUATION
            # ========================================
            logger.info("Evaluating position...")
            board = chess.Board(fen)
            evaluation = self.evaluator.evaluate(board)
            
            eval_dict = asdict(evaluation) if hasattr(evaluation, '__dict__') else evaluation
            total_score = float(eval_dict.get('total_score', 0))
            best_side = eval_dict.get('best_side', 'equal')
            
            logger.info(f"Evaluation: {total_score:+.2f}p ({best_side})")
            
            # ========================================
            # 6. EVALUATION BAR GENERATION
            # ========================================
            logger.info("Generating evaluation bar...")
            bar_data = self.bar_generator.create_full_bar_data(
                white_centipawns=total_score * 100,
                black_centipawns=0,
                material_score=eval_dict.get('material_score', 0) * 100,
                positional_score=total_score * 100 - eval_dict.get('material_score', 0) * 100
            )
            
            logger.info(f"Bar: {bar_data['numeric_display']} "
                       f"({bar_data['white_percentage']:.1f}% vs {bar_data['black_percentage']:.1f}%)")
            
            # ========================================
            # 7. ANALYSIS AND EXPLANATION
            # ========================================
            logger.info("Analyzing position...")
            analysis = self.analyzer.analyze(board)
            
            analysis_dict = asdict(analysis) if hasattr(analysis, '__dict__') else analysis
            
            logger.info(f"Analysis: {analysis_dict.get('summary', '')[:100]}...")
            
            # ========================================
            # 8. JSON OUTPUT FORMATTING
            # ========================================
            logger.info("Formatting JSON output...")
            
            json_builder = ChessAnalysisJSONBuilder()
            json_builder.with_position(fen, board_matrix, os.path.basename(image_path))
            json_builder.with_evaluation(eval_dict)
            json_builder.with_bar(bar_data)
            json_builder.with_analysis(analysis_dict)
            
            json_output = json_builder.build()
            
            # Save JSON if requested
            if save_json:
                json_builder.save(save_json, pretty=True)
                logger.info(f"JSON saved to: {save_json}")
            
            # ========================================
            # RETURN COMPLETE OUTPUT
            # ========================================
            processing_time = time.time() - start_time
            
            output = EnhancedPipelineOutput(
                input_image_path=image_path,
                upload_timestamp=datetime.now().isoformat(),
                board_detected=True,
                board_confidence=detection_result.confidence_score,
                board_image=board_image,
                board_matrix=board_matrix,
                piece_confidences=piece_confidences,
                fen=fen,
                fen_valid=fen_valid,
                evaluation_scores=eval_dict,
                total_score=total_score,
                best_side=best_side,
                eval_bar=bar_data,
                analysis_summary=analysis_dict.get('summary', ''),
                strengths=analysis_dict.get('strengths', []),
                weaknesses=analysis_dict.get('weaknesses', []),
                key_highlights=analysis_dict.get('key_highlights', []),
                json_output=json_output,
                success=True,
                processing_time=processing_time
            )
            
            logger.info(f"Analysis complete in {processing_time:.2f}s")
            return output
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}", exc_info=True)
            return self._create_error_output(image_path, str(e), start_time)
    
    def _create_error_output(self, image_path: str, error_msg: str, start_time: float) -> EnhancedPipelineOutput:
        """Create error response output"""
        processing_time = __import__('time').time() - start_time
        
        json_error = self.json_formatter.create_error_response(
            error_msg, 
            error_type="pipeline_error"
        )
        
        return EnhancedPipelineOutput(
            input_image_path=image_path,
            upload_timestamp=datetime.now().isoformat(),
            board_detected=False,
            board_confidence=0.0,
            board_image=None,
            board_matrix=None,
            piece_confidences=None,
            fen=None,
            fen_valid=False,
            evaluation_scores=None,
            total_score=0.0,
            best_side="unknown",
            eval_bar=None,
            analysis_summary="Error during analysis",
            strengths=[],
            weaknesses=[],
            key_highlights=[],
            json_output=json_error,
            success=False,
            processing_time=processing_time,
            error_message=error_msg
        )
    
    def print_detailed_analysis(self, output: EnhancedPipelineOutput):
        """Print detailed analysis in human-readable format"""
        
        if not output.success:
            print("\n" + "="*70)
            print("❌ ANALYSIS FAILED")
            print("="*70)
            print(f"Error: {output.error_message}")
            return
        
        print("\n" + "="*70)
        print("║" + " "*68 + "║")
        print("║" + "CHESS POSITION ANALYSIS REPORT".center(68) + "║")
        print("║" + " "*68 + "║")
        print("="*70)
        
        # Metadata
        print(f"\n📋 METADATA")
        print(f"  • Upload: {output.upload_timestamp}")
        print(f"  • Processing Time: {output.processing_time:.2f}s")
        print(f"  • Image: {output.input_image_path}")
        
        # Position Detection
        print(f"\n🎯 POSITION DETECTION")
        print(f"  • Board Detected: {'✓' if output.board_detected else '✗'}")
        print(f"  • Board Confidence: {output.board_confidence:.1%}")
        print(f"  • FEN Valid: {'✓' if output.fen_valid else '✗'}")
        print(f"  • FEN: {output.fen}")
        
        # Evaluation
        print(f"\n⚡ EVALUATION")
        print(f"  • Total Score: {output.total_score:+.2f}p ({output.best_side})")
        print(f"  • Material: {output.evaluation_scores.get('material_score', 0):+.2f}p")
        print(f"  • Mobility: {output.evaluation_scores.get('mobility_score', 0):+.2f}p")
        print(f"  • King Safety: {output.evaluation_scores.get('king_safety_score', 0):+.2f}p")
        
        # Evaluation Bar
        if output.eval_bar:
            print(f"\n📊 EVALUATION BAR")
            print(f"  {output.eval_bar['visual_bar']}")
            print(f"  {output.eval_bar['numeric_display']}")
            print(f"  • White: {output.eval_bar['white_percentage']:.1f}%")
            print(f"  • Black: {output.eval_bar['black_percentage']:.1f}%")
            print(f"  • Type: {output.eval_bar['evaluation_type']}")
            print(f"  • {output.eval_bar['explanation']}")
        
        # Analysis
        print(f"\n📝 ANALYSIS")
        print(f"  • Summary: {output.analysis_summary}")
        if output.strengths:
            print(f"  • Strengths: {', '.join(output.strengths)}")
        if output.weaknesses:
            print(f"  • Weaknesses: {', '.join(output.weaknesses)}")
        if output.key_highlights:
            print(f"  • Key Points: {', '.join(output.key_highlights)}")
        
        print("\n" + "="*70 + "\n")
    
    def cleanup(self):
        """Clean up temporary files"""
        logger.info("Cleaning up temporary files...")
        self.upload_handler.cleanup_old_uploads()


if __name__ == "__main__":
    print("Enhanced Chess Board Analyzer Pipeline Module")
    print(f"Supports CNN classification with JSON and bar visualization")
