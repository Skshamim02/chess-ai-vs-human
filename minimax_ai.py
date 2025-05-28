import chess
import random

# Piece-square tables for heuristic evaluation
PIECE_SQUARE_TABLES = {
    'P': [
        0, 0, 0, 0, 0, 0, 0, 0,
        5, 5, 5, 5, 5, 5, 5, 5,
        1, 1, 2, 3, 3, 2, 1, 1,
        0.5, 0.5, 1, 2.5, 2.5, 1, 0.5, 0.5,
        0, 0, 0, 2, 2, 0, 0, 0,
        0.5, -0.5, -1, 0, 0, -1, -0.5, 0.5,
        0.5, 1, 1, -2, -2, 1, 1, 0.5,
        0, 0, 0, 0, 0, 0, 0, 0,
    ],
    'N': [
        -5, -4, -3, -3, -3, -3, -4, -5,
        -4, -2, 0, 0.5, 0.5, 0, -2, -4,
        -3, 0.5, 1, 1.5, 1.5, 1, 0.5, -3,
        -3, 1, 1.5, 2, 2, 1.5, 1, -3,
        -3, 0.5, 1.5, 2, 2, 1.5, 0.5, -3,
        -3, 0, 1, 1.5, 1.5, 1, 0, -3,
        -4, -2, 0, 0, 0, 0, -2, -4,
        -5, -4, -3, -3, -3, -3, -4, -5,
    ],
    # Additional tables can be added for B, R, Q, K
}

PIECE_VALUES = {
    'P': 1,
    'N': 3,
    'B': 3.3,
    'R': 5,
    'Q': 9,
    'K': 0  # King value isn't used directly
}


def evaluate_board(board):
    """Evaluate the board state."""
    if board.is_checkmate():
        return -9999 if board.turn else 9999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    evaluation = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = PIECE_VALUES.get(piece.symbol().upper(), 0)
            position_value = PIECE_SQUARE_TABLES.get(piece.symbol().upper(), [0] * 64)[square]
            evaluation += value if piece.color == chess.WHITE else -value
            evaluation += position_value if piece.color == chess.WHITE else -position_value

    # Add king safety bonus/penalty
    evaluation += king_safety(board)

    return evaluation


def king_safety(board):
    """Evaluate king safety."""
    safety_score = 0
    for square, piece in board.piece_map().items():
        if piece.symbol().upper() == 'K':
            row, col = chess.square_rank(square), chess.square_file(square)
            if piece.color == chess.WHITE and row < 2:
                safety_score += 0.5  # Bonus for white king being safe
            elif piece.color == chess.BLACK and row > 5:
                safety_score -= 0.5  # Bonus for black king being safe
    return safety_score


def order_moves(board, legal_moves):
    """Order moves to improve alpha-beta pruning."""
    def move_priority(move):
        if board.gives_check(move):
            return 3  # Prioritize checks
        if board.is_capture(move):
            return 2  # Prioritize captures
        if board.is_castling(move):
            return 1  # Prioritize castling
        return 0  # Other moves

    return sorted(legal_moves, key=move_priority, reverse=True)


def minimax(board, depth, alpha, beta, maximizing_player):
    """Minimax algorithm with alpha-beta pruning."""
    if depth == 0 or board.is_game_over():
        return evaluate_board(board), None

    best_move = None
    legal_moves = order_moves(board, list(board.legal_moves))

    if maximizing_player:
        max_eval = -float('inf')
        for move in legal_moves:
            board.push(move)
            evaluation, _ = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            if evaluation > max_eval:
                max_eval = evaluation
                best_move = move
            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break  # Beta cutoff
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in legal_moves:
            board.push(move)
            evaluation, _ = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            if evaluation < min_eval:
                min_eval = evaluation
                best_move = move
            beta = min(beta, evaluation)
            if beta <= alpha:
                break  # Alpha cutoff
        return min_eval, best_move


def get_best_move(board, difficulty):
    """Get the best move for the AI based on difficulty."""
    depth_map = {
        "Beginner": 2,
        "Intermediate": 4,
        "Expert": 6
    }
    search_depth = depth_map.get(difficulty, 4)  # Default to intermediate depth
    _, best_move = minimax(board, search_depth, -float('inf'), float('inf'), board.turn)
    return best_move if best_move else random.choice(list(board.legal_moves))
