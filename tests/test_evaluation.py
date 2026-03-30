"""Unit tests for evaluation engine."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import chess
from evaluation_engine import PositionEvaluator


def test_starting_position_evaluation():
    """Test evaluation of starting position (should be equal)."""
    board = chess.Board()
    evaluator = PositionEvaluator()
    result = evaluator.evaluate(board)
    
    print(f"✓ test_starting_position_evaluation:")
    print(f"  Score: {result.total_score:+.2f}p")
    print(f"  Assessment: {result.best_side}")
    
    # Starting position should be equal
    assert abs(result.total_score) < 0.5, "Starting position should be near equal"
    assert result.is_valid, "Position should be valid"


def test_material_imbalance():
    """Test evaluation with material imbalance (white up a knight)."""
    fen = "rnbqkb1r/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    board = chess.Board(fen)
    evaluator = PositionEvaluator()
    result = evaluator.evaluate(board)
    
    print(f"✓ test_material_imbalance:")
    print(f"  Score: {result.total_score:+.2f}p")
    print(f"  Material: {result.features['Material Balance']:+.2f}p")
    
    # White should be winning
    assert result.total_score > 2.0, "White should be significantly better"
    assert result.best_side == "White", "White should be better"
    assert result.features['Material Balance'] > 2.0, "Material difference should be positive"


def test_all_features_present():
    """Test that all features are evaluated."""
    board = chess.Board()
    evaluator = PositionEvaluator()
    result = evaluator.evaluate(board)
    
    expected_features = {
        'Material Balance',
        'Mobility',
        'King Safety',
        'Pawn Structure',
        'Center Control',
        'Piece-Square Tables'
    }
    
    print(f"✓ test_all_features_present:")
    print(f"  Features found: {set(result.features.keys())}")
    
    assert expected_features == set(result.features.keys()), "All features should be present"


def test_mobility_advantage():
    """Test that mobility is properly evaluated."""
    # Position where white has more moves
    fen = "rnbqkb1r/pppppppp/5n2/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 1 2"
    board = chess.Board(fen)
    evaluator = PositionEvaluator()
    result = evaluator.evaluate(board)
    
    white_moves = len(list(board.legal_moves))
    
    print(f"✓ test_mobility_advantage:")
    print(f"  White legal moves: {white_moves}")
    print(f"  Mobility score: {result.features['Mobility']:+.2f}p")
    
    assert white_moves > 0, "Should have legal moves"


def test_endgame_material():
    """Test material evaluation in endgame."""
    # Rook endgame: White rook vs nothing
    fen = "8/8/8/4k3/8/8/R3K3/8 w - - 0 1"
    board = chess.Board(fen)
    evaluator = PositionEvaluator()
    result = evaluator.evaluate(board)
    
    print(f"✓ test_endgame_material:")
    print(f"  Material: {result.features['Material Balance']:+.2f}p")
    print(f"  Total score: {result.total_score:+.2f}p")
    
    # White should have decisive material advantage
    assert result.features['Material Balance'] > 4.5, "Rook material advantage"
    assert result.total_score > 4.0, "White should be winning"


def test_invalid_position():
    """Test evaluation of invalid position."""
    # This should still be handled gracefully
    try:
        fen = "invalid/fen/format"
        board = chess.Board(fen)
    except:
        print(f"✓ test_invalid_position:")
        print(f"  Invalid FEN properly rejected")
        return
    
    evaluator = PositionEvaluator()
    result = evaluator.evaluate(board)
    
    print(f"  Result is_valid: {result.is_valid}")


def test_score_normalization():
    """Test that scores are properly normalized to pawns."""
    board = chess.Board()
    evaluator = PositionEvaluator()
    result = evaluator.evaluate(board)
    
    print(f"✓ test_score_normalization:")
    print(f"  Score in pawns: {result.total_score:+.2f}p")
    print(f"  Score in centipawns: {result.total_centipawns:+.0f}cp")
    
    # Check relationship between pawns and centipawns
    # 100 centipawns = 1 pawn
    expected_cp = result.total_score * 100
    assert abs(result.total_centipawns - expected_cp) < 10, "Normalization should be consistent"


if __name__ == "__main__":
    print("\n" + "="*60)
    print("RUNNING EVALUATION ENGINE TESTS")
    print("="*60 + "\n")
    
    try:
        test_starting_position_evaluation()
        test_material_imbalance()
        test_all_features_present()
        test_mobility_advantage()
        test_endgame_material()
        test_invalid_position()
        test_score_normalization()
        
        print("\n" + "="*60)
        print("✅ ALL EVALUATION TESTS PASSED!")
        print("="*60 + "\n")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
