import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class DtshirtsdistributionRewardCalculator(BaseRewardCalculator):
    """Dtshirtsdistribution奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        solution = solution.strip().upper().split('\n')
        if not solution:
            return False
        
        # 验证NO情况
        if solution[0] == 'NO':
            try:
                # 调用参考解法验证是否确实无解
                from copy import deepcopy
                from io import StringIO
                import sys
                
                class Demand:
                    def __init__(self, parts):
                        self.x = cls.SIZE_IDX[parts[0]]
                        self.y = cls.SIZE_IDX[parts[1]] if len(parts)>1 else -1
                        self.assigned = None
                
                # 构建输入数据
                a = deepcopy(identity['available'])
                demands = [Demand(d.split(',')) for d in identity['demands']]
                
                # 处理单一需求
                valid = True
                for d in demands:
                    if d.y == -1:
                        a[d.x] -= 1
                        if a[d.x] < 0:
                            valid = False
                
                if not valid:
                    return True
                
                # 处理双需求
                for i in range(5):
                    for d in demands:
                        if d.y != -1 and d.x == i and d.assigned is None:
                            if a[i] > 0:
                                a[i] -= 1
                                d.assigned = i
                            elif a[i+1] > 0:
                                a[i+1] -= 1
                                d.assigned = i+1
                            else:
                                valid = False
                    if not valid:
                        break
                
                return not valid
            except:
                return False
        
        # 验证YES情况
        if solution[0] != 'YES' or len(solution) != identity['n']+1:
            return False
        
        # 检查格式有效性
        try:
            assigned = [cls.SIZE_IDX[s.upper()] for s in solution[1:]]
        except KeyError:
            return False
        
        # 检查库存消耗
        inventory = list(identity['available'])
        for idx in assigned:
            inventory[idx] -= 1
            if inventory[idx] < 0:
                return False
        
        # 检查需求匹配
        for i, (size_idx, demand) in enumerate(zip(assigned, identity['demands'])):
            allowed = [cls.SIZE_IDX[p] for p in demand.split(',')]
            if size_idx not in allowed:
                return False
        
        return True
    
    # 其他额外方法

