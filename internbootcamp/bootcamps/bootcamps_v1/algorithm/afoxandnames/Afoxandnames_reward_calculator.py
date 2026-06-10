import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import json




class AfoxandnamesRewardCalculator(BaseRewardCalculator):
    """Afoxandnames奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        parts = output.split('[answer]')
        if len(parts) < 2:
            return None
        last_answer = parts[-1].split('[/answer]')[0].strip()
        return last_answer
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if solution == 'Impossible':
            names = identity['names']
            graph = {}
            for i in range(len(names) - 1):
                first = names[i]
                second = names[i+1]
                k = 0
                while k < min(len(first), len(second)) and first[k] == second[k]:
                    k += 1
                if k == len(first):
                    continue
                elif k == len(second):
                    return False  # Cannot be ordered
                if first[k] not in graph:
                    graph[first[k]] = []
                if second[k] not in graph[first[k]]:
                    graph[first[k]].append(second[k])
            try:
                order = cls.topological_sort(graph)
                if order == -1:
                    return True  # Impossible is correct
                else:
                    return False  # Solution is not Impossible
            except:
                return False
        else:
            order = solution
            if len(order) != 26 or len(set(order)) != 26:
                return False
            order_dict = {char: idx for idx, char in enumerate(order)}
            for i in range(len(identity['names']) - 1):
                first = identity['names'][i]
                second = identity['names'][i+1]
                if not cls.is_ordered(first, second, order_dict):
                    return False
            return True
    
    # 其他额外方法

