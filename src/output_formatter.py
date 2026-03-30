"""
JSON Output Formatter
Structures analysis results into standardized JSON format
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import chess


class JSONOutputFormatter:
    """Format chess analysis results as structured JSON"""
    
    def __init__(self, include_metadata: bool = True):
        """
        Initialize JSON formatter
        
        Args:
            include_metadata: Whether to include timestamp and version info
        """
        self.include_metadata = include_metadata
        self.model_version = "2.0"
    
    def format_position(self, fen: str, board_matrix: List[List[str]], 
                       image_file: Optional[str] = None) -> Dict:
        """
        Format chess position data
        
        Args:
            fen: FEN string representation
            board_matrix: 8x8 board as list of lists with piece symbols
            image_file: Optional source image filename
            
        Returns:
            Dictionary with position data
        """
        try:
            board = chess.Board(fen)
            is_valid = True
            error_msg = None
        except:
            board = None
            is_valid = False
            error_msg = "Invalid FEN notation"
        
        return {
            "fen": fen,
            "board_matrix": self._serialize_board(board_matrix),
            "is_valid": is_valid,
            "whose_turn": "white" if board and board.turn else "black" if board else None,
            "in_check": board.is_check() if board else None,
            "is_checkmate": board.is_checkmate() if board else None,
            "is_stalemate": board.is_stalemate() if board else None,
            "halfmove_clock": board.halfmove_clock if board else None,
            "fullmove_number": board.fullmove_number if board else None,
            "legal_move_count": len(list(board.legal_moves)) if board else None,
            "image_source": image_file,
            "error": error_msg
        }
    
    def format_evaluation(self, evaluation_result: Dict) -> Dict:
        """
        Format evaluation engine results
        
        Args:
            evaluation_result: Dictionary from PositionEvaluator
            
        Returns:
            Dictionary with formatted evaluation
        """
        return {
            "total_score": round(evaluation_result.get("total_score", 0), 2),
            "best_side": evaluation_result.get("best_side", "unknown"),
            "features": {
                "material_balance": round(evaluation_result.get("material_score", 0), 2),
                "mobility": round(evaluation_result.get("mobility_score", 0), 2),
                "king_safety": round(evaluation_result.get("king_safety_score", 0), 2),
                "pawn_structure": round(evaluation_result.get("pawn_structure_score", 0), 2),
                "center_control": round(evaluation_result.get("center_control_score", 0), 2),
                "piece_square_tables": round(evaluation_result.get("pst_score", 0), 2)
            },
            "centipawn_score": round(evaluation_result.get("total_score", 0) * 100, 0)
        }
    
    def format_bar(self, bar_data: Dict) -> Dict:
        """
        Format evaluation bar visualization data
        
        Args:
            bar_data: Dictionary from EvaluationBarGenerator
            
        Returns:
            Dictionary with bar data
        """
        return {
            "white_percentage": bar_data.get("white_percentage", 50),
            "black_percentage": bar_data.get("black_percentage", 50),
            "centipawn_score": bar_data.get("centipawn_score", 0),
            "evaluation_type": bar_data.get("evaluation_type", "equal"),
            "visual_bar": bar_data.get("visual_bar", ""),
            "numeric_display": bar_data.get("numeric_display", "0.0"),
            "explanation": bar_data.get("explanation", "")
        }
    
    def format_analysis(self, analysis: Dict) -> Dict:
        """
        Format human-readable analysis
        
        Args:
            analysis: Dictionary from GameAnalyzer
            
        Returns:
            Dictionary with analysis
        """
        return {
            "summary": analysis.get("summary", ""),
            "key_features": analysis.get("key_features", []),
            "strengths": analysis.get("strengths", []),
            "weaknesses": analysis.get("weaknesses", []),
            "key_highlights": analysis.get("key_highlights", []),
            "recommendations": analysis.get("recommendations", [])
        }
    
    def combine_all(self, position_data: Dict, evaluation_data: Dict, 
                   bar_data: Dict, analysis_data: Dict) -> Dict:
        """
        Combine all analysis components into single JSON output
        
        Args:
            position_data: Formatted position data
            evaluation_data: Formatted evaluation data
            bar_data: Formatted bar data
            analysis_data: Formatted analysis data
            
        Returns:
            Complete JSON output dictionary
        """
        output = {}
        
        if self.include_metadata:
            output["metadata"] = {
                "timestamp": datetime.now().isoformat(),
                "model_version": self.model_version,
                "formatter_version": "2.0"
            }
        
        output.update({
            "position": position_data,
            "evaluation": evaluation_data,
            "bar": bar_data,
            "analysis": analysis_data,
            "status": "success"
        })
        
        return output
    
    def create_error_response(self, error_message: str, error_type: str = "unknown") -> Dict:
        """
        Create error response in standard format
        
        Args:
            error_message: Human-readable error message
            error_type: Type of error (validation, processing, etc.)
            
        Returns:
            Error response dictionary
        """
        return {
            "status": "error",
            "error": {
                "type": error_type,
                "message": error_message,
                "timestamp": datetime.now().isoformat()
            },
            "position": None,
            "evaluation": None,
            "bar": None,
            "analysis": None
        }
    
    def to_json_string(self, data: Dict, pretty: bool = True, indent: int = 2) -> str:
        """
        Convert data to JSON string
        
        Args:
            data: Dictionary to convert
            pretty: Whether to format prettily
            indent: Indentation level for pretty printing
            
        Returns:
            JSON string
        """
        if pretty:
            return json.dumps(data, indent=indent, default=str)
        else:
            return json.dumps(data, default=str)
    
    def save_to_file(self, data: Dict, file_path: str, pretty: bool = True):
        """
        Save analysis result to JSON file
        
        Args:
            data: Dictionary to save
            file_path: Path to save file
            pretty: Whether to format prettily
        """
        json_str = self.to_json_string(data, pretty=pretty)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(json_str)
    
    def load_from_file(self, file_path: str) -> Dict:
        """
        Load analysis result from JSON file
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Dictionary from JSON file
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _serialize_board(self, board_matrix: List[List[str]]) -> List[List[str]]:
        """
        Serialize board matrix for JSON output
        
        Args:
            board_matrix: 8x8 board matrix
            
        Returns:
            Serializable board representation
        """
        if not board_matrix:
            return [['' for _ in range(8)] for _ in range(8)]
        
        return [
            [str(piece) if piece else '' for piece in row]
            for row in board_matrix
        ]


class ChessAnalysisJSONBuilder:
    """Builder pattern for constructing complex JSON responses"""
    
    def __init__(self):
        """Initialize builder"""
        self.formatter = JSONOutputFormatter()
        self._position = None
        self._evaluation = None
        self._bar = None
        self._analysis = None
        self._image_file = None
    
    def with_position(self, fen: str, board_matrix: List[List[str]], 
                     image_file: Optional[str] = None) -> 'ChessAnalysisJSONBuilder':
        """Set position data"""
        self._position = self.formatter.format_position(fen, board_matrix, image_file)
        self._image_file = image_file
        return self
    
    def with_evaluation(self, evaluation_result: Dict) -> 'ChessAnalysisJSONBuilder':
        """Set evaluation data"""
        self._evaluation = self.formatter.format_evaluation(evaluation_result)
        return self
    
    def with_bar(self, bar_data: Dict) -> 'ChessAnalysisJSONBuilder':
        """Set bar visualization data"""
        self._bar = self.formatter.format_bar(bar_data)
        return self
    
    def with_analysis(self, analysis_data: Dict) -> 'ChessAnalysisJSONBuilder':
        """Set analysis data"""
        self._analysis = self.formatter.format_analysis(analysis_data)
        return self
    
    def build(self) -> Dict:
        """Build final JSON output"""
        return self.formatter.combine_all(
            self._position or {},
            self._evaluation or {},
            self._bar or {},
            self._analysis or {}
        )
    
    def build_json_string(self, pretty: bool = True) -> str:
        """Build and convert to JSON string"""
        return self.formatter.to_json_string(self.build(), pretty=pretty)
    
    def save(self, file_path: str, pretty: bool = True):
        """Build and save to file"""
        self.formatter.save_to_file(self.build(), file_path, pretty=pretty)


if __name__ == "__main__":
    # Test the JSON formatter
    formatter = JSONOutputFormatter()
    
    # Create sample data
    sample_position = formatter.format_position(
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
        [['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
         ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
         ['', '', '', '', '', '', '', ''],
         ['', '', '', '', '', '', '', ''],
         ['', '', '', 'P', '', '', '', ''],
         ['', '', '', '', '', '', '', ''],
         ['P', 'P', 'P', '', 'P', 'P', 'P', 'P'],
         ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']],
        "game.png"
    )
    
    sample_eval = {
        "total_score": 0.5,
        "best_side": "white",
        "material_score": 0,
        "mobility_score": 0.5,
        "king_safety_score": 0,
        "pawn_structure_score": 0,
        "center_control_score": 0,
        "pst_score": 0
    }
    
    sample_bar = {
        "white_percentage": 55,
        "black_percentage": 45,
        "centipawn_score": 50,
        "evaluation_type": "white_slightly_better",
        "visual_bar": "█████████░░░░░░░░░░",
        "numeric_display": "+0.5",
        "explanation": "White is slightly better"
    }
    
    sample_analysis = {
        "summary": "White has a small initiative in this position.",
        "key_features": ["White's slight mobility advantage"],
        "strengths": ["Active pieces"],
        "weaknesses": ["Black is solid"],
        "key_highlights": ["White controls the center"],
        "recommendations": ["Continue with natural development"]
    }
    
    # Build complete output
    builder = ChessAnalysisJSONBuilder()
    builder.with_position("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1", [], "game.png")
    builder.with_evaluation(sample_eval)
    builder.with_bar(sample_bar)
    builder.with_analysis(sample_analysis)
    
    print("Complete JSON Output:")
    print(builder.build_json_string(pretty=True))
