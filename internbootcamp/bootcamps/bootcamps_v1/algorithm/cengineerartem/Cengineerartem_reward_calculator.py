import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CengineerartemRewardCalculator(BaseRewardCalculator):
    """Cengineerartem奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 支持多答案块和大小写标签
        pattern = re.compile(r'\[answer\](.*?)\[/?answer\]', re.DOTALL | re.IGNORECASE)
        matches = pattern.findall(output)
        if not matches:
            return None
        
        # 处理最后一个答案块
        last_answer = matches[-1].strip()
        matrix = []
        for line in last_answer.split('\n'):
            line = line.strip()
            if line:
                try:
                    matrix.append( list(map(int, line.split())) )
                except ValueError:
                    continue
        return matrix if matrix else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 维度校验
        if len(solution) != identity['n'] or any(len(row)!=identity['m'] for row in solution):
            return False
        
        a = identity['a']
        # 值域校验
        for i in range(identity['n']):
            for j in range(identity['m']):
                if solution[i][j] not in {a[i][j], a[i][j]+1}:
                    return False
        
        # 相邻校验
        directions = [(-1,0),(1,0),(0,-1),(0,1)]
        for i in range(identity['n']):
            for j in range(identity['m']):
                for dx, dy in directions:
                    x, y = i+dx, j+dy
                    if 0 <= x < identity['n'] and 0 <= y < identity['m']:
                        if solution[i][j] == solution[x][y]:
                            return False
        return True
    
    # 其他额外方法

