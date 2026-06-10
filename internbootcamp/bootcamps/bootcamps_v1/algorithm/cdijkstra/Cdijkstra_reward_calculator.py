import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
from collections import defaultdict
import heapq
import random
import re




class CdijkstraRewardCalculator(BaseRewardCalculator):
    """Cdijkstra奖励计算器"""
    
    @staticmethod
    def extract_output(text):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', text, re.IGNORECASE | re.DOTALL)
        if not matches:
            return None
        # 取最后一个有效答案并标准化输出
        last_answer = matches[-1].strip()
        # 清理多余空格和换行符
        return ' '.join(last_answer.split()) if last_answer != '-1' else '-1'
    
    @classmethod
    def _verify_correction(cls, solution, case):
        # 处理无解情况
        if solution == "-1":
            return not case['has_path']
        
        # 解析路径
        try:
            path = list(map(int, solution.split()))
        except ValueError:
            return False
        
        # 验证端点
        if path[0] != 1 or path[-1] != case['n']:
            return False
        
        # 构建最小权重邻接字典
        min_weights = defaultdict(dict)
        for a, b, w in case['edges']:
            if b not in min_weights[a] or w < min_weights[a][b]:
                min_weights[a][b] = w
            if a not in min_weights[b] or w < min_weights[b][a]:
                min_weights[b][a] = w
        
        # 计算路径总权重
        total = 0
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            if v not in min_weights.get(u, {}):
                return False
            total += min_weights[u][v]
        
        # 浮点数精度处理
        return abs(total - case['expected_distance']) < 1e-9
    
    # 其他额外方法

