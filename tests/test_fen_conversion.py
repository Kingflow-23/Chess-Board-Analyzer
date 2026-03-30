"""Unit tests for FEN conversion module."""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import chess
from position_module import FENConverter


def test_starting_position():
    """Test FEN conversion for starting position."""
    board_matrix = np.array([
        ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
        ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
        ['empty'] * 8,
        ['empty'] * 8,
        ['empty'] * 8,
        ['empty'] * 8,
        ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
        ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
    ], dtype=object)
    
    converter = FENConverter()
    result = converter.board_matrix_to_fen(board_matrix)
    
    print(f"✓ test_starting_position:")
    print(f"  Generated: {result.fen}")
    print(f"  Valid: {result.is_valid}")
    assert result.is_valid, "Starting position FEN should be valid"
    assert "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR" in result.fen


def test_empty_board():
    """Test FEN conversion for empty board."""
    board_matrix = np.full((8, 8), 'empty', dtype=object)
    
    converter = FENConverter()
    result = converter.board_matrix_to_fen(board_matrix)
    
    print(f"✓ test_empty_board:")
    print(f"  Generated: {result.fen}")
    print(f"  Valid: {result.is_valid}")
    assert "88888888/88888888/88888888/88888888/88888888/88888888/88888888/88888888" in result.fen


def test_fen_to_board_matrix():
    """Test inverse operation: FEN to board matrix."""
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    
    converter = FENConverter()
    board_matrix = converter.fen_to_board_matrix(fen)
    
    print(f"✓ test_fen_to_board_matrix:")
    print(f"  Pieces: {board_matrix[0, 0]}, {board_matrix[0, 4]}, {board_matrix[7, 4]}")
    
    assert board_matrix[0, 0] == 'r'
    assert board_matrix[0, 4] == 'k'
    assert board_matrix[7, 4] == 'K'


def test_castling_inference():
    """Test castling rights inference."""
    board_matrix = np.full((8, 8), 'empty', dtype=object)
    board_matrix[7] = ['R', 'empty', 'empty', 'empty', 'K', 'empty', 'empty', 'R']
    board_matrix[0] = ['r', 'empty', 'empty', 'empty', 'k', 'empty', 'empty', 'r']
    
    converter = FENConverter()
    result = converter.board_matrix_to_fen(board_matrix)
    
    print(f"✓ test_castling_inference:")
    print(f"  Castling rights: {result.castling_rights}")
    
    assert 'K' in result.castling_rights
    assert 'Q' in result.castling_rights
    assert 'k' in result.castling_rights
    assert 'q' in result.castling_rights


if __name__ == "__main__":
    print("\n" + "="*60)
    print("RUNNING FEN CONVERSION TESTS")
    print("="*60 + "\n")
    
    try:
        test_starting_position()
        test_empty_board()
        test_fen_to_board_matrix()
        test_castling_inference()
        
        print("\n" + "="*60)
        print("✅ ALL FEN TESTS PASSED!")
        print("="*60 + "\n")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
