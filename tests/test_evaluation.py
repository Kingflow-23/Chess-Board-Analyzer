"""Unit tests for evaluation engine."""

import chess
from evaluation_engine import PositionEvaluator
from visualization import EvaluationBarGenerator
from output_formatter import ChessAnalysisJSONBuilder
from upload_handler import ImageUploadHandler
import json
import tempfile
from pathlib import Path


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


# ============================================================================
# EVALUATION BAR TESTS
# ============================================================================

def test_evaluation_bar_equal_position():
    """Test evaluation bar for equal position."""
    generator = EvaluationBarGenerator()
    bar_data = generator.generate_bar(0, 0)
    
    print(f"✓ test_evaluation_bar_equal_position:")
    print(f"  White: {bar_data['white_percentage']:.1f}%")
    print(f"  Black: {bar_data['black_percentage']:.1f}%")
    
    # Equal position should be ~50/50
    assert abs(bar_data['white_percentage'] - 50.0) < 2, "Equal position should be ~50%"
    assert abs(bar_data['black_percentage'] - 50.0) < 2, "Equal position should be ~50%"


def test_evaluation_bar_white_advantage():
    """Test evaluation bar with white advantage."""
    generator = EvaluationBarGenerator()
    bar_data = generator.generate_bar(150, 0)
    
    print(f"✓ test_evaluation_bar_white_advantage:")
    print(f"  Score: {bar_data['centipawn_score']:.0f}cp → {bar_data['white_percentage']:.1f}% white")
    print(f"  Type: {bar_data['evaluation_type']}")
    
    # White advantage should be > 50%
    assert bar_data['white_percentage'] > 50, "White advantage should show % > 50"
    assert 'white' in bar_data['evaluation_type'], "Should indicate white advantage"


def test_evaluation_bar_black_advantage():
    """Test evaluation bar with black advantage."""
    generator = EvaluationBarGenerator()
    bar_data = generator.generate_bar(-250, 0)
    
    print(f"✓ test_evaluation_bar_black_advantage:")
    print(f"  Score: {bar_data['centipawn_score']:.0f}cp → {bar_data['black_percentage']:.1f}% black")
    print(f"  Type: {bar_data['evaluation_type']}")
    
    # Black advantage should be > 50%
    assert bar_data['black_percentage'] > 50, "Black advantage should show % > 50"
    assert 'black' in bar_data['evaluation_type'], "Should indicate black advantage"


def test_evaluation_bar_winning_position():
    """Test evaluation bar for clearly winning position."""
    generator = EvaluationBarGenerator()
    bar_data = generator.generate_bar(750, 0)
    
    print(f"✓ test_evaluation_bar_winning_position:")
    print(f"  Score: {bar_data['centipawn_score']:.0f}cp → {bar_data['white_percentage']:.1f}% white")
    print(f"  Type: {bar_data['evaluation_type']}")
    
    # Winning position should be very high %
    assert bar_data['white_percentage'] > 95, "Winning position should be > 95%"
    assert 'crushing' in bar_data['evaluation_type'], "Should be marked as crushing"


def test_evaluation_bar_symmetry():
    """Test that positive and negative scores are symmetric."""
    generator = EvaluationBarGenerator()
    
    bar_white = generator.generate_bar(200, 0)
    bar_black = generator.generate_bar(-200, 0)
    
    print(f"✓ test_evaluation_bar_symmetry:")
    print(f"  +200cp: White {bar_white['white_percentage']:.1f}%")
    print(f"  -200cp: Black {bar_black['black_percentage']:.1f}%")
    
    # Should be approximately symmetric
    assert abs(bar_white['white_percentage'] - bar_black['black_percentage']) < 2, "Scores should be symmetric"


# ============================================================================
# JSON OUTPUT TESTS
# ============================================================================

def test_json_output_structure():
    """Test that JSON output has correct structure."""
    builder = ChessAnalysisJSONBuilder()
    
    builder.with_position(
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
        [['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
         ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
         ['', '', '', '', '', '', '', ''],
         ['', '', '', '', '', '', '', ''],
         ['', '', '', 'P', '', '', '', ''],
         ['', '', '', '', '', '', '', ''],
         ['P', 'P', 'P', '', 'P', 'P', 'P', 'P'],
         ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']],
        "test.png"
    )
    
    builder.with_evaluation({"total_score": 0.5, "best_side": "white", "material_score": 0})
    builder.with_bar({"white_percentage": 55})
    builder.with_analysis({"summary": "Test position"})
    
    json_output = builder.build()
    
    print(f"✓ test_json_output_structure:")
    
    # Check required top-level keys
    required_keys = ['status', 'metadata', 'position', 'evaluation', 'bar', 'analysis']
    for key in required_keys:
        assert key in json_output, f"JSON should contain '{key}'"
        print(f"  ✓ Contains '{key}'")
    
    # Check position structure
    assert 'fen' in json_output['position'], "Position should have FEN"
    assert 'board_matrix' in json_output['position'], "Position should have board matrix"
    
    # Check evaluation structure
    assert 'total_score' in json_output['evaluation'], "Evaluation should have total_score"
    assert 'features' in json_output['evaluation'], "Evaluation should have features"


def test_json_output_validity():
    """Test that JSON output is valid and can be serialized."""
    builder = ChessAnalysisJSONBuilder()
    
    builder.with_position(
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        [['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
         ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
         ['', '', '', '', '', '', '', ''],
         ['', '', '', '', '', '', '', ''],
         ['', '', '', '', '', '', '', ''],
         ['', '', '', '', '', '', '', ''],
         ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
         ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']],
        "start.png"
    )
    
    builder.with_evaluation({"total_score": 0})
    builder.with_bar({"white_percentage": 50})
    builder.with_analysis({"summary": "Starting position"})
    
    json_str = builder.build_json_string()
    
    print(f"✓ test_json_output_validity:")
    print(f"  JSON string size: {len(json_str)} bytes")
    
    # Should be valid JSON
    parsed = json.loads(json_str)
    assert parsed is not None, "JSON should be parseable"
    print(f"  ✓ JSON is valid and parseable")


# ============================================================================
# UPLOAD HANDLER TESTS
# ============================================================================

def test_upload_handler_format_validation():
    """Test that upload handler validates file formats."""
    handler = ImageUploadHandler()
    
    print(f"✓ test_upload_handler_format_validation:")
    print(f"  Allowed formats: {handler.ALLOWED_FORMATS}")
    
    # Check allowed formats
    assert '.png' in handler.ALLOWED_FORMATS, "Should allow PNG"
    assert '.jpg' in handler.ALLOWED_FORMATS or '.jpeg' in handler.ALLOWED_FORMATS, "Should allow JPG"
    assert '.bmp' in handler.ALLOWED_FORMATS, "Should allow BMP"


def test_upload_handler_size_constraints():
    """Test that upload handler has size constraints."""
    handler = ImageUploadHandler()
    
    print(f"✓ test_upload_handler_size_constraints:")
    print(f"  Max file size: {handler.MAX_FILE_SIZE / 1024 / 1024:.1f} MB")
    print(f"  Min dimension: {handler.MIN_DIMENSION}×{handler.MIN_DIMENSION}")
    print(f"  Max dimension: {handler.MAX_DIMENSION}×{handler.MAX_DIMENSION}")
    
    # Check constraints are reasonable
    assert handler.MAX_FILE_SIZE > 0, "Max file size should be positive"
    assert handler.MIN_DIMENSION > 0, "Min dimension should be positive"
    assert handler.MAX_DIMENSION > handler.MIN_DIMENSION, "Max dimension should be > min"


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_evaluation_to_bar_integration():
    """Test that evaluation scores properly convert to bar percentages."""
    evaluator = PositionEvaluator()
    bar_gen = EvaluationBarGenerator()
    
    # Evaluate starting position
    board = chess.Board()
    eval_result = evaluator.evaluate(board)
    
    # Generate bar
    bar_data = bar_gen.generate_bar(eval_result.total_centipawns, 0)
    
    print(f"✓ test_evaluation_to_bar_integration:")
    print(f"  Evaluation: {eval_result.total_score:+.2f}p ({eval_result.total_centipawns:+.0f}cp)")
    print(f"  Bar: {bar_data['white_percentage']:.1f}% white")
    
    # Starting position should evaluate to ~50/50
    assert 45 < bar_data['white_percentage'] < 55, "Equal position bar should be ~50%"


if __name__ == "__main__":
    print("\n" + "="*60)
    print("RUNNING CHESS ANALYZER TEST SUITE")
    print("="*60 + "\n")
    
    try:
        # Evaluation Engine Tests
        print("\n[1/3] Evaluation Engine Tests")
        print("-" * 60)
        test_starting_position_evaluation()
        test_material_imbalance()
        test_all_features_present()
        test_mobility_advantage()
        test_endgame_material()
        test_invalid_position()
        test_score_normalization()
        
        # Evaluation Bar Tests
        print("\n[2/3] Evaluation Bar Tests")
        print("-" * 60)
        test_evaluation_bar_equal_position()
        test_evaluation_bar_white_advantage()
        test_evaluation_bar_black_advantage()
        test_evaluation_bar_winning_position()
        test_evaluation_bar_symmetry()
        
        # JSON Output Tests
        print("\n[3/3] JSON Output & Upload Handler Tests")
        print("-" * 60)
        test_json_output_structure()
        test_json_output_validity()
        test_upload_handler_format_validation()
        test_upload_handler_size_constraints()
        test_evaluation_to_bar_integration()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60 + "\n")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import sys
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        import sys
        sys.exit(1)
