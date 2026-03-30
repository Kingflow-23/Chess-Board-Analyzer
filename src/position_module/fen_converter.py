"""Position Reconstruction Module - Converts board matrix to FEN notation."""
import chess
import numpy as np
from typing import Optional
from dataclasses import dataclass


@dataclass
class PositionReconstructionResult:
    """Result of position reconstruction."""
    fen: str  # Full FEN string
    board_matrix: np.ndarray  # 8x8 piece matrix
    is_valid: bool  # Whether FEN is valid
    white_to_move: bool  # Current side to move (default True for static images)
    castling_rights: str  # Castling rights string (-, KQkq, etc.)
    en_passant_square: Optional[str]  # En passant target square
    halfmove_clock: int  # Halfmove clock
    fullmove_number: int  # Fullmove number


class FENConverter:
    """Converts board matrix to FEN notation."""
    
    def __init__(self):
        """Initialize FEN converter."""
        pass
    
    def board_matrix_to_fen(
        self,
        board_matrix: np.ndarray,
        white_to_move: bool = True,
        castling_rights: str = 'KQkq',
        en_passant_square: Optional[str] = None,
        halfmove_clock: int = 0,
        fullmove_number: int = 1
    ) -> PositionReconstructionResult:
        """
        Convert board matrix to FEN notation.
        
        Args:
            board_matrix: 8x8 array where [0,0] is top-left (a8), [0,7] is top-right (h8)
            white_to_move: Whether it's white's turn
            castling_rights: Castling rights string (e.g., 'KQkq', '-')
            en_passant_square: En passant square (e.g., 'e3', None)
            halfmove_clock: Halfmove clock
            fullmove_number: Fullmove number
        
        Returns:
            PositionReconstructionResult with FEN and validation
        """
        # 1. Build FEN board representation
        fen_board = self._build_fen_board_string(board_matrix)
        
        # 2. Determine side to move
        side_to_move = 'w' if white_to_move else 'b'
        
        # 3. Infer castling rights (optional - heuristic)
        inferred_castling = self._infer_castling_rights(board_matrix, castling_rights)
        
        # 4. Validate en passant square
        if en_passant_square and not self._is_valid_square(en_passant_square):
            en_passant_square = None
        
        # 5. Construct full FEN
        fen_parts = [
            fen_board,
            side_to_move,
            inferred_castling,
            en_passant_square or '-',
            str(halfmove_clock),
            str(fullmove_number)
        ]
        
        fen = ' '.join(fen_parts)
        
        # 6. Validate FEN using python-chess
        is_valid = self._validate_fen(fen)
        
        return PositionReconstructionResult(
            fen=fen,
            board_matrix=board_matrix,
            is_valid=is_valid,
            white_to_move=white_to_move,
            castling_rights=inferred_castling,
            en_passant_square=en_passant_square,
            halfmove_clock=halfmove_clock,
            fullmove_number=fullmove_number
        )
    
    def _build_fen_board_string(self, board_matrix: np.ndarray) -> str:
        """
        Convert 8x8 board matrix to FEN board string.
        
        Args:
            board_matrix: 8x8 array with piece identifiers
        
        Returns:
            FEN board string (8 ranks separated by /)
        """
        fen_ranks = []
        
        for row in range(8):
            fen_rank = []
            empty_count = 0
            
            for col in range(8):
                piece = board_matrix[row, col]
                
                if piece == 'empty' or piece == '':
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fen_rank.append(str(empty_count))
                        empty_count = 0
                    fen_rank.append(str(piece))
            
            if empty_count > 0:
                fen_rank.append(str(empty_count))
            
            fen_ranks.append(''.join(fen_rank))
        
        return '/'.join(fen_ranks)
    
    def _infer_castling_rights(self, board_matrix: np.ndarray, provided_castling: str) -> str:
        """
        Infer castling rights based on board position.
        
        Checks if kings and rooks are on starting squares.
        
        Args:
            board_matrix: 8x8 board matrix
            provided_castling: Provided castling string
        
        Returns:
            Inferred castling rights string
        """
        castling_available = []
        
        # Check white king on e1 and rooks on a1, h1
        if (board_matrix[7, 4] == 'K' and  # e1
            board_matrix[7, 0] == 'R'):  # a1
            castling_available.append('Q')
        
        if (board_matrix[7, 4] == 'K' and  # e1
            board_matrix[7, 7] == 'R'):  # h1
            castling_available.append('K')
        
        # Check black king on e8 and rooks on a8, h8
        if (board_matrix[0, 4] == 'k' and  # e8
            board_matrix[0, 0] == 'r'):  # a8
            castling_available.append('q')
        
        if (board_matrix[0, 4] == 'k' and  # e8
            board_matrix[0, 7] == 'r'):  # h8
            castling_available.append('k')
        
        castling_str = ''.join(castling_available) or '-'
        
        # If no inference possible, use provided
        if castling_str == '-':
            return provided_castling
        
        return castling_str
    
    def _is_valid_square(self, square: str) -> bool:
        """
        Validate chess square notation.
        
        Args:
            square: Square notation (e.g., 'e4')
        
        Returns:
            True if valid
        """
        if not square or len(square) != 2:
            return False
        
        file = square[0]
        rank = square[1]
        
        return file in 'abcdefgh' and rank in '12345678'
    
    def _validate_fen(self, fen: str) -> bool:
        """
        Validate FEN using python-chess.
        
        Args:
            fen: FEN string
        
        Returns:
            True if valid
        """
        try:
            board = chess.Board(fen)
            return True
        except (ValueError, chess.IllegalMoveError):
            return False
    
    def fen_to_board_matrix(self, fen: str) -> np.ndarray:
        """
        Convert FEN to board matrix (inverse operation).
        
        Args:
            fen: FEN string
        
        Returns:
            8x8 board matrix
        """
        try:
            board = chess.Board(fen)
        except:
            # Return starting position if FEN is invalid
            board = chess.Board()
        
        board_matrix = np.empty((8, 8), dtype=object)
        
        for square in chess.SQUARES:
            row = 8 - (square // 8 + 1)  # Convert to matrix coordinates
            col = square % 8
            piece = board.piece_at(square)
            
            if piece:
                board_matrix[row, col] = piece.symbol()
            else:
                board_matrix[row, col] = 'empty'
        
        return board_matrix
