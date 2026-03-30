#!/usr/bin/env python3
"""
Demo Script - Tests the Chess Board Analyzer System

This script demonstrates the complete pipeline:
1. Image → Board Detection
2. CV → Piece Classification
3. Piece Matrix → FEN Conversion
4. FEN → Position Evaluation
5. Evaluation → Human-Readable Analysis

For MVP testing, we'll use predefined FEN positions and a synthetic board matrix.
In phase 2, we'll add real image input.
"""

import sys
import os
import numpy as np
import chess

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pipeline import ChessBoardAnalyzerPipeline
from position_module import FENConverter
from evaluation_engine import PositionEvaluator
from explanation_layer import GameAnalyzer


def demo_fen_to_evaluation(fen_string: str):
    """
    Demonstrate evaluation of a FEN position directly.
    
    Args:
        fen_string: FEN notation of chess position
    """
    print("\n" + "="*70)
    print("DEMO: FEN → EVALUATION PIPELINE")
    print("="*70)
    
    print(f"\nInput FEN: {fen_string}")
    
    # Create board
    try:
        board = chess.Board(fen_string)
    except Exception as e:
        print(f"Error: Invalid FEN - {e}")
        return
    
    # Evaluate
    evaluator = PositionEvaluator()
    eval_result = evaluator.evaluate(board)
    
    if not eval_result.is_valid:
        print("Position evaluation failed.")
        return
    
    # Analyze with explanations
    analyzer = GameAnalyzer()
    analysis = analyzer.analyze(board)
    
    # Print results
    print(f"\n{'='*70}")
    print(f"EVALUATION RESULT:")
    print(f"{'='*70}")
    
    print(f"\nAdvantage: {analysis.advantage_str} (in pawns)")
    print(f"Assessment: {eval_result.best_side}")
    
    print(f"\nFEATURE SCORES (in pawns):")
    for feature_name, score in eval_result.features.items():
        indicator = "↑" if score > 0 else "↓" if score < 0 else "="
        print(f"  {indicator} {feature_name}: {score:+.2f}p")
    
    print(f"\nSUMMARY:")
    print(f"  {analysis.summary}")
    
    if analysis.details:
        print(f"\nDETAILED ANALYSIS:")
        for i, detail in enumerate(analysis.details[:3], 1):
            print(f"  {i}. {detail}")
    
    if analysis.highlights:
        print(f"\nKEY POINTS:")
        for highlight in analysis.highlights:
            print(f"  • {highlight}")
    
    print()


def demo_board_matrix_to_fen():
    """
    Demonstrate conversion from board matrix to FEN.
    """
    print("\n" + "="*70)
    print("DEMO: BOARD MATRIX → FEN CONVERSION")
    print("="*70)
    
    # Create a sample starting position as board matrix
    board_matrix = np.array([
        ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
        ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
        ['empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty'],
        ['empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty'],
        ['empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty'],
        ['empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty'],
        ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
        ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
    ], dtype=object)
    
    print("\nBoard Matrix (starting position):")
    print(board_matrix)
    
    # Convert to FEN
    fen_converter = FENConverter()
    position_result = fen_converter.board_matrix_to_fen(board_matrix)
    
    print(f"\nGenerated FEN: {position_result.fen}")
    print(f"FEN Valid: {position_result.is_valid}")
    
    if position_result.is_valid:
        expected_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        print(f"Expected FEN:  {expected_fen}")
        print(f"Match: {position_result.fen == expected_fen}")


def demo_interesting_positions():
    """
    Demo various interesting chess positions.
    """
    positions = [
        {
            "name": "Scholar's Mate (Mate in 4)",
            "fen": "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 4 4",
            "description": "A common beginner tactic"
        },
        {
            "name": "Sicilian Defense",
            "fen": "rnbqkb1r/pp1ppppp/5n2/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq c6 0 3",
            "description": "After 1.e4 c5 2.Nf3"
        },
        {
            "name": "Ruy Lopez",
            "fen": "r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 1 3",
            "description": "Classical opening"
        },
        {
            "name": "Endgame: King + Rook vs King",
            "fen": "8/8/8/4k3/8/8/R3K3/8 w - - 0 1",
            "description": "Rook endgame (winning for white)"
        }
    ]
    
    print("\n" + "="*70)
    print("DEMO: ANALYZING REAL CHESS POSITIONS")
    print("="*70)
    
    for pos in positions:
        print(f"\n\n{'─'*70}")
        print(f"Position: {pos['name']}")
        print(f"Description: {pos['description']}")
        
        # Evaluate
        board = chess.Board(pos['fen'])
        evaluator = PositionEvaluator()
        eval_result = evaluator.evaluate(board)
        
        analyzer = GameAnalyzer()
        analysis = analyzer.analyze(board)
        
        print(f"FEN: {pos['fen']}")
        print(f"\nAdvantage: {analysis.advantage_str}")
        print(f"Assessment: {eval_result.best_side}")
        print(f"\nSummary: {analysis.summary}")
        
        # Show feature breakdown
        print(f"\nFeature Breakdown:")
        sorted_features = sorted(
            eval_result.features.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        for feature_name, score in sorted_features[:3]:
            print(f"  • {feature_name}: {score:+.2f}p")


def main():
    """Run all demos."""
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  CHESS BOARD ANALYZER - MVP DEMONSTRATION".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    # Demo 1: Board matrix to FEN
    demo_board_matrix_to_fen()
    
    # Demo 2: Single FEN evaluation
    demo_fen_to_evaluation("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    
    # Demo 3: Various positions
    demo_interesting_positions()
    
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  DEMONSTRATION COMPLETE".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70 + "\n")
    
    print("Next Steps:")
    print("  1. Improve piece classifier (add CNN training)")
    print("  2. Test with real chessboard images")
    print("  3. Add move recommendations (minimax)")
    print("  4. Create web UI with Streamlit")
    print("  5. Fine-tune evaluation weights using game data\n")


if __name__ == "__main__":
    main()
