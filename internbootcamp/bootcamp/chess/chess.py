"""### 谜题描述

The chess puzzle involves strategically placing a specified number of pieces (e.g., queens, knights) on an N×N grid, adhering to movement constraints inherent to each piece type. The goal is to arrange all pieces such that no two pieces violate predefined interaction rules (e.g., mutual non-attacking positions for queens, restricted adjacency for knights). The solution must satisfy these conditions across the entire grid, regardless of its size or the number of pieces. Each piece's movement capabilities (e.g., queens attacking along rows, columns, and diagonals; knights moving in L-shaped patterns) define the constraints. The puzzle is considered solved when a valid configuration is found for the generalized parameters (any grid size and piece count).


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import random
import ast
import re

class ChessV2bootcamp(Basebootcamp):
    def __init__(self, grid_size=8, piece_type='queen', piece_count=None):
        super().__init__()
        self.grid_size = grid_size
        self.piece_type = piece_type
        
        if piece_count is None:
            if self.piece_type == 'queen':
                self.piece_count = grid_size
            else:
                self.piece_count = 1  # Default for other piece types
        else:
            self.piece_count = piece_count
        
        # Validate parameters
        if self.piece_type == 'queen' and self.piece_count != self.grid_size:
            raise ValueError("For queens, piece_count must equal grid_size")
        if self.grid_size < 4 and self.piece_type == 'queen':
            raise ValueError("Grid size must be at least 4 for queens")
    
    def case_generator(self):
        # Generate valid grid_size ensuring solvability for queens
        if self.piece_type == 'queen':
            valid_sizes = [4, 5, 6, 7, 8]
            grid_size = random.choice(valid_sizes)
            piece_count = grid_size
        else:
            grid_size = self.grid_size
            piece_count = self.piece_count
        
        return {
            'grid_size': grid_size,
            'piece_type': self.piece_type,
            'piece_count': piece_count
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        grid_size = question_case['grid_size']
        piece_type = question_case['piece_type']
        piece_count = question_case['piece_count']
        
        if piece_type == 'queen':
            rule_desc = "no two queens can share the same row, column, or diagonal"
        elif piece_type == 'knight':
            rule_desc = "no two knights can be positioned at a knight's move (L-shaped) from each other"
        else:
            rule_desc = "pieces cannot attack each other based on their movement rules"
        
        return f"""You are a chess puzzle solver. Place {piece_count} {piece_type}(s) on a {grid_size}x{grid_size} grid such that {rule_desc}.
The grid uses 1-based indexing (rows and columns range from 1 to {grid_size}).

Provide your answer as a list of coordinates in the format:
[answer]
[(row1, col1), (row2, col2), ..., (rowN, colN)]
[/answer]
Ensure all coordinates are integers between 1 and {grid_size}."""

    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        
        last_answer = matches[-1].strip()
        try:
            return ast.literal_eval(last_answer)
        except (SyntaxError, ValueError):
            return None

    @classmethod
    def _verify_correction(cls, solution, identity):
        grid_size = identity['grid_size']
        piece_type = identity['piece_type']
        piece_count = identity['piece_count']
        
        # Basic format validation
        if not isinstance(solution, list) or len(solution) != piece_count:
            return False
        
        try:
            positions = [(int(r), int(c)) for r, c in solution]
        except (TypeError, ValueError):
            return False
        
        # Boundary check
        for r, c in positions:
            if not (1 <= r <= grid_size and 1 <= c <= grid_size):
                return False
        
        # Uniqueness check
        if len(set(positions)) != len(positions):
            return False
        
        # Piece-specific attack checks
        if piece_type == 'queen':
            for i in range(len(positions)):
                r1, c1 = positions[i]
                for j in range(i+1, len(positions)):
                    r2, c2 = positions[j]
                    if r1 == r2 or c1 == c2 or abs(r1-r2) == abs(c1-c2):
                        return False
            return True
        
        if piece_type == 'knight':
            for i in range(len(positions)):
                r1, c1 = positions[i]
                for j in range(i+1, len(positions)):
                    r2, c2 = positions[j]
                    dr = abs(r1 - r2)
                    dc = abs(c1 - c2)
                    if (dr == 2 and dc == 1) or (dr == 1 and dc == 2):
                        return False
            return True
        
        return False  # Unknown piece type
