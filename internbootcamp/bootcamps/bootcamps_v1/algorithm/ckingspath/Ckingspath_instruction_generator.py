import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from collections import deque
from collections import defaultdict




class CkingspathInstructionGenerator(BaseInstructionGenerator):
    """Ckingspath Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Ckingspath指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_coord = params.get('max_coord', 100)  # 限制坐标范围便于测试
        self.min_segments = params.get('min_segments', 1)
        self.max_segments = params.get('max_segments', 5)
        super().__init__(**params)
    
    def case_generator(self):
        # 生成唯一坐标对
        def rand_point():
            return (random.randint(1, self.max_coord), 
                    random.randint(1, self.max_coord))
        
        start = rand_point()
        end = rand_point()
        while start == end:
            end = rand_point()

        # 生成有效路径或隔离区域
        if random.random() < 0.7:  # 70%有解案例
            path = self._generate_king_path(start, end)
            segments = self._merge_segments(path)
        else:  # 30%无解案例
            segments = self._generate_disjoint_segments(start, end)
        
        return {
            'start': start,
            'end': end,
            'segments': segments
        }
    
    @staticmethod
    def prompt_func(question_case):
        case = question_case
        # 构建输入内容
        input_lines = [
            f"{case['start'][0]} {case['start'][1]} {case['end'][0]} {case['end'][1]}",
            str(len(case['segments']))
        ]
        input_lines += [f"{r} {a} {b}" for r, a, b in case['segments']]
        
        # 正确构建多行字符串
        input_str = '\n'.join(input_lines)
        
        return (
            f"国际象棋国王导航问题\n"
            f"起点坐标：({case['start'][0]}, {case['start'][1]})\n"
            f"终点坐标：({case['end'][0]}, {case['end'][1]})\n"
            f"允许区域描述：\n{input_str}\n\n"
            f"请计算最少移动步数（国王每次可向周围8格移动），若无解返回-1。\n"
            f"答案格式：[answer]你的答案[/answer]，例如：[answer]4[/answer]"
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_king_path(self, start, end):
        """生成国王移动的合法路径"""
        path = [start]
        x, y = start
        tx, ty = end

        while (x, y) != (tx, ty):
            dx = 0 if x == tx else (1 if tx > x else -1)
            dy = 0 if y == ty else (1 if ty > y else -1)
            x += dx
            y += dy
            path.append((x, y))
        return path

    def _merge_segments(self, path):
        """合并连续列形成线段"""
        row_dict = defaultdict(list)
        for x, y in path:
            row_dict[x].append(y)

        segments = []
        for row in row_dict:
            cols = sorted(row_dict[row])
            start = cols[0]
            for i in range(1, len(cols)):
                if cols[i] > cols[i-1] + 1:
                    segments.append([row, start, cols[i-1]])
                    start = cols[i]
            segments.append([row, start, cols[-1]])
        return segments

    def _generate_disjoint_segments(self, start, end):
        """生成隔离区域确保无解"""
        segments = []
        # 单独包裹起点
        segments.append([start[0], start[1]-1, start[1]+1])
        # 单独包裹终点（不同行）
        segments.append([end[0]+2, end[1]-1, end[1]+1])
        # 添加干扰线段
        for _ in range(random.randint(1,3)):
            r = random.randint(1, self.max_coord)
            a = random.randint(1, self.max_coord//2)
            b = random.randint(a+2, self.max_coord)
            segments.append([r, a, b])
        return segments
