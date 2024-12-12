from copy import deepcopy
from typing import List, Dict, Optional, Tuple

class ChessEngine:
    def __init__(self):
        self.reset_game()
        
    def reset_game(self):
        self.board = self._create_initial_board()
        self.current_turn = 'white'
        self.game_status = 'active'
        self.castling_rights = {
            'white': {'kingside': True, 'queenside': True},
            'black': {'kingside': True, 'queenside': True}
        }
        self.en_passant_target = None
        
    def _create_initial_board(self) -> dict:
        board = {}
        # Setup pawns
        for i in range(8):
            board[f'{i}1'] = {'piece': 'pawn', 'color': 'white'}
            board[f'{i}6'] = {'piece': 'pawn', 'color': 'black'}
        
        # Setup other pieces
        piece_order = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
        for i, piece in enumerate(piece_order):
            board[f'{i}0'] = {'piece': piece, 'color': 'white'}
            board[f'{i}7'] = {'piece': piece, 'color': 'black'}
            
        return board
    
    def get_valid_moves(self, position: str) -> List[str]:
        if not position in self.board:
            return []
            
        piece = self.board[position]
        if piece['color'] != self.current_turn:
            return []
            
        moves = []
        x, y = int(position[0]), int(position[1])
        
        if piece['piece'] == 'pawn':
            moves.extend(self._get_pawn_moves(x, y, piece['color']))
        elif piece['piece'] == 'knight':
            moves.extend(self._get_knight_moves(x, y, piece['color']))
        elif piece['piece'] == 'bishop':
            moves.extend(self._get_bishop_moves(x, y, piece['color']))
        elif piece['piece'] == 'rook':
            moves.extend(self._get_rook_moves(x, y, piece['color']))
        elif piece['piece'] == 'queen':
            moves.extend(self._get_queen_moves(x, y, piece['color']))
        elif piece['piece'] == 'king':
            moves.extend(self._get_king_moves(x, y, piece['color']))
            
        # Filter moves that would put or leave the king in check
        valid_moves = []
        for move in moves:
            if not self._move_puts_king_in_check(position, move, piece['color']):
                valid_moves.append(move)
                
        return valid_moves
    
    def _get_pawn_moves(self, x: int, y: int, color: str) -> List[str]:
        moves = []
        direction = 1 if color == 'white' else -1
        start_rank = 1 if color == 'white' else 6
        
        # Forward move
        new_y = y + direction
        if 0 <= new_y < 8 and f'{x}{new_y}' not in self.board:
            moves.append(f'{x}{new_y}')
            # Double move from starting position
            if y == start_rank and f'{x}{y + 2*direction}' not in self.board:
                moves.append(f'{x}{y + 2*direction}')
        
        # Captures
        for dx in [-1, 1]:
            new_x = x + dx
            if 0 <= new_x < 8:
                capture_pos = f'{new_x}{new_y}'
                if capture_pos in self.board and self.board[capture_pos]['color'] != color:
                    moves.append(capture_pos)
                # En passant
                if self.en_passant_target == capture_pos:
                    moves.append(capture_pos)
        
        return moves
    
    def _get_knight_moves(self, x: int, y: int, color: str) -> List[str]:
        moves = []
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        
        for dx, dy in knight_moves:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < 8 and 0 <= new_y < 8:
                pos = f'{new_x}{new_y}'
                if pos not in self.board or self.board[pos]['color'] != color:
                    moves.append(pos)
        
        return moves
    
    def _get_bishop_moves(self, x: int, y: int, color: str) -> List[str]:
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            while 0 <= new_x < 8 and 0 <= new_y < 8:
                pos = f'{new_x}{new_y}'
                if pos not in self.board:
                    moves.append(pos)
                elif self.board[pos]['color'] != color:
                    moves.append(pos)
                    break
                else:
                    break
                new_x, new_y = new_x + dx, new_y + dy
        
        return moves
    
    def _get_rook_moves(self, x: int, y: int, color: str) -> List[str]:
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            while 0 <= new_x < 8 and 0 <= new_y < 8:
                pos = f'{new_x}{new_y}'
                if pos not in self.board:
                    moves.append(pos)
                elif self.board[pos]['color'] != color:
                    moves.append(pos)
                    break
                else:
                    break
                new_x, new_y = new_x + dx, new_y + dy
        
        return moves
    
    def _get_queen_moves(self, x: int, y: int, color: str) -> List[str]:
        return self._get_bishop_moves(x, y, color) + self._get_rook_moves(x, y, color)
    
    def _get_king_moves(self, x: int, y: int, color: str) -> List[str]:
        moves = []
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < 8 and 0 <= new_y < 8:
                pos = f'{new_x}{new_y}'
                if pos not in self.board or self.board[pos]['color'] != color:
                    moves.append(pos)
        
        # Castling
        if self.castling_rights[color]['kingside']:
            if self._can_castle_kingside(color):
                moves.append(f'6{y}')
        if self.castling_rights[color]['queenside']:
            if self._can_castle_queenside(color):
                moves.append(f'2{y}')
        
        return moves
    
    def _can_castle_kingside(self, color: str) -> bool:
        y = 0 if color == 'white' else 7
        return (f'5{y}' in self.board and
                f'7{y}' in self.board and
                all(f'{x}{y}' not in self.board for x in [6]) and
                not self._is_square_attacked(f'5{y}', color) and
                not self._is_square_attacked(f'6{y}', color))
    
    def _can_castle_queenside(self, color: str) -> bool:
        y = 0 if color == 'white' else 7
        return (f'5{y}' in self.board and
                f'0{y}' in self.board and
                all(f'{x}{y}' not in self.board for x in [1, 2, 3]) and
                not self._is_square_attacked(f'5{y}', color) and
                not self._is_square_attacked(f'3{y}', color))
    
    def _is_square_attacked(self, position: str, defending_color: str) -> bool:
        x, y = int(position[0]), int(position[1])
        attacking_color = 'black' if defending_color == 'white' else 'white'
        
        # Check for pawn attacks
        pawn_direction = -1 if attacking_color == 'white' else 1
        for dx in [-1, 1]:
            attack_x, attack_y = x + dx, y + pawn_direction
            if 0 <= attack_x < 8 and 0 <= attack_y < 8:
                pos = f'{attack_x}{attack_y}'
                if pos in self.board and self.board[pos]['piece'] == 'pawn' and self.board[pos]['color'] == attacking_color:
                    return True
        
        # Check for knight attacks
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for dx, dy in knight_moves:
            attack_x, attack_y = x + dx, y + dy
            if 0 <= attack_x < 8 and 0 <= attack_y < 8:
                pos = f'{attack_x}{attack_y}'
                if pos in self.board and self.board[pos]['piece'] == 'knight' and self.board[pos]['color'] == attacking_color:
                    return True
        
        # Check for diagonal attacks (bishop/queen)
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            attack_x, attack_y = x + dx, y + dy
            while 0 <= attack_x < 8 and 0 <= attack_y < 8:
                pos = f'{attack_x}{attack_y}'
                if pos in self.board:
                    piece = self.board[pos]
                    if piece['color'] == attacking_color and piece['piece'] in ['bishop', 'queen']:
                        return True
                    break
                attack_x, attack_y = attack_x + dx, attack_y + dy
        
        # Check for straight attacks (rook/queen)
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            attack_x, attack_y = x + dx, y + dy
            while 0 <= attack_x < 8 and 0 <= attack_y < 8:
                pos = f'{attack_x}{attack_y}'
                if pos in self.board:
                    piece = self.board[pos]
                    if piece['color'] == attacking_color and piece['piece'] in ['rook', 'queen']:
                        return True
                    break
                attack_x, attack_y = attack_x + dx, attack_y + dy
        
        # Check for king attacks
        king_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for dx, dy in king_moves:
            attack_x, attack_y = x + dx, y + dy
            if 0 <= attack_x < 8 and 0 <= attack_y < 8:
                pos = f'{attack_x}{attack_y}'
                if pos in self.board and self.board[pos]['piece'] == 'king' and self.board[pos]['color'] == attacking_color:
                    return True
        
        return False
    
    def _move_puts_king_in_check(self, from_pos: str, to_pos: str, color: str) -> bool:
        # Make a temporary move and check if the king is in check
        board_copy = deepcopy(self.board)
        self.board[to_pos] = self.board[from_pos]
        del self.board[from_pos]
        
        # Find the king's position
        king_pos = None
        for pos, piece in self.board.items():
            if piece['piece'] == 'king' and piece['color'] == color:
                king_pos = pos
                break
        
        # Check if the king is in check
        in_check = self._is_square_attacked(king_pos, color)
        
        # Restore the board
        self.board = board_copy
        return in_check
    
    def make_move(self, from_pos: str, to_pos: str) -> Dict:
        if from_pos not in self.board:
            return {'valid': False, 'message': 'No piece at source position'}
            
        piece = self.board[from_pos]
        if piece['color'] != self.current_turn:
            return {'valid': False, 'message': 'Not your turn'}
            
        valid_moves = self.get_valid_moves(from_pos)
        if to_pos not in valid_moves:
            return {'valid': False, 'message': 'Invalid move'}
            
        # Handle castling
        if piece['piece'] == 'king' and abs(int(to_pos[0]) - int(from_pos[0])) == 2:
            self._handle_castling(from_pos, to_pos)
        
        # Handle en passant capture
        if piece['piece'] == 'pawn' and to_pos == self.en_passant_target:
            capture_y = int(from_pos[1])
            self._handle_en_passant(to_pos, capture_y)
        
        # Update castling rights
        self._update_castling_rights(from_pos, to_pos)
        
        # Set en passant target
        self._update_en_passant_target(from_pos, to_pos, piece)
        
        # Make the move
        captured_piece = self.board.get(to_pos)
        self.board[to_pos] = piece
        del self.board[from_pos]
        
        # Handle pawn promotion
        if piece['piece'] == 'pawn' and (int(to_pos[1]) == 7 or int(to_pos[1]) == 0):
            self.board[to_pos]['piece'] = 'queen'
        
        # Switch turns
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'
        
        # Check game status
        self._update_game_status()
        
        return {
            'valid': True,
            'captured': captured_piece['piece'] if captured_piece else None,
            'game_status': self.game_status
        }
    
    def _handle_castling(self, from_pos: str, to_pos: str):
        y = int(from_pos[1])
        if int(to_pos[0]) == 6:  # Kingside
            self.board[f'5{y}'] = self.board[f'7{y}']
            del self.board[f'7{y}']
        else:  # Queenside
            self.board[f'3{y}'] = self.board[f'0{y}']
            del self.board[f'0{y}']
    
    def _handle_en_passant(self, to_pos: str, capture_y: int):
        capture_x = int(to_pos[0])
        del self.board[f'{capture_x}{capture_y}']
    
    def _update_castling_rights(self, from_pos: str, to_pos: str):
        # Remove castling rights when king or rook moves
        piece = self.board[from_pos]
        color = piece['color']
        
        if piece['piece'] == 'king':
            self.castling_rights[color]['kingside'] = False
            self.castling_rights[color]['queenside'] = False
        elif piece['piece'] == 'rook':
            if from_pos[0] == '0':  # Queenside rook
                self.castling_rights[color]['queenside'] = False
            elif from_pos[0] == '7':  # Kingside rook
                self.castling_rights[color]['kingside'] = False
    
    def _update_en_passant_target(self, from_pos: str, to_pos: str, piece: Dict):
        if piece['piece'] == 'pawn' and abs(int(to_pos[1]) - int(from_pos[1])) == 2:
            x = int(from_pos[0])
            y = (int(from_pos[1]) + int(to_pos[1])) // 2
            self.en_passant_target = f'{x}{y}'
        else:
            self.en_passant_target = None
    
    def _update_game_status(self):
        # Check if the current player has any valid moves
        has_moves = False
        for pos, piece in self.board.items():
            if piece['color'] == self.current_turn and self.get_valid_moves(pos):
                has_moves = True
                break
        
        if not has_moves:
            # Find the king's position
            king_pos = None
            for pos, piece in self.board.items():
                if piece['piece'] == 'king' and piece['color'] == self.current_turn:
                    king_pos = pos
                    break
            
            # If the king is in check, it's checkmate
            if self._is_square_attacked(king_pos, self.current_turn):
                self.game_status = 'checkmate'
            else:
                self.game_status = 'stalemate'
    
    def get_ai_move(self) -> Optional[Dict[str, str]]:
        if self.game_status != 'active':
            return None
            
        best_move = self._minimax(2, float('-inf'), float('inf'), True)
        return best_move['move'] if best_move else None
    
    def _minimax(self, depth: int, alpha: float, beta: float, maximizing: bool) -> Dict:
        if depth == 0 or self.game_status != 'active':
            return {'score': self._evaluate_position(), 'move': None}
        
        best_move = None
        best_score = float('-inf') if maximizing else float('inf')
        
        moves = self._get_all_valid_moves('black' if maximizing else 'white')
        for move in moves:
            # Make move
            board_copy = deepcopy(self.board)
            self.make_move(move['from'], move['to'])
            
            # Recursive evaluation
            eval_result = self._minimax(depth - 1, alpha, beta, not maximizing)
            score = eval_result['score']
            
            # Restore board
            self.board = board_copy
            
            # Update best move
            if maximizing:
                if score > best_score:
                    best_score = score
                    best_move = move
                alpha = max(alpha, best_score)
            else:
                if score < best_score:
                    best_score = score
                    best_move = move
                beta = min(beta, best_score)
            
            if beta <= alpha:
                break
        
        return {'score': best_score, 'move': best_move}
    
    def _get_all_valid_moves(self, color: str) -> List[Dict[str, str]]:
        moves = []
        for pos, piece in self.board.items():
            if piece['color'] == color:
                valid_moves = self.get_valid_moves(pos)
                moves.extend({'from': pos, 'to': move} for move in valid_moves)
        return moves
    
    def _evaluate_position(self) -> float:
        piece_values = {
            'pawn': 1,
            'knight': 3,
            'bishop': 3,
            'rook': 5,
            'queen': 9,
            'king': 0
        }
        
        score = 0
        for pos, piece in self.board.items():
            value = piece_values[piece['piece']]
            if piece['color'] == 'black':
                score += value
            else:
                score -= value
        
        return score