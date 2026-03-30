"""
Evaluation Bar Generator
Creates chess.com-style evaluation visualization data
"""

from typing import Dict, Tuple
import math


class EvaluationBarGenerator:
    """Generate evaluation bars similar to chess.com"""
    
    def __init__(self):
        """Initialize evaluation bar generator"""
        # Sigmoid curve parameters for smooth score mapping
        self.sigmoid_steepness = 0.015  # Controls how quickly bar changes
        self.midpoint = 0  # 0 centipawns = equal position
    
    def generate_bar(self, white_centipawns: float, black_centipawns: float) -> Dict:
        """
        Generate evaluation bar data from centipawn scores
        
        Args:
            white_centipawns: White's evaluation in centipawns
            black_centipawns: Black's evaluation in centipawns
            
        Returns:
            Dictionary with bar visualization data
        """
        # If both provided, use white - black
        if white_centipawns != 0 and black_centipawns != 0:
            net_score = white_centipawns - black_centipawns
        else:
            net_score = white_centipawns if white_centipawns != 0 else -black_centipawns
        
        white_percentage = self._score_to_percentage(net_score)
        black_percentage = 100 - white_percentage
        
        evaluation_type = self._get_evaluation_type(net_score)
        
        return {
            "white_percentage": round(white_percentage, 1),
            "black_percentage": round(black_percentage, 1),
            "centipawn_score": round(net_score, 0),
            "evaluation_type": evaluation_type,
            "raw_net_score": float(net_score),
            "sigmoid_curve_data": self._get_sigmoid_data(net_score)
        }
    
    def _score_to_percentage(self, centipawns: float) -> float:
        """
        Convert centipawn score to percentage using sigmoid function
        
        This creates a smooth S-curve where:
        - -500cp = ~1% white
        - 0cp = 50% white (equal)
        - +500cp = ~99% white
        
        Args:
            centipawns: Score in centipawns
            
        Returns:
            Percentage (0-100) for white
        """
        # Sigmoid function: 1 / (1 + e^(-steepness * x))
        exponent = -self.sigmoid_steepness * centipawns
        
        # Clamp exponent to prevent overflow
        exponent = max(-100, min(100, exponent))
        
        sigmoid_value = 1 / (1 + math.exp(exponent))
        percentage = sigmoid_value * 100
        
        # Ensure within bounds
        return max(0.1, min(99.9, percentage))
    
    def _get_evaluation_type(self, centipawns: float) -> str:
        """
        Classify position evaluation into categories
        
        Args:
            centipawns: Score in centipawns
            
        Returns:
            String describing evaluation
        """
        abs_score = abs(centipawns)
        sign = "white" if centipawns >= 0 else "black"
        
        if abs_score < 50:
            return "drawn"
        elif abs_score < 150:
            return f"{sign}_slightly_better"
        elif abs_score < 300:
            return f"{sign}_better"
        elif abs_score < 500:
            return f"{sign}_is_winning"
        elif abs_score < 1000:
            return f"{sign}_is_crushing"
        else:
            return f"{sign}_is_completely_winning"
    
    def _get_sigmoid_data(self, centipawns: float) -> Dict:
        """
        Generate detailed sigmoid curve data for smooth visualization
        
        Args:
            centipawns: Score in centipawns
            
        Returns:
            Dictionary with curve points for smooth animation
        """
        # Generate points from current score to midpoint
        num_points = 20
        data_points = []
        
        for i in range(num_points + 1):
            alpha = i / num_points
            # Interpolate from current score to 0
            score = centipawns * (1 - alpha)
            percentage = self._score_to_percentage(score)
            data_points.append({
                "step": i,
                "score": round(score, 0),
                "white_percentage": round(percentage, 1)
            })
        
        return {
            "curve_points": data_points,
            "total_steps": num_points
        }
    
    def get_bar_visual_text(self, white_percentage: float, bar_width: int = 40) -> str:
        """
        Generate ASCII visualization of evaluation bar
        
        Args:
            white_percentage: White's percentage (0-100)
            bar_width: Width of ASCII bar
            
        Returns:
            ASCII representation of evaluation bar
        """
        white_blocks = int((white_percentage / 100) * bar_width)
        black_blocks = bar_width - white_blocks
        
        bar = "█" * white_blocks + "░" * black_blocks
        return bar
    
    def get_numeric_display(self, centipawns: float) -> str:
        """
        Get human-readable numeric display of score
        
        Examples:
        - 45 -> "+0.5"
        - -150 -> "-1.5"
        - 0 -> "0.0"
        
        Args:
            centipawns: Score in centipawns
            
        Returns:
            Formatted string representation
        """
        pawns = centipawns / 100
        
        if abs(pawns) < 0.05:
            return "0.0"
        
        if centipawns > 0:
            return f"+{pawns:.1f}"
        else:
            return f"{pawns:.1f}"
    
    def combine_scores(self, 
                      material_score: float, 
                      positional_score: float,
                      weights: Tuple[float, float] = (0.6, 0.4)) -> float:
        """
        Combine material and positional scores into overall evaluation
        
        Args:
            material_score: Material advantage in centipawns
            positional_score: Positional advantage in centipawns
            weights: Tuple of (material_weight, positional_weight)
            
        Returns:
            Combined evaluation in centipawns
        """
        total_weight = sum(weights)
        weighted_material = material_score * (weights[0] / total_weight)
        weighted_positional = positional_score * (weights[1] / total_weight)
        
        return weighted_material + weighted_positional
    
    def create_full_bar_data(self, 
                            white_score: float, 
                            black_score: float,
                            material_score: float,
                            positional_score: float) -> Dict:
        """
        Create comprehensive bar data with all components
        
        Args:
            white_score: White's total score (centipawns)
            black_score: Black's total score (centipawns)
            material_score: Material advantage (white perspective)
            positional_score: Positional advantage (white perspective)
            
        Returns:
            Complete bar data dictionary
        """
        net_score = white_score - black_score
        bar_data = self.generate_bar(white_score, black_score)
        
        return {
            **bar_data,
            "score_breakdown": {
                "total": round(net_score, 0),
                "material": round(material_score, 0),
                "positional": round(positional_score, 0)
            },
            "visual_bar": self.get_bar_visual_text(bar_data["white_percentage"]),
            "numeric_display": self.get_numeric_display(net_score),
            "explanation": self._get_explanation(net_score)
        }
    
    def _get_explanation(self, centipawns: float) -> str:
        """
        Get human-readable explanation of evaluation
        
        Args:
            centipawns: Score in centipawns
            
        Returns:
            English explanation
        """
        abs_score = abs(centipawns)
        side = "White" if centipawns >= 0 else "Black"
        
        if abs_score < 50:
            return "Position is roughly equal"
        elif abs_score < 150:
            return f"{side} is slightly better"
        elif abs_score < 300:
            return f"{side} is better (±{abs_score/100:.1f}p)"
        elif abs_score < 500:
            return f"{side} is in a winning position (±{abs_score/100:.1f}p)"
        elif abs_score < 1000:
            return f"{side} has a decisive advantage (±{abs_score/100:.1f}p)"
        else:
            return f"{side} is completely winning (±{abs_score/100:.1f}p)"


if __name__ == "__main__":
    # Test the evaluation bar generator
    generator = EvaluationBarGenerator()
    
    test_cases = [
        (0, 0, "Equal position"),
        (50, 0, "Slight white advantage"),
        (250, 0, "White winning"),
        (-300, 0, "Black winning"),
        (1500, 0, "Decisive white advantage"),
    ]
    
    print("Testing Evaluation Bar Generator\n")
    print("=" * 70)
    
    for white_cp, black_cp, description in test_cases:
        bar_data = generator.generate_bar(white_cp, black_cp)
        print(f"\n{description}")
        print(f"White: {bar_cp}%, Black: {bar_data['black_percentage']}%")
        print(f"Type: {bar_data['evaluation_type']}")
        print(f"Visual: {generator.get_bar_visual_text(bar_data['white_percentage'])}")
        print(f"Numeric: {generator.get_numeric_display(white_cp)}")
