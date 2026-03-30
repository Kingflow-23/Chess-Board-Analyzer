"""Feature definitions for position evaluation."""
import numpy as np
import chess
from abc import ABC, abstractmethod


class FeatureEvaluator(ABC):
    """Base class for chess position evaluation features."""
    
    @property
    @abstractmethod
    def feature_name(self) -> str:
        """Name of the feature."""
        pass
    
    @abstractmethod
    def evaluate(self, board: chess.Board) -> float:
        """
        Evaluate this feature for the given position.
        
        Args:
            board: Chess board position
        
        Returns:
            Score in centipawns (positive = white advantage)
        """
        pass


class MaterialBalance(FeatureEvaluator):
    """Evaluate material balance (standard piece values)."""
    
    PIECE_VALUES = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 0  # King value not counted
    }
    
    @property
    def feature_name(self) -> str:
        return "Material Balance"
    
    def evaluate(self, board: chess.Board) -> float:
        """Calculate material balance."""
        white_material = 0
        black_material = 0
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                value = self.PIECE_VALUES.get(piece.piece_type, 0)
                if piece.color == chess.WHITE:
                    white_material += value
                else:
                    black_material += value
        
        return white_material - black_material


class Mobility(FeatureEvaluator):
    """Evaluate piece mobility (number of legal moves)."""
    
    @property
    def feature_name(self) -> str:
        return "Mobility"
    
    def evaluate(self, board: chess.Board) -> float:
        """Calculate mobility advantage."""
        white_legal_moves = len(list(board.legal_moves))
        
        # Count black's legal moves
        board.push(chess.Move.null())
        black_legal_moves = len(list(board.legal_moves))
        board.pop()
        
        # Mobility bonus: more moves is better
        mobility_bonus = (white_legal_moves - black_legal_moves) * 10
        
        return mobility_bonus


class KingSafety(FeatureEvaluator):
    """Evaluate king safety."""
    
    @property
    def feature_name(self) -> str:
        return "King Safety"
    
    def evaluate(self, board: chess.Board) -> float:
        """Calculate king safety."""
        score = 0
        
        # White king
        white_king_square = board.king(chess.WHITE)
        if white_king_square:
            score -= self._evaluate_king(board, white_king_square, chess.WHITE)
        
        # Black king
        black_king_square = board.king(chess.BLACK)
        if black_king_square:
            score += self._evaluate_king(board, black_king_square, chess.BLACK)
        
        return score
    
    def _evaluate_king(self, board: chess.Board, king_square: int, color: bool) -> float:
        """Evaluate safety of a single king."""
        score = 0
        
        # 1. Pawn shield evaluation
        pawn_shield = self._evaluate_pawn_shield(board, king_square, color)
        score += pawn_shield
        
        # 2. Open files near king
        open_files_penalty = self._evaluate_open_files(board, king_square, color)
        score += open_files_penalty
        
        # 3. Attacked squares around king
        attacked_penalty = self._evaluate_attacked_zone(board, king_square, color)
        score += attacked_penalty
        
        return score
    
    def _evaluate_pawn_shield(self, board: chess.Board, king_square: int, color: bool) -> float:
        """Evaluate pawn shield (close pawns protect king)."""
        king_file = chess.square_file(king_square)
        king_rank = chess.square_rank(king_square)
        
        pawn_shield_score = 0
        
        # Look for pawns in front of king
        direction = 1 if color == chess.WHITE else -1
        
        for file_offset in [-1, 0, 1]:
            f = king_file + file_offset
            if 0 <= f < 8:
                # Check for pawn
                for rank_offset in range(1, 3):
                    check_rank = king_rank + direction * rank_offset
                    if 0 <= check_rank < 8:
                        square = chess.square(f, check_rank)
                        piece = board.piece_at(square)
                        if piece and piece.piece_type == chess.PAWN and piece.color == color:
                            pawn_shield_score -= 20  # Bonus for defensive pawn
        
        return pawn_shield_score
    
    def _evaluate_open_files(self, board: chess.Board, king_square: int, color: bool) -> float:
        """Penalize king on open files."""
        king_file = chess.square_file(king_square)
        
        # Check if king file is open (no pawns of own color)
        open_file_penalty = 0
        
        for rank in range(8):
            square = chess.square(king_file, rank)
            piece = board.piece_at(square)
            if piece and piece.piece_type == chess.PAWN and piece.color == color:
                return 0  # File is not open
        
        return 30  # Penalty for open file
    
    def _evaluate_attacked_zone(self, board: chess.Board, king_square: int, color: bool) -> float:
        """Penalize for opponent pieces attacking king zone."""
        attacked_penalty = 0
        opponent_color = chess.BLACK if color == chess.WHITE else chess.WHITE
        
        # Check squares around king
        king_file = chess.square_file(king_square)
        king_rank = chess.square_rank(king_square)
        
        for file_offset in range(-2, 3):
            for rank_offset in range(-2, 3):
                f = king_file + file_offset
                r = king_rank + rank_offset
                
                if 0 <= f < 8 and 0 <= r < 8:
                    square = chess.square(f, r)
                    
                    # Count attacks from opponent
                    attackers = board.attackers(opponent_color, square)
                    if attackers:
                        attacked_penalty += len(attackers) * 5
        
        return attacked_penalty


class PawnStructure(FeatureEvaluator):
    """Evaluate pawn structure."""
    
    @property
    def feature_name(self) -> str:
        return "Pawn Structure"
    
    def evaluate(self, board: chess.Board) -> float:
        """Calculate pawn structure score."""
        score = 0
        
        # Evaluate white pawns
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.piece_type == chess.PAWN and piece.color == chess.WHITE:
                score -= self._evaluate_pawn(board, square, chess.WHITE)
        
        # Evaluate black pawns
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.piece_type == chess.PAWN and piece.color == chess.BLACK:
                score += self._evaluate_pawn(board, square, chess.BLACK)
        
        return score
    
    def _evaluate_pawn(self, board: chess.Board, pawn_square: int, color: bool) -> float:
        """Evaluate a single pawn."""
        score = 0
        pawn_file = chess.square_file(pawn_square)
        pawn_rank = chess.square_rank(pawn_square)
        
        # 1. Doubled pawns penalty
        if self._has_pawn_on_file(board, pawn_file, pawn_rank, color):
            score += 20
        
        # 2. Isolated pawns penalty
        if self._is_isolated_pawn(board, pawn_file, pawn_rank, color):
            score += 15
        
        # 3. Backward pawns penalty
        if self._is_backward_pawn(board, pawn_file, pawn_rank, color):
            score += 10
        
        # 4. Passed pawns bonus
        if self._is_passed_pawn(board, pawn_square, color):
            score -= 30
        
        return score
    
    def _has_pawn_on_file(self, board: chess.Board, file: int, exclude_rank: int, color: bool) -> bool:
        """Check if there's another pawn on the same file."""
        for rank in range(8):
            if rank != exclude_rank:
                square = chess.square(file, rank)
                piece = board.piece_at(square)
                if piece and piece.piece_type == chess.PAWN and piece.color == color:
                    return True
        return False
    
    def _is_isolated_pawn(self, board: chess.Board, file: int, rank: int, color: bool) -> bool:
        """Check if pawn is isolated (no pawns on adjacent files)."""
        for adj_file in [file - 1, file + 1]:
            if 0 <= adj_file < 8:
                for adj_rank in range(8):
                    square = chess.square(adj_file, adj_rank)
                    piece = board.piece_at(square)
                    if piece and piece.piece_type == chess.PAWN and piece.color == color:
                        return False
        return True
    
    def _is_backward_pawn(self, board: chess.Board, file: int, rank: int, color: bool) -> bool:
        """Check if pawn is backward."""
        # Backward: no support pawns, can't be protected
        direction = -1 if color == chess.WHITE else 1
        
        # Check for supporting pawn
        for adj_file in [file - 1, file + 1]:
            if 0 <= adj_file < 8:
                support_rank = rank + direction
                if 0 <= support_rank < 8:
                    square = chess.square(adj_file, support_rank)
                    piece = board.piece_at(square)
                    if piece and piece.piece_type == chess.PAWN and piece.color == color:
                        return False
        
        return True
    
    def _is_passed_pawn(self, board: chess.Board, pawn_square: int, color: bool) -> bool:
        """Check if pawn is passed."""
        pawn_file = chess.square_file(pawn_square)
        pawn_rank = chess.square_rank(pawn_square)
        
        opponent_color = chess.BLACK if color == chess.WHITE else chess.WHITE
        direction = 1 if color == chess.WHITE else -1
        
        # Check if no opponent pawns can stop this pawn
        for file in [pawn_file - 1, pawn_file, pawn_file + 1]:
            if 0 <= file < 8:
                for rank in range(pawn_rank + direction, 8 if direction > 0 else -1, direction):
                    square = chess.square(file, rank)
                    piece = board.piece_at(square)
                    if piece and piece.piece_type == chess.PAWN and piece.color == opponent_color:
                        return False
        
        return True


class CenterControl(FeatureEvaluator):
    """Evaluate control of central squares."""
    
    # Central squares: d4, e4, d5, e5
    CENTER_SQUARES = [chess.D4, chess.E4, chess.D5, chess.E5]
    
    @property
    def feature_name(self) -> str:
        return "Center Control"
    
    def evaluate(self, board: chess.Board) -> float:
        """Calculate center control."""
        score = 0
        
        for square in self.CENTER_SQUARES:
            # Count attackers for each side
            white_attackers = len(board.attackers(chess.WHITE, square))
            black_attackers = len(board.attackers(chess.BLACK, square))
            
            # Difference in control
            score += (white_attackers - black_attackers) * 5
        
        return score


class PieceSquareTables(FeatureEvaluator):
    """Simple piece-square table evaluation."""
    
    @property
    def feature_name(self) -> str:
        return "Piece-Square Tables"
    
    def evaluate(self, board: chess.Board) -> float:
        """Evaluate piece-square positions."""
        score = 0
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                pst_value = self._get_pst_value(piece, square)
                if piece.color == chess.WHITE:
                    score += pst_value
                else:
                    score -= pst_value
        
        return score
    
    def _get_pst_value(self, piece: chess.Piece, square: int) -> float:
        """Get piece-square table value."""
        piece_type = piece.piece_type
        file = chess.square_file(square)
        rank = chess.square_rank(square)
        
        # Simple PST: center control bonus
        center_distance = min(
            abs(file - 3.5),
            abs(file - 4.5)
        ) + min(
            abs(rank - 3.5),
            abs(rank - 4.5)
        )
        
        base_bonus = max(0, 4 - center_distance) * 2
        
        # Piece-type specific bonuses
        if piece_type == chess.PAWN:
            return base_bonus + (rank * 3 if piece.color == chess.WHITE else (7 - rank) * 3)
        elif piece_type == chess.KNIGHT:
            return base_bonus + 5
        elif piece_type == chess.BISHOP:
            return base_bonus + 3
        elif piece_type == chess.ROOK:
            return base_bonus + 1
        elif piece_type == chess.QUEEN:
            return base_bonus + 2
        
        return 0
