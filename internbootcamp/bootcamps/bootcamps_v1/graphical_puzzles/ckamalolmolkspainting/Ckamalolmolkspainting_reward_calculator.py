import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random

# === 源文件中的全局函数 ===

def solve(n, m, grid):
    a = [[1 if cell == 'X' else 0 for cell in row] for row in grid]
    original_n, original_m = n, m

    def work(a, n, m):
        found = False
        x = y = 0
        for i in range(n):
            for j in range(m):
                if a[i][j]:
                    x, y = i, j
                    found = True
                    break
            if found:
                break
        if not found:
            return n * m * 2  # 无效情况

        lenx = 1
        while x + lenx < n and a[x + lenx][y]:
            lenx += 1

        l = 0
        r = 1
        while y + r < m and a[x][y + r]:
            r += 1
        r += 1  # 初始右边界

        def all_cells(x_check, y_check, lx_check, ly_check):
            if x_check < 0 or y_check < 0 or x_check + lx_check > n or y_check + ly_check > m:
                return False
            for i in range(x_check, x_check + lx_check):
                for j in range(y_check, y_check + ly_check):
                    if not a[i][j]:
                        return False
            return True

        def chk(lx_brush, ly_brush):
            if not all_cells(x, y, lx_brush, ly_brush):
                return 2
            b = [[0] * m for _ in range(n)]
            for i in range(x, x + lx_brush):
                for j in range(y, y + ly_brush):
                    b[i][j] = 1

            current_x, current_y = x, y
            t = 0  # 移动方向标记，0右优先，1下优先
            while True:
                can_right = False
                if current_y + ly_brush < m:
                    can_right = all_cells(current_x, current_y + ly_brush, lx_brush, 1)
                can_down = False
                if current_x + lx_brush < n:
                    can_down = all_cells(current_x + lx_brush, current_y, 1, ly_brush)
                
                if not can_right and not can_down:
                    break

                moved = False
                if can_right and (t == 0 or (not can_down and t == 1)):
                    valid = True
                    for i in range(current_x):
                        if a[i][current_y + ly_brush]:
                            valid = False
                            break
                    if valid:
                        for i in range(current_x, current_x + lx_brush):
                            b[i][current_y + ly_brush] = 1
                        current_y += 1
                        moved = True
                        t = 0
                    else:
                        return 0  # 无效移动路径

                if not moved and can_down and (t == 1 or (not can_right and t == 0)):
                    valid = True
                    for j in range(current_y):
                        if a[current_x + lx_brush][j]:
                            valid = False
                            break
                    if valid:
                        for j in range(current_y, current_y + ly_brush):
                            b[current_x + lx_brush][j] = 1
                        current_x += 1
                        moved = True
                        t = 1
                    else:
                        return 0  # 无效移动路径

                if not moved:
                    break  # 无法移动

            for i in range(n):
                for j in range(m):
                    if a[i][j] != b[i][j]:
                        return 2
            return 1

        left, right = 1, r
        answer = n * m * 2
        while left <= right:
            mid = (left + right) // 2
            res = chk(lenx, mid)
            if res == 1:
                answer = lenx * mid
                right = mid - 1
            elif res == 0:  # 路径无效，需要扩大ly
                left = mid + 1
            else:  # 覆盖不全，需要扩大ly
                left = mid + 1
        return answer if answer <= n * m else n * m * 2

    res1 = work(a, n, m)
    # 转置处理列优先的情况
    a_transposed = [list(row) for row in zip(*a)]
    res2 = work(a_transposed, m, n)
    min_res = min(res1, res2)
    return min_res if min_res <= max(n, m) * max(n, m) else -1


class CkamalolmolkspaintingRewardCalculator(BaseRewardCalculator):
    """Ckamalolmolkspainting奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if matches:
            try:
                return int(matches[-1].strip())
            except:
                return None
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['answer']
    
    # 其他额外方法

