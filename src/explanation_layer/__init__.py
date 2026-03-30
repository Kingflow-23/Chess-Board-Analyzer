"""Explanation Layer - Generates human-readable position analysis."""
from dataclasses import dataclass
from typing import List, Dict
import chess

from evaluation_engine import PositionEvaluator, EvaluationResult


@dataclass
class AnalysisExplanation:
    """Complete analysis with explanations."""
    summary: str  # Overall summary
    advantage_str: str  # Advantage string (e.g., "+1.2")
    details: List[str]  # Detailed explanations
    feature_explanations: Dict[str, str]  # Per-feature explanations
    blunders: List[str]  # Any detected blunders
    highlights: List[str]  # Strong points to highlight


class GameAnalyzer:
    """Generates human-readable chess analysis."""
    
    def __init__(self):
        """Initialize analyzer."""
        self.evaluator = PositionEvaluator()
    
    def analyze(self, board: chess.Board) -> AnalysisExplanation:
        """
        Analyze a position and generate explanation.
        
        Args:
            board: Chess board position
        
        Returns:
            AnalysisExplanation with summary and details
        """
        # Evaluate position
        eval_result = self.evaluator.evaluate(board)
        
        if not eval_result.is_valid:
            return AnalysisExplanation(
                summary="Invalid position.",
                advantage_str="0.0",
                details=["The position is invalid."],
                feature_explanations={},
                blunders=[],
                highlights=[]
            )
        
        # Generate explanations
        summary = self._generate_summary(eval_result)
        advantage_str = self._format_advantage(eval_result.total_score)
        details = self._generate_details(eval_result)
        feature_explanations = self._generate_feature_explanations(eval_result)
        blunders = self._detect_blunders(board, eval_result)
        highlights = self._generate_highlights(board, eval_result)
        
        return AnalysisExplanation(
            summary=summary,
            advantage_str=advantage_str,
            details=details,
            feature_explanations=feature_explanations,
            blunders=blunders,
            highlights=highlights
        )
    
    def _generate_summary(self, eval_result: EvaluationResult) -> str:
        """Generate overall summary."""
        score = eval_result.total_score
        
        if abs(score) < 0.3:
            summary = "The position is roughly equal. Both sides have balanced advantages and disadvantages."
        elif abs(score) < 0.8:
            if score > 0:
                summary = f"White has a slight advantage ({score:+.1f}p). White's position is slightly preferable due to better piece coordination and structure."
            else:
                summary = f"Black has a slight advantage ({score:+.1f}p). Black's position is slightly preferable due to better piece coordination and structure."
        elif abs(score) < 1.5:
            if score > 0:
                summary = f"White is better ({score:+.1f}p). White has a notable advantage, likely from material or positional superiority."
            else:
                summary = f"Black is better ({score:+.1f}p). Black has a notable advantage, likely from material or positional superiority."
        else:
            if score > 0:
                summary = f"White has a significant advantage ({score:+.1f}p). White is much better and should be winning with good technique."
            else:
                summary = f"Black has a significant advantage ({score:+.1f}p). Black is much better and should be winning with good technique."
        
        return summary
    
    def _format_advantage(self, score: float) -> str:
        """Format advantage as +X.X or -X.X."""
        return f"{score:+.1f}"
    
    def _generate_details(self, eval_result: EvaluationResult) -> List[str]:
        """Generate detailed points."""
        details = []
        
        # Sort features by absolute score (most important first)
        sorted_features = sorted(
            eval_result.features.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        for feature_name, score in sorted_features:
            explanation = self.evaluator.get_feature_explanation(chess.Board())
            details.append(explanation.get(feature_name, ""))
        
        return [d for d in details if d]  # Remove empty strings
    
    def _generate_feature_explanations(self, eval_result: EvaluationResult) -> Dict[str, str]:
        """Generate explanations for each feature."""
        explanations = {}
        
        for feature_name, score in eval_result.features.items():
            if abs(score) < 0.05:
                explanations[feature_name] = "Balanced."
            else:
                advantage = "White" if score > 0 else "Black"
                magnitude = abs(score)
                
                if magnitude < 0.3:
                    assessment = "slightly better"
                elif magnitude < 0.8:
                    assessment = "moderately better"
                elif magnitude < 1.5:
                    assessment = "significantly better"
                else:
                    assessment = "much better"
                
                explanations[feature_name] = f"{advantage} is {assessment} ({score:+.2f}p)."
        
        return explanations
    
    def _detect_blunders(self, board: chess.Board, eval_result: EvaluationResult) -> List[str]:
        """Detect obvious blunders."""
        blunders = []
        
        # Check for exposed kings
        white_king = board.king(chess.WHITE)
        black_king = board.king(chess.BLACK)
        
        if white_king is not None:
            white_attackers = board.attackers(chess.BLACK, white_king)
            if len(white_attackers) > 2:
                blunders.append("White's king is under heavy attack!")
        
        if black_king is not None:
            black_attackers = board.attackers(chess.WHITE, black_king)
            if len(black_attackers) > 2:
                blunders.append("Black's king is under heavy attack!")
        
        return blunders
    
    def _generate_highlights(self, board: chess.Board, eval_result: EvaluationResult) -> List[str]:
        """Generate highlights of strong points."""
        highlights = []
        
        # Highlight material advantage
        if abs(eval_result.features.get("Material Balance", 0)) > 0.5:
            advantage = "White" if eval_result.features["Material Balance"] > 0 else "Black"
            highlights.append(f"{advantage} has a material advantage.")
        
        # Highlight mobility advantage
        if abs(eval_result.features.get("Mobility", 0)) > 0.3:
            advantage = "White" if eval_result.features["Mobility"] > 0 else "Black"
            highlights.append(f"{advantage}'s pieces are more active.")
        
        # Highlight king safety
        if abs(eval_result.features.get("King Safety", 0)) > 0.4:
            advantage = "White" if eval_result.features["King Safety"] > 0 else "Black"
            highlights.append(f"{advantage}'s king is safer.")
        
        # Highlight center control
        if abs(eval_result.features.get("Center Control", 0)) > 0.2:
            advantage = "White" if eval_result.features["Center Control"] > 0 else "Black"
            highlights.append(f"{advantage} controls the center.")
        
        return highlights
