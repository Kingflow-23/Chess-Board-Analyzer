"""Feature weights and configuration for evaluation engine."""


class EvaluationWeights:
    """Weights for combining evaluation features."""
    
    # Default weights (can be tuned)
    WEIGHTS = {
        "Material Balance": 1.0,      # Highest importance
        "Mobility": 0.3,              # Legal moves advantage
        "King Safety": 0.4,           # Safety is important
        "Pawn Structure": 0.2,        # Structural features
        "Center Control": 0.2,        # Central control
        "Piece-Square Tables": 0.15   # Positional bonuses
    }
    
    # Normalize scores to centipawns
    NORMALIZATION_FACTOR = 100.0
    
    @classmethod
    def get_weight(cls, feature_name: str) -> float:
        """Get weight for a feature."""
        return cls.WEIGHTS.get(feature_name, 1.0)
    
    @classmethod
    def normalize_score(cls, raw_score: float) -> float:
        """
        Normalize raw evaluation score to pawns.
        
        100 centipawns = 1 pawn
        
        Args:
            raw_score: Raw score value
        
        Returns:
            Score in pawns
        """
        return raw_score / cls.NORMALIZATION_FACTOR
    
    @classmethod
    def denormalize_score(cls, score_in_pawns: float) -> float:
        """Convert pawns to centipawns."""
        return score_in_pawns * cls.NORMALIZATION_FACTOR
