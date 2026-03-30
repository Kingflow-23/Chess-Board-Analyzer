"""Core Position Evaluator - Combines all features into single score."""
import chess
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from .features import (
    FeatureEvaluator,
    MaterialBalance,
    Mobility,
    KingSafety,
    PawnStructure,
    CenterControl,
    PieceSquareTables
)
from .weights import EvaluationWeights


@dataclass
class EvaluationResult:
    """Result of position evaluation."""
    total_score: float  # Total score in pawns (positive = white advantage)
    total_centipawns: float  # Total score in centipawns
    features: Dict[str, float]  # Individual feature scores in pawns
    features_centipawns: Dict[str, float]  # Individual feature scores in centipawns
    is_valid: bool  # Whether evaluation succeeded
    best_side: str = "White"  # Which side is better


class PositionEvaluator:
    """
    Modular chess position evaluator.
    
    Evaluates a position by combining multiple independent features.
    Each feature is explainable and can be tested independently.
    """
    
    def __init__(self):
        """Initialize evaluator with all features."""
        self.features: List[FeatureEvaluator] = [
            MaterialBalance(),
            Mobility(),
            KingSafety(),
            PawnStructure(),
            CenterControl(),
            PieceSquareTables()
        ]
    
    def evaluate(self, board: chess.Board) -> EvaluationResult:
        """
        Evaluate a chess position.
        
        Args:
            board: Chess board position
        
        Returns:
            EvaluationResult with total score and feature breakdown
        """
        # Check basic validity
        if not board.is_valid():
            return EvaluationResult(
                total_score=0.0,
                total_centipawns=0,
                features={},
                features_centipawns={},
                is_valid=False
            )
        
        # Evaluate each feature
        feature_scores_centipawns = {}
        total_weighted_score = 0.0
        
        for feature in self.features:
            try:
                raw_score = feature.evaluate(board)
                weight = EvaluationWeights.get_weight(feature.feature_name)
                weighted_score = raw_score * weight
                
                feature_scores_centipawns[feature.feature_name] = raw_score
                total_weighted_score += weighted_score
                
            except Exception as e:
                print(f"Error evaluating {feature.feature_name}: {e}")
                feature_scores_centipawns[feature.feature_name] = 0
        
        # Normalize to pawns
        total_score_in_pawns = EvaluationWeights.normalize_score(total_weighted_score)
        
        # Convert all features to pawns
        feature_scores_pawns = {
            name: EvaluationWeights.normalize_score(score)
            for name, score in feature_scores_centipawns.items()
        }
        
        # Determine best side
        if total_score_in_pawns > 0:
            best_side = "White"
        elif total_score_in_pawns < 0:
            best_side = "Black"
        else:
            best_side = "Equal"
        
        return EvaluationResult(
            total_score=total_score_in_pawns,
            total_centipawns=total_weighted_score,
            features=feature_scores_pawns,
            features_centipawns=feature_scores_centipawns,
            is_valid=True,
            best_side=best_side
        )
    
    def get_feature_explanation(self, board: chess.Board) -> Dict[str, str]:
        """
        Get human-readable explanations for each feature.
        
        Args:
            board: Chess board position
        
        Returns:
            Dictionary mapping feature names to explanations
        """
        explanations = {}
        
        eval_result = self.evaluate(board)
        
        for feature_name, score in eval_result.features.items():
            explanations[feature_name] = self._explain_feature(
                feature_name, score, board
            )
        
        return explanations
    
    def _explain_feature(self, feature_name: str, score: float, board: chess.Board) -> str:
        """
        Generate explanation for a feature score.
        
        Args:
            feature_name: Name of feature
            score: Score in pawns
            board: Chess board
        
        Returns:
            Human-readable explanation
        """
        if abs(score) < 0.05:
            neutral = "Material is equal."
            explanations = {
                "Material Balance": "Material is roughly equal.",
                "Mobility": "Both sides have similar mobility.",
                "King Safety": "Both kings are equally safe.",
                "Pawn Structure": "Pawn structures are similar.",
                "Center Control": "Center control is balanced.",
                "Piece-Square Tables": "Pieces are similarly placed."
            }
            return explanations.get(feature_name, "No significant advantage.")
        
        advantage = "White" if score > 0 else "Black"
        magnitude = abs(score)
        
        if magnitude < 0.3:
            assessment = "slight"
        elif magnitude < 0.8:
            assessment = "moderate"
        elif magnitude < 1.5:
            assessment = "significant"
        else:
            assessment = "decisive"
        
        templates = {
            "Material Balance": f"{advantage} has a {assessment} material advantage ({score:+.1f}p).",
            "Mobility": f"{advantage}'s pieces are {assessment}ly more active ({score:+.1f}p).",
            "King Safety": f"{advantage}'s king is {assessment}ly safer ({score:+.1f}p).",
            "Pawn Structure": f"{advantage} has a {assessment}ly better pawn structure ({score:+.1f}p).",
            "Center Control": f"{advantage} controls the center {assessment}ly better ({score:+.1f}p).",
            "Piece-Square Tables": f"{advantage}'s pieces are {assessment}ly better placed ({score:+.1f}p)."
        }
        
        return templates.get(feature_name, f"{advantage} has an advantage in {feature_name.lower()}.")
