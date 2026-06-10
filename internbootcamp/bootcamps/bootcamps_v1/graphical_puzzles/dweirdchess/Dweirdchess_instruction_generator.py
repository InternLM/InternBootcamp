import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class DweirdchessInstructionGenerator(BaseInstructionGenerator):
    """Dweirdchess Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Dweirdchess指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = params.get('n', 5)
        self.min_o = params.get('min_o', 1)
        self.max_o = params.get('max_o', 3)
        self.move_types = params.get('move_types', ['random', 'rook', 'knight'])
        self.current_move_type = params.get('move_type', 'random')
    
    def case_generator(self):
        n = self.n
        move_vectors = self._generate_move_vectors(n)
        o_positions = self._generate_o_positions(n)
        grid = self._generate_grid(n, o_positions, move_vectors)
        return {
            'n': n,
            'grid': [''.join(row) for row in grid]
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        grid = '\n'.join(question_case['grid'])
        return f"""You are participating in Igor's chess puzzle challenge. The chessboard is a {n}x{n} grid where:
- 'o' represents a piece.
- 'x' represents a cell attacked by at least one piece.
- '.' represents a cell not attacked by any piece.

The current board configuration is:
{grid}

Your task is to determine if there exists a valid set of move vectors for the pieces to achieve the attack pattern shown. If possible, output 'YES' followed by the move vectors matrix. The matrix should be a {2*n-1}x{2*n-1} grid with 'o' at the center and 'x' marking valid moves. If impossible, output 'NO'.

Format your answer as follows:
[answer]
YES
....x....
...x.x...
..x...x..
.x.....x.
xxxxoxxxx
.x.....x.
..x...x..
...x.x...
....x....
[/answer]
or
[answer]
NO
[/answer]

Replace the example with your solution. Ensure your answer is enclosed within [answer] and [/answer] tags.""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_move_vectors(self, n):
        if self.current_move_type == 'rook':
            vectors = []
            for dx in range(-n+1, n):
                if dx != 0:
                    vectors.append((dx, 0))
            for dy in range(-n+1, n):
                if dy != 0:
                    vectors.append((0, dy))
            return list(set(vectors))
        elif self.current_move_type == 'knight':
            return [ (dx, dy) for dx in (-2, -1, 1, 2) for dy in (-2, -1, 1, 2) if abs(dx) + abs(dy) == 3 ]
        else:
            vectors = []
            for _ in range(random.randint(3, 6)):
                dx = random.randint(-n+1, n-1)
                dy = random.randint(-n+1, n-1)
                if dx == 0 and dy == 0:
                    continue
                vectors.append((dx, dy))
            return list(set(vectors))

    def _generate_o_positions(self, n):
        count = random.randint(self.min_o, self.max_o)
        positions = set()
        while len(positions) < count:
            x = random.randint(0, n-1)
            y = random.randint(0, n-1)
            positions.add((x, y))
        return list(positions)

    def _generate_grid(self, n, o_positions, move_vectors):
        grid = [['.' for _ in range(n)] for _ in range(n)]
        o_coords = set((x, y) for x, y in o_positions)

        for x, y in o_coords:
            grid[y][x] = 'o'

        for x, y in o_coords:
            for dx, dy in move_vectors:
                tx = x + dx
                ty = y + dy
                if 0 <= tx < n and 0 <= ty < n:
                    if (tx, ty) not in o_coords:
                        grid[ty][tx] = 'x'

        return grid
